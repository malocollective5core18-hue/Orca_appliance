# Phase 1 dependency review

Reviewed 20 October 2026. Versions are exact direct pins. This file is not a full transitive/hash
lock. Network restrictions prevented installing the test tools and running `pip-audit`; known
vulnerabilities are therefore **UNVERIFIED** pending a successful dependency audit.

| Package | Pin | Purpose | Maintainer / license | Release evidence | Known issues / status |
|---|---:|---|---|---|---|
| Django | 5.2.18 | Current LTS framework; admin, auth, ORM, migrations, checks. | Django Software Foundation; BSD-3-Clause. | PyPI release 6 Oct 2026. | Pin selected from current LTS and owner-provided Render version. `pip-audit` not run in this environment. |
| psycopg[binary] | 3.3.6 | PostgreSQL driver for Supabase. | Daniele Varrazzo / Psycopg; LGPL-3.0-only. | PyPI release 18 Sep 2026. | Binary wheel is platform-specific; confirm Render Python/platform build. Security audit not run. |
| Gunicorn | 23.0.0 | WSGI process server. | Benoit Chesneau and maintainers; MIT. | PyPI release 10 Aug 2024; this exact version appeared in the supplied Render log. | Older than current PyPI release; retained for observed deployment compatibility. Review/upgrade after CI and `pip-audit`; vulnerabilities **UNVERIFIED**. |
| WhiteNoise | 6.12.0 | Serve collected static assets on Render. | David Evans / Adam Johnson; MIT. | PyPI release 27 Feb 2026. | No known issue asserted; dependency audit not run. |
| Pillow | 13.0.0 | Verify uploaded image bytes, strip metadata, and emit WebP variants. | Pillow maintainers; MIT-CMU. | PyPI release 16 Oct 2026; CPython 3.14 wheel available. | Added in Phase 2. `pip-audit` for the updated graph remains **UNVERIFIED**. |
| pytest | 9.1.1 | Test runner. | pytest-dev maintainers; MIT. | PyPI release 19 Jun 2026. | Not installed or run here. |
| pytest-django | 4.14.0 | Django test settings/database fixtures for pytest. | pytest-django maintainers; BSD-3-Clause. | PyPI release 10 Aug 2026. | Not installed or run here. |
| pytest-cov | 7.1.0 | Coverage reporting for pytest. | pytest-cov maintainers; BSD-3-Clause. | PyPI release 21 Mar 2026. | Requires coverage >=7.10.6; exact coverage pin is included. Not run here. |
| coverage | 7.16.2 | Python coverage measurement. | Ned Batchelder and contributors; Apache-2.0. | PyPI release 27 Sep 2026. | No minimum coverage gate is set for the empty skeleton. |
| Ruff | 0.16.8 | Fast lint/format checks. | Astral Software; MIT. | PyPI release 16 Sep 2026. | Not installed or run here. |
| pre-commit | 4.7.0 | Run local Ruff hooks before commit. | Anthony Sottile; MIT. | PyPI release 12 Oct 2026. | Local-system hooks rely on `requirements-dev.txt`; hooks were not installed/run. |
| pip-audit | 2.10.1 | Audit installed/locked Python dependencies. | Trail of Bits / maintainers; Apache-2.0. | PyPI release 10 Jun 2026. | Added to dev inputs; no audit result is claimed for Phase 2. |
| pip-tools | 7.6.2 | Generate pinned hash-locked requirements files from `.in` inputs. | Jazzband maintainers; BSD-3-Clause. | PyPI release 12 Aug 2026. | Added to dev inputs; human must generate and review the lock files. |

Official package metadata:

- [Django 5.2.18 on PyPI](https://pypi.org/project/Django/5.2.18/)
- [Psycopg 3.3.6 on PyPI](https://pypi.org/project/psycopg/3.3.6/)
- [Gunicorn 23.0.0 on PyPI](https://pypi.org/project/gunicorn/23.0.0/)
- [WhiteNoise 6.12.0 on PyPI](https://pypi.org/project/whitenoise/6.12.0/)
- [pytest on PyPI](https://pypi.org/project/pytest/)
- [pytest-django on PyPI](https://pypi.org/project/pytest-django/)
- [pytest-cov on PyPI](https://pypi.org/project/pytest-cov/)
- [coverage on PyPI](https://pypi.org/project/coverage/)
- [Ruff on PyPI](https://pypi.org/project/ruff/)
- [pre-commit on PyPI](https://pypi.org/project/pre-commit/)
- [Pillow 13.0.0 on PyPI](https://pypi.org/project/Pillow/13.0.0/)
- [pip-audit 2.10.1 on PyPI](https://pypi.org/project/pip-audit/2.10.1/)
- [pip-tools 7.6.2 on PyPI](https://pypi.org/project/pip-tools/7.6.2/)

Before staging, build a complete hash-locked dependency file in networked CI, run `pip-audit`, inspect
the full dependency tree, and update this table with the tested Python and OS images. Do not treat
these direct pins as a reproducible full lock.
