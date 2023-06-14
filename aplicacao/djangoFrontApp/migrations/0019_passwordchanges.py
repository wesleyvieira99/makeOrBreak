# Generated by Django 4.1.9 on 2023-06-12 14:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("djangoFrontApp", "0018_rename_metric_id_prediction_metric"),
    ]

    operations = [
        migrations.CreateModel(
            name="PasswordChanges",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_pwd",
                    models.CharField(db_column="last_pwd", default="", max_length=15),
                ),
                (
                    "new_pwd",
                    models.CharField(db_column="new_pwd", default="", max_length=15),
                ),
                ("date", models.DateField(db_column="date")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
