# Generated by Django 4.1.9 on 2023-06-01 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("djangoFrontApp", "0010_rename_desc_project_descricao_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="metrics", name="project",),
        migrations.AddField(
            model_name="metrics",
            name="projeto",
            field=models.ForeignKey(
                db_column="project",
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="djangoFrontApp.project",
            ),
            preserve_default=False,
        ),
    ]
