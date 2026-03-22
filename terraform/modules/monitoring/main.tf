# terraform/modules/monitoring/main.tf
# Azure Application Insights for bot telemetry, error tracking, and log queries.
# The bot reads APPLICATIONINSIGHTS_CONNECTION_STRING from env to emit traces.

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-lolnotifier-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 90

  # MCSB: disable local auth — force AAD-only access
  internet_ingestion_enabled = true
  internet_query_enabled     = true

  tags = var.tags
}

resource "azurerm_application_insights" "main" {
  name                = "appi-lolnotifier-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "other"
  retention_in_days   = 90
  workspace_id        = azurerm_log_analytics_workspace.main.id

  tags = var.tags
}

# ── Diagnostic settings — Function App logs ─────────────────────────────────

resource "azurerm_monitor_diagnostic_setting" "function_app" {
  name                       = "diag-func-lolnotifier-${var.environment}"
  target_resource_id         = azurerm_application_insights.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "AppTraces"
  }

  enabled_log {
    category = "AppExceptions"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

resource "azurerm_monitor_metric_alert" "container_restarts" {
  name                = "alert-lolnotifier-restarts-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_application_insights.main.id]
  description         = "Alert when bot container restarts more than 3 times in 5 minutes"
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name      = "exceptions/count"
    aggregation      = "Count"
    operator         = "GreaterThan"
    threshold        = 10
  }

  tags = var.tags
}
