# ORCA account and language journey

## Language

- The public `index.html` page provides a working English/Kiswahili selector in the desktop header and mobile sidebar.
- The account pages use the same `orca-language` browser preference and provide a language selector at the top.
- Language selection is stored only in the current browser's `localStorage`; the server does not infer language from customer identity.

## Signup, login, and routing

| Route | Access | Result |
|---|---|---|
| `/accounts/signup/` | Public | Creates a `customer` account with full name, email, phone number, and password; logs the customer in and redirects to `/accounts/dashboard/`. |
| `/accounts/login/` | Public | Email/password login. Safe same-host `next` redirects are allowed. Otherwise redirects to `/accounts/dashboard/`. |
| `/accounts/dashboard/` | Authenticated | Shows a responsive customer account for customers, or a staff workspace for non-customer roles. |
| `/accounts/dashboard/register-user/` | Superuser or administrator | A superuser may create any supported role. An administrator may create only `customer_service`; submitted role choices are checked server-side. |
| `/accounts/dashboard/operations/` | Authenticated staff | Embeds the supplied interactive ORCA dashboard demo, including its Overview, Devices, Payments, Alerts, Partners, and Audit navigation. Its values are sample data pending later integration. |
| `/accounts/logout/` | Authenticated, POST + CSRF | Ends the session and returns to the public landing page. |
| `/admin/` | Superuser only | Django admin. Other authenticated staff receive 403. |

A customer-service user cannot create system accounts. The dashboard includes a role-aware navigation bar: administrators see Overview and Users; customer-service users see Overview only; only superusers see the Django administration link. Direct `/admin/` access for other authenticated users is denied by middleware. Public signup always assigns `customer`; the request cannot select a staff role.

## Data and integration boundary

`DATABASE_URL` is parsed by `config/settings/base.py`; production settings require SSL and `DATABASE_CONNECTION_MODE=session`. A read-only `SELECT 1` connection check against the configured URL succeeded on 22 October 2026. It did not read or alter customer data and did not validate migrations or application CRUD against Supabase.

The customer dashboard displays the account identity saved by Django. The Operations dashboard is available only to authenticated staff and intentionally shows the current standalone demo with sample data until real data integration is implemented. Finance applications, appliance assignments, repayment schedules, payments, and native mobile authentication are not connected yet. The separate `orca-dashboard-demo-1.html` continues to show generated sample data and is not part of authenticated staff operations.

## Production migration

Apply the accounts schema migration (`accounts.0002_user_name_and_staff_roles`) through the normal reviewed deployment migration step before serving signup or role management. Keep production `DATABASE_URL` in Render's environment; never commit it or use it for test runs.

## Security limits

- Staff registration requires an authenticated superuser or administrator and CSRF protection.
- The server limits administrator role creation even if a forged form submits a different role.
- Passwords use Django hashing and configured validators; passwords are never displayed after submission.
- Email verification, password reset, MFA, invitation delivery, staff onboarding audit events, and native-app tokens are not implemented in this phase.
