# Generated by Django 4.2.14 on 2024-07-30 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0010_remove_dancer_styles_alter_dancer_country"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
