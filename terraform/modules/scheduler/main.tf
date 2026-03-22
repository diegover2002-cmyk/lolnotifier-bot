# =============================================================================
# terraform/modules/scheduler/main.tf
#
# Polling scheduler for lolnotifier-bot.
#
# Implementation: Azure Logic App (Consumption) with a Recurrence trigger.
# The Logic App calls the Function App's /api/poll HTTP endpoint on schedule.
#
# Why Logic App instead of Function App Timer Trigger:
#   - Timer triggers inside Function App require the app to be always-warm
#   - On Consumption plan (Y1), cold starts can delay timer triggers by minutes
#   - Logic App Recurrence is a managed scheduler — guaranteed firing, no cold start
#   - Logic App is free for the first 4000 actions/month (well within bot usage)
#
# Alternative: If using Premium plan (EP1), use Function App Timer Trigger directly
# and delete this module — set POLL_CRON in function_app app_settings instead.
#
# Dev Key compliance:
#   - Default schedule: every 5 minutes (matches POLL_INTERVAL=300)
#   - Riot Dev Key limit: 100 req/2min — 28 pros × 2 req = 56 req per cycle, safe
# =============================================================================

resource "azurerm_logic_app_workflow" "scheduler" {
  name                = "logic-lolnotifier-scheduler-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# ── Recurrence trigger ────────────────────────────────────────────────────────

resource "azurerm_logic_app_trigger_recurrence" "poll_trigger" {
  name         = "poll-every-5-minutes"
  logic_app_id = azurerm_logic_app_workflow.scheduler.id
  frequency    = "Minute"
  interval     = var.poll_interval_minutes  # default: 5
}

# ── HTTP action — calls the Function App polling endpoint ─────────────────────

resource "azurerm_logic_app_action_http" "call_poll" {
  name         = "call-poll-function"
  logic_app_id = azurerm_logic_app_workflow.scheduler.id
  method       = "POST"
  uri          = "https://${var.function_app_hostname}/api/poll"

  headers = {
    "Content-Type" = "application/json"
    # Function key auth — stored as Logic App parameter, not hardcoded
    "x-functions-key" = "@parameters('functionKey')"
  }

  body = jsonencode({
    source    = "scheduler"
    timestamp = "@{utcNow()}"
  })

  run_after {}
}
