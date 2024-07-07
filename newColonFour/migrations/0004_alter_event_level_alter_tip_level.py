# Generated by Django 4.2.8 on 2024-07-07 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0003_tip"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="level",
            field=models.CharField(
                choices=[
                    ("Open", "Open"),
                    ("Rookie", "Rookie"),
                    ("Advanced", "Advanced"),
                ],
                default="1vs1",
                max_length=13,
            ),
        ),
        migrations.AlterField(
            model_name="tip",
            name="level",
            field=models.CharField(
                choices=[
                    ("Open", "Open"),
                    ("Rookie", "Rookie"),
                    ("Advanced", "Advanced"),
                ],
                default="1vs1",
                max_length=13,
            ),
        ),
    ]