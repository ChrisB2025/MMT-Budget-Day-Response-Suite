# Generated manually for making email optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_rename_users_email_idx_users_email_4b85f2_idx_and_more"),
    ]

    operations = [
        # Remove email index since email is no longer required for authentication
        migrations.RemoveIndex(
            model_name="user",
            name="users_email_4b85f2_idx",
        ),
        # Make email field nullable and optional
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, null=True, max_length=254, verbose_name="email address"),
        ),
    ]
