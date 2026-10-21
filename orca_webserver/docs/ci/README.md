# Human-installed CI drafts

These are drafts inside the approved `orca_webserver/` write boundary. GitHub does not execute
workflow files from this nested folder, and this directory is not a CODEOWNERS location. A repository
owner must review and copy the workflow to root `.github/workflows/` and `CODEOWNERS.proposed` to an
accepted root location. **CI and code ownership are not active until that human action is complete.**

Before enabling the workflow, generate and commit the complete hashed locks from this directory:

```sh
python -m pip install pip-tools==7.6.2
pip-compile --generate-hashes --output-file=requirements.lock requirements.in
pip-compile --generate-hashes --output-file=requirements-dev.lock requirements-dev.in
```

Review the resulting package changes, then install with `pip install --require-hashes -r requirements-dev.lock`.
Run `pip-audit -r requirements.lock`. Do not commit machine-specific or unreviewed generated locks.

The CI workflow draft uses a disposable PostgreSQL service and synthetic values only. It never contacts
ClickPesa, SMS vendors, Supabase, object storage, Render, or device brokers.
