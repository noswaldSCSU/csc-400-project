# Generated by Django 5.0.6 on 2024-08-06 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vaast_app', '0007_experiment_image_alter_experiment_font_size_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='is_remote',
            field=models.BooleanField(default=True),
        ),
    ]
