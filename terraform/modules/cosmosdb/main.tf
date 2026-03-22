# =============================================================================
# terraform/modules/cosmosdb/main.tf
#
# Azure Cosmos DB (Core API / NoSQL) for storing:
#   - pro_players   : tracked pro accounts (game_name, tag_line, puuid, region, team, role)
#   - users         : registered Telegram users and their linked LoL accounts
#   - match_history : parsed match stats per player (KDA, CS, gold, damage, vision)
#
# Why CosmosDB over SQLite on Azure:
#   - SQLite over Azure File Share works for single-instance but has SMB latency
#   - CosmosDB is serverless, globally distributed, and scales to 0 cost when idle
#   - Enables future multi-region deployment without schema migration
#
# Dev Key note:
#   - Only match/v5 data is stored (KDA, CS, gold, damage, vision, win/loss)
#   - No summoner/v4 or league/v4 data — those endpoints return 403 on Dev Key
#   - Schema is forward-compatible: ranked fields exist but remain null until prod key
# =============================================================================

resource "azurerm_cosmosdb_account" "main" {
  name                = "cosmos-lolnotifier-${var.environment}-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"  # Core (NoSQL) API

  # Consistency: Session is the right balance for a single-bot workload
  consistency_policy {
    consistency_level = "Session"
  }

  # Single-region for dev/prod (add failover_priority = 1 region for HA)
  geo_location {
    location          = "northeurope"
    failover_priority = 0
  }

  # Security hardening
  is_virtual_network_filter_enabled = false  # Set true when VNet integration is added
  public_network_access_enabled     = true   # Set false when using Private Endpoint
  local_authentication_disabled     = false  # Keep enabled — managed identity auth used in app

  # Serverless capacity mode — pay only for RU consumed, ideal for low-traffic bots
  capabilities {
    name = "EnableServerless"
  }

  tags = var.tags
}

# ── Database ──────────────────────────────────────────────────────────────────

resource "azurerm_cosmosdb_sql_database" "lolnotifier" {
  name                = "lolnotifier"
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.main.name
  # No throughput set — inherited from serverless account
}

# ── Containers (collections) ──────────────────────────────────────────────────

# Users: partition key = /user_id (Telegram user ID)
resource "azurerm_cosmosdb_sql_container" "users" {
  name                = "users"
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.lolnotifier.name
  partition_key_paths = ["/user_id"]

  indexing_policy {
    indexing_mode = "consistent"
    included_path { path = "/*" }
    excluded_path { path = "/match_history/*" }  # Large nested arrays excluded
  }
}

# Pro players: partition key = /region (enables efficient region-scoped queries)
resource "azurerm_cosmosdb_sql_container" "pro_players" {
  name                = "pro_players"
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.lolnotifier.name
  partition_key_paths = ["/region"]

  indexing_policy {
    indexing_mode = "consistent"
    included_path { path = "/*" }
  }
}

# Match history: partition key = /puuid (all matches for a player in one partition)
# Dev Key note: only match/v5 fields stored — no ranked/summoner data
resource "azurerm_cosmosdb_sql_container" "match_history" {
  name                = "match_history"
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.lolnotifier.name
  partition_key_paths = ["/puuid"]

  # TTL: auto-expire match records after 90 days to control storage costs
  default_ttl = 7776000  # 90 days in seconds

  indexing_policy {
    indexing_mode = "consistent"
    included_path { path = "/*" }
    # Exclude large string fields from index to reduce RU cost
    excluded_path { path = "/raw_payload/*" }
  }
}
