# Generated by Django 4.2.15 on 2024-08-06 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0014_tip_event_start_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tip",
            name="event_start_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]