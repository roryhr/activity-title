# Generated by Django 5.0.8 on 2024-10-10 17:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("titles", "0008_customuser"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CustomUser",
        ),
    ]
