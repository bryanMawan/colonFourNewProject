# Generated by Django 4.2.15 on 2024-08-06 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0012_remove_event_end_time"),
    ]

    operations = [
        migrations.RemoveField(model_name="tip", name="contact_info",),
        migrations.RemoveField(model_name="tip", name="date",),
        migrations.RemoveField(model_name="tip", name="description",),
        migrations.RemoveField(model_name="tip", name="end_time",),
        migrations.RemoveField(model_name="tip", name="level",),
        migrations.RemoveField(model_name="tip", name="location",),
        migrations.RemoveField(model_name="tip", name="name",),
        migrations.RemoveField(model_name="tip", name="poster",),
        migrations.RemoveField(model_name="tip", name="start_time",),
        migrations.RemoveField(model_name="tip", name="styles",),
        migrations.RemoveField(model_name="tip", name="type",),
        migrations.RemoveField(model_name="tip", name="video",),
        migrations.AddField(
            model_name="tip",
            name="url",
            field=models.URLField(default=1),
            preserve_default=False,
        ),
    ]