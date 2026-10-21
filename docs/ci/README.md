# CI and ownership drafts

**Status:** PROPOSED; not active GitHub configuration. **Owner:** repository owner and engineering. **Last reviewed:** 21 October 2026. **Baseline:** codex/orca-cloud-foundation at 3f5e4b8.

GitHub only recognizes workflow files under repository-root .github/workflows/ and CODEOWNERS at supported root locations. These drafts intentionally remain under docs/ci/ and do not enable CI, branch protection, required checks, deployment or ownership enforcement.

Before copying anything, review action maintainers and pin each action to a reviewed full commit SHA, confirm Python/Flutter versions and required check names, and approve ownership handles. Copy github-actions-orca.yml to .github/workflows/orca.yml and CODEOWNERS.proposed to CODEOWNERS at repository root. Then inspect the Actions page and branch protection settings. Do not deploy from these jobs.
