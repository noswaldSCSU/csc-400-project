# Generated by Django 5.0.7 on 2024-07-28 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maat_app', '0003_experiment_background_color_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='random_fixation',
            field=models.IntegerField(default=1000),
        ),
    ]
