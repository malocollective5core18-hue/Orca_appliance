from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="user",
            name="full_name",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("customer", "Customer"),
                    ("support", "Support"),
                    ("finance", "Finance"),
                    ("admin", "Administrator"),
                    ("customer_service", "Customer service"),
                    ("superuser", "Superuser"),
                    ("partner_viewer", "Partner viewer"),
                ],
                default="customer",
                max_length=32,
            ),
        ),
    ]
