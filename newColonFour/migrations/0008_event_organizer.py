# Generated by Django 4.2.8 on 2024-01-16 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0007_event_organizerprofile_goings_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="organizer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organized_events",
                to="newColonFour.organizerprofile",
            ),
        ),
    ]