# Generated by Django 4.1.9 on 2023-06-12 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("djangoFrontApp", "0019_passwordchanges"),
    ]

    operations = [
        migrations.RemoveField(model_name="passwordchanges", name="last_pwd",),
    ]
