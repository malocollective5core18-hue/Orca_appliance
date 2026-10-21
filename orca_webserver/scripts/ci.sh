#!/usr/bin/env bash
set -euo pipefail

# Run from orca_webserver/ after: python -m pip install -r requirements-dev.txt
export DEBUG=false
ruff check .
ruff format --check --exclude 'apps/*/migrations/*.py' .
python manage.py makemigrations --check --dry-run --settings=config.settings.test
python manage.py test --settings=config.settings.test

# Use fake settings only. This check validates deployment configuration without opening a DB socket.
DJANGO_SETTINGS_MODULE=config.settings.production \
DJANGO_SECRET_KEY='CI_TEST_VALUE_NOT_A_SECRET_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
DATABASE_URL='postgresql://orca:fake@db.example.invalid:5432/orca?sslmode=require' \
DATABASE_CONNECTION_MODE=session \
ALLOWED_HOSTS=orca.example.invalid \
CSRF_TRUSTED_ORIGINS=https://orca.example.invalid \
PAYMENTS_LIVE_ENABLED=false \
ALLOW_DEMO_BACKENDS=true \
SMS_BACKEND=console \
python manage.py check --deploy

python -m pytest --cov=apps --cov-report=term-missing
