# Generated by Django 4.2.15 on 2024-08-06 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0013_remove_tip_contact_info_remove_tip_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tip",
            name="event_start_date",
            field=models.DateField(null=True, blank=True),  # Allow null and blank values
            preserve_default=False,
        ),
    ]
