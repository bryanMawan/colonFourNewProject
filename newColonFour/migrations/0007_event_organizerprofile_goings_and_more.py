# Generated by Django 4.2.8 on 2024-01-16 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0006_organizerprofile_slug"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("date", models.DateTimeField()),
                ("location", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("is_hidden", models.BooleanField(default=False)),
                ("number_of_interests", models.IntegerField(default=0)),
                ("number_of_organizer_interests", models.IntegerField(default=0)),
                ("viewed", models.IntegerField(default=0)),
                (
                    "poster",
                    models.ImageField(
                        blank=True, null=True, upload_to="event_posters/"
                    ),
                ),
                (
                    "video",
                    models.FileField(blank=True, null=True, upload_to="event_videos/"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="organizerprofile",
            name="goings",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="organizerprofile",
            name="number_of_events",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="organizerprofile",
            name="profile_picture",
            field=models.ImageField(blank=True, null=True, upload_to="organizer_pics/"),
        ),
        migrations.AddField(
            model_name="organizerprofile",
            name="organizer_events",
            field=models.ManyToManyField(
                related_name="organizer_profiles", to="newColonFour.event"
            ),
        ),
    ]