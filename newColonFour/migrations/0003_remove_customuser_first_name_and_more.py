# Generated by Django 4.2.8 on 2023-12-30 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0002_organizerprofile"),
    ]

    operations = [
        migrations.RemoveField(model_name="customuser", name="first_name",),
        migrations.RemoveField(model_name="customuser", name="last_name",),
        migrations.AddField(
            model_name="customuser",
            name="name",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
    ]
