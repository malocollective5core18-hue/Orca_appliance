"""Guard cross-table partner ownership and audit immutability on PostgreSQL and SQLite."""

from django.db import migrations


CREATE_FUNCTION = r"""
CREATE OR REPLACE FUNCTION domain_check_partner_scope() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF TG_TABLE_NAME = 'domain_agreement' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_customer WHERE id = NEW.customer_id AND partner_id = NEW.partner_id)
           OR NOT EXISTS (SELECT 1 FROM domain_product WHERE id = NEW.product_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Agreement references another partner' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_installment' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_agreement WHERE id = NEW.agreement_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Installment references another partner' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_device' AND NEW.agreement_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM domain_agreement WHERE id = NEW.agreement_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Device references another partner agreement' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_pairingcode' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_device WHERE id = NEW.device_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Pairing code references another partner' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_payment' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_agreement WHERE id = NEW.agreement_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Payment references another partner agreement' USING ERRCODE = '23514';
        END IF;
        IF NEW.installment_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM domain_installment
            WHERE id = NEW.installment_id AND partner_id = NEW.partner_id AND agreement_id = NEW.agreement_id
        ) THEN
            RAISE EXCEPTION 'Payment references another partner installment' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_paymentattempt' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_payment WHERE id = NEW.payment_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Payment attempt references another partner' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_devicestatushistory' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_device WHERE id = NEW.device_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Device history references another partner' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_devicecommand' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_device WHERE id = NEW.device_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Device command references another partner' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_notification' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_customer WHERE id = NEW.customer_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Notification references another partner' USING ERRCODE = '23514';
        END IF;
    ELSIF TG_TABLE_NAME = 'domain_imageasset' THEN
        IF NOT EXISTS (SELECT 1 FROM domain_product WHERE id = NEW.product_id AND partner_id = NEW.partner_id) THEN
            RAISE EXCEPTION 'Image references another partner' USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
"""

AUDIT_GUARD_FUNCTION = r"""
CREATE OR REPLACE FUNCTION domain_reject_audit_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'Audit events are append-only' USING ERRCODE = '55000';
    RETURN OLD;
END;
$$;
"""

TABLES = (
    "domain_agreement",
    "domain_installment",
    "domain_device",
    "domain_pairingcode",
    "domain_payment",
    "domain_paymentattempt",
    "domain_devicestatushistory",
    "domain_devicecommand",
    "domain_notification",
    "domain_imageasset",
)

SQLITE_SCOPE_PREDICATES = {
    "domain_agreement": (
        "NOT EXISTS (SELECT 1 FROM domain_customer WHERE id=NEW.customer_id AND partner_id=NEW.partner_id) "
        "OR NOT EXISTS (SELECT 1 FROM domain_product WHERE id=NEW.product_id AND partner_id=NEW.partner_id)"
    ),
    "domain_installment": "NOT EXISTS (SELECT 1 FROM domain_agreement WHERE id=NEW.agreement_id AND partner_id=NEW.partner_id)",
    "domain_device": "NEW.agreement_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM domain_agreement WHERE id=NEW.agreement_id AND partner_id=NEW.partner_id)",
    "domain_pairingcode": "NOT EXISTS (SELECT 1 FROM domain_device WHERE id=NEW.device_id AND partner_id=NEW.partner_id)",
    "domain_payment": (
        "NOT EXISTS (SELECT 1 FROM domain_agreement WHERE id=NEW.agreement_id AND partner_id=NEW.partner_id) "
        "OR (NEW.installment_id IS NOT NULL AND NOT EXISTS "
        "(SELECT 1 FROM domain_installment WHERE id=NEW.installment_id AND partner_id=NEW.partner_id AND agreement_id=NEW.agreement_id))"
    ),
    "domain_paymentattempt": "NOT EXISTS (SELECT 1 FROM domain_payment WHERE id=NEW.payment_id AND partner_id=NEW.partner_id)",
    "domain_devicestatushistory": "NOT EXISTS (SELECT 1 FROM domain_device WHERE id=NEW.device_id AND partner_id=NEW.partner_id)",
    "domain_devicecommand": "NOT EXISTS (SELECT 1 FROM domain_device WHERE id=NEW.device_id AND partner_id=NEW.partner_id)",
    "domain_notification": "NOT EXISTS (SELECT 1 FROM domain_customer WHERE id=NEW.customer_id AND partner_id=NEW.partner_id)",
    "domain_imageasset": "NOT EXISTS (SELECT 1 FROM domain_product WHERE id=NEW.product_id AND partner_id=NEW.partner_id)",
}


def install_partner_scope_triggers(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as cursor:
        if vendor == "sqlite":
            cursor.execute(
                "CREATE TRIGGER domain_audit_no_update BEFORE UPDATE ON domain_auditevent "
                "BEGIN SELECT RAISE(ABORT, 'Audit events are append-only'); END"
            )
            cursor.execute(
                "CREATE TRIGGER domain_audit_no_delete BEFORE DELETE ON domain_auditevent "
                "BEGIN SELECT RAISE(ABORT, 'Audit events are append-only'); END"
            )
            for table, predicate in SQLITE_SCOPE_PREDICATES.items():
                for event in ("INSERT", "UPDATE"):
                    cursor.execute(
                        f"CREATE TRIGGER {table}_partner_scope_{event.lower()} "
                        f"BEFORE {event} ON {table} WHEN ({predicate}) "
                        "BEGIN SELECT RAISE(ABORT, 'Cross-partner relationship rejected'); END"
                    )
            return
        if vendor != "postgresql":
            return
        cursor.execute(AUDIT_GUARD_FUNCTION)
        cursor.execute(
            "CREATE TRIGGER domain_audit_no_mutation BEFORE UPDATE OR DELETE ON domain_auditevent "
            "FOR EACH ROW EXECUTE FUNCTION domain_reject_audit_mutation()"
        )
        cursor.execute(CREATE_FUNCTION)
        for table in TABLES:
            cursor.execute(
                f"CREATE TRIGGER {table}_partner_scope "
                f"BEFORE INSERT OR UPDATE ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION domain_check_partner_scope()"
            )


def remove_partner_scope_triggers(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as cursor:
        if vendor == "sqlite":
            cursor.execute("DROP TRIGGER IF EXISTS domain_audit_no_update")
            cursor.execute("DROP TRIGGER IF EXISTS domain_audit_no_delete")
            for table in SQLITE_SCOPE_PREDICATES:
                for event in ("insert", "update"):
                    cursor.execute(f"DROP TRIGGER IF EXISTS {table}_partner_scope_{event}")
            return
        if vendor != "postgresql":
            return
        for table in TABLES:
            cursor.execute(f"DROP TRIGGER IF EXISTS {table}_partner_scope ON {table}")
        cursor.execute("DROP FUNCTION IF EXISTS domain_check_partner_scope()")
        cursor.execute("DROP TRIGGER IF EXISTS domain_audit_no_mutation ON domain_auditevent")
        cursor.execute("DROP FUNCTION IF EXISTS domain_reject_audit_mutation()")


class Migration(migrations.Migration):
    dependencies = [("domain", "0001_initial")]

    operations = [migrations.RunPython(install_partner_scope_triggers, remove_partner_scope_triggers)]
