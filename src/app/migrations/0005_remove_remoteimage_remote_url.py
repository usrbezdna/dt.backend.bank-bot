# Generated by Django 4.2.1 on 2023-05-17 10:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_remoteimage_remote_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="remoteimage",
            name="remote_url",
        ),
    ]