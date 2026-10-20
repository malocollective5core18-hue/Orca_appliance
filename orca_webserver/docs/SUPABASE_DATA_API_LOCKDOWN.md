# Supabase Data API lockdown plan — not applied

**Status:** documentation only. No Supabase project was opened or modified.

## Intended boundary

Mobile, TV, and browser clients call ORCA Cloud only. They never receive a Supabase URL, anon key,
service-role key, or database credential. Django connects to Postgres using its server-only
`DATABASE_URL`. The Supabase Data API is not an ORCA client backend.

## Human dashboard procedure before staging

1. Open the staging Supabase project only after the owner confirms its project identity.
2. In API settings, disable the Data API if that control is available for the selected project. If it
   must remain enabled for another approved use, remove ORCA's application schema from exposed
   schemas and deny `anon` and `authenticated` access to ORCA tables/schema.
3. Create a dedicated application database role with only the privileges Django needs. Do not use a
   Supabase client key or service-role API key in Django or any client app.
4. Keep future domain tables in the agreed schema and enable RLS before granting any Data API role.
   Add no permissive policy by default. A table with RLS enabled and no matching policy should deny
   Data API reads/writes.
5. Apply the same checks after migrations because Django creates new tables and grants may differ.
6. Review the API schema-exposure configuration and role grants in the dashboard. Record a redacted
   screenshot or settings export in the owner's secure release record, not in this repository.
7. Validate from an isolated test client that an unauthenticated Data API request cannot read or
   mutate a synthetic ORCA row. Do not test against production customer rows.

## Verify connection mode separately

Copy the exact Supabase connection string from the selected project's Connect panel. Render should
use the shared session pooler for IPv4 compatibility unless direct connectivity is verified for the
service plan. Require `sslmode=require` or stronger. Keep the session pooler (normally port 5432) for
Django workers and migrations. Never use transaction pooler port 6543. No Render-to-Supabase
connection test has been run; actual host, mode, SSL validation, DB role and capacity are
**UNVERIFIED**.

## Phase 1 code guard

`config.settings.production` requires `DATABASE_CONNECTION_MODE=session`, requires PostgreSQL SSL,
and rejects port 6543. This is a configuration guard, not proof that the supplied hostname really is
Supabase's session pooler. Verify it manually before entering the secret.
