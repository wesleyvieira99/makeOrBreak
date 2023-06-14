# Generated by Django 4.1.9 on 2023-05-31 23:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("djangoFrontApp", "0007_alter_metrics_project_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="metrics",
            name="project_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="djangoFrontApp.project"
            ),
        ),
    ]