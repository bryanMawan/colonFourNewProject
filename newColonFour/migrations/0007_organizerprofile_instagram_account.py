# Generated by Django 4.2.8 on 2024-07-09 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0006_remove_event_info_pics_carousel_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizerprofile",
            name="instagram_account",
            field=models.URLField(blank=True, null=True),
        ),
    ]