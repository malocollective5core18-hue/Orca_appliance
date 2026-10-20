# CI and code ownership boundary

**Decision:** owner chose to keep this implementation strictly inside `orca_webserver/`.

GitHub Actions discovers workflow YAML only in the repository-root `.github/workflows/` directory.
GitHub CODEOWNERS is recognized at the repository root, `.github/CODEOWNERS`, or `docs/CODEOWNERS`;
it is not recognized from `orca_webserver/CODEOWNERS`. A nested workflow or nested CODEOWNERS would
look like a safeguard without providing the promised behavior, so neither is created.

## Phase 1 local/CI command bundle

From `orca_webserver/`, install `requirements-dev.txt` and run:

```sh
./scripts/ci.sh
```

That script runs Ruff lint and format checks, migration drift check, Django tests, Django's
deployment check with fake settings, and pytest with coverage. It never calls ClickPesa or Supabase.

## Owner action before GitHub CI is available

After approving a root-level write, add a workflow under `.github/workflows/` with a path filter for
`orca_webserver/**`, `orca_mobile/**`, and `orca_TVapp/**` as separate jobs. For the server job, use
Python 3.14.8, install `orca_webserver/requirements-dev.txt`, run the equivalent of `scripts/ci.sh`,
and attach an isolated PostgreSQL service if PostgreSQL integration tests are introduced. Keep mobile
and TV jobs independent. Add CODEOWNERS entries from the repository root for each owned directory.

**Status:** local script exists; actual GitHub Actions, protected branch checks, and enforced code
ownership are **NOT IMPLEMENTED** due the approved scope boundary.
