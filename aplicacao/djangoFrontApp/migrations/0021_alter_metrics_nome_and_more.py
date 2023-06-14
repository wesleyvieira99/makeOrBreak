# Generated by Django 4.1.9 on 2023-06-14 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangoFrontApp", "0020_remove_passwordchanges_last_pwd"),
    ]

    operations = [
        migrations.AlterField(
            model_name="metrics",
            name="nome",
            field=models.CharField(db_column="name", max_length=100),
        ),
        migrations.AlterField(
            model_name="metricsvalues",
            name="cadastrado_por",
            field=models.CharField(db_column="add_by", default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="metricsvalues",
            name="decisao",
            field=models.IntegerField(db_column="decision"),
        ),
        migrations.AlterField(
            model_name="metricsvalues",
            name="tempo",
            field=models.IntegerField(db_column="time"),
        ),
        migrations.AlterField(
            model_name="metricsvalues",
            name="valor",
            field=models.IntegerField(db_column="value"),
        ),
    ]
