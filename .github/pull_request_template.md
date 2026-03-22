## Summary

<!-- What does this PR do? Why is it needed? -->

## Changes

- [ ] Terraform module(s) updated
- [ ] GitHub Actions workflow(s) updated
- [ ] Application code updated
- [ ] Documentation updated
- [ ] Tests added or updated

## Module Versions Updated

| Module | Previous | New |
|---|---|---|
| <!-- e.g. function_app --> | <!-- v1.0.0 --> | <!-- v1.1.0 --> |

---

## 🤖 Automated CI Summary

> _This section is updated automatically by the CI bot on every push to this PR._
> _Do not edit manually._

<!-- CI_REPORT_PLACEHOLDER -->

---

## Security & Dev Key Compliance

- [ ] No secrets committed (no tokens, keys, connection strings in code)
- [ ] All secrets use Key Vault references or `os.getenv()`
- [ ] Only Dev Key endpoints used: `account/v1`, `match/v5`
- [ ] No `summoner/v4`, `league/v4`, `spectator/v5` calls added
- [ ] Logs contain no PII (no PUUIDs, tokens, chat IDs in log output)
- [ ] `poll_interval_seconds >= 60` maintained
- [ ] `RATE_LIMIT_DELAY` not reduced below `0.06`

## Terraform Safety

- [ ] `terraform plan` output reviewed — no unexpected destroys
- [ ] No `lifecycle { prevent_destroy }` removed
- [ ] No `ignore_changes` removed from secret values
- [ ] Remote state backend unchanged

## Reviewer Notes

<!-- Anything the reviewer should pay special attention to -->
