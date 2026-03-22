## Summary

<!-- What does this PR do? Why is it needed? -->

## Changes

<!-- List files/modules changed and what was updated -->

- [ ] Terraform module(s) updated
- [ ] GitHub Actions workflow(s) updated
- [ ] Application code updated
- [ ] Documentation updated
- [ ] Tests added or updated

## Module Versions Updated

| Module | Previous | New |
|---|---|---|
| <!-- e.g. function_app --> | <!-- e.g. 1.0.0 --> | <!-- e.g. 1.1.0 --> |

## Tests Performed

- [ ] `terraform fmt -check` passed
- [ ] `terraform validate` passed
- [ ] `python -m pytest tests/ -v` — all unit tests pass
- [ ] Functional tests run manually (if applicable)

## Checkov Scan Results

<!-- Paste summary from CI or run locally: checkov -d terraform/ --framework terraform -->

```
Passed checks: X
Failed checks: Y (list any new failures below)
```

**New failures introduced:** <!-- none / list with justification -->

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
