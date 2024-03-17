# Generated by Django 4.2.8 on 2024-03-16 10:23

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to.",
                        related_name="customuser_groups",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="customuser_permissions",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
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
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("workshop", "Workshop"),
                            ("battle", "Battle"),
                            ("showcase", "Showcase"),
                        ],
                        default="workshop",
                        max_length=10,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("date", models.DateTimeField()),
                ("location", models.CharField(max_length=255)),
                (
                    "location_point",
                    models.CharField(blank=True, max_length=30, null=True),
                ),
                ("description", models.TextField()),
                ("is_hidden", models.BooleanField(default=True)),
                ("goings", models.IntegerField(default=0)),
                ("number_of_goings", models.IntegerField(default=0)),
                ("start_time", models.TimeField(blank=True, null=True)),
                ("end_time", models.TimeField(blank=True, null=True)),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("Open", "Open"),
                            ("Beginner", "Beginner"),
                            ("Intermediate", "Intermediate"),
                            ("Advanced", "Advanced"),
                        ],
                        default="1vs1",
                        max_length=13,
                    ),
                ),
                (
                    "styles",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
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
        migrations.CreateModel(
            name="OrganizerProfile",
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
                (
                    "gdpr_consented",
                    models.BooleanField(default=False, verbose_name="GDPR Consented"),
                ),
                (
                    "is_verified",
                    models.BooleanField(default=False, verbose_name="Is Verified"),
                ),
                ("slug", models.SlugField(blank=True, unique=True)),
                (
                    "profile_picture",
                    models.ImageField(
                        blank=True, null=True, upload_to="organizer_pics/"
                    ),
                ),
                ("goings", models.IntegerField(default=0)),
                ("number_of_events", models.IntegerField(default=0)),
                (
                    "organizer_events",
                    models.ManyToManyField(
                        related_name="organizer_profiles", to="newColonFour.event"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Showcase",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="newColonFour.event",
                    ),
                ),
            ],
            bases=("newColonFour.event",),
        ),
        migrations.CreateModel(
            name="Workshop",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="newColonFour.event",
                    ),
                ),
            ],
            bases=("newColonFour.event",),
        ),
        migrations.CreateModel(
            name="OrganizerVerificationRequest",
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
                ("url", models.URLField()),
                ("processed", models.BooleanField(default=False)),
                (
                    "organizer_profile",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="newColonFour.organizerprofile",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="event",
            name="organizer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organized_events",
                to="newColonFour.organizerprofile",
            ),
        ),
        migrations.CreateModel(
            name="Dancer",
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
                (
                    "country",
                    models.CharField(
                        choices=[("USA", "United States"), ("CAN", "Canada")],
                        max_length=3,
                    ),
                ),
                (
                    "picture",
                    models.ImageField(blank=True, null=True, upload_to="dancer_pics/"),
                ),
                (
                    "styles",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100), size=None
                    ),
                ),
                ("dancer_has_consented", models.BooleanField(default=False)),
                (
                    "events",
                    models.ManyToManyField(
                        related_name="dancers", to="newColonFour.event"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Battle",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="newColonFour.event",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("1vs1", "1vs1"),
                            ("2vs2", "2vs2"),
                            ("3vs3", "3vs3"),
                            ("crew", "Crew"),
                        ],
                        default="1vs1",
                        max_length=10,
                    ),
                ),
                ("is_7tosmoke", models.BooleanField(default=False)),
                (
                    "host",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="newColonFour.dancer",
                    ),
                ),
                (
                    "judges",
                    models.ManyToManyField(
                        blank=True,
                        related_name="battle_judges",
                        to="newColonFour.dancer",
                    ),
                ),
            ],
            bases=("newColonFour.event",),
        ),
    ]
