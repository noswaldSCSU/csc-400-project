# Generated by Django 5.0.6 on 2024-07-20 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vaast_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='instructions',
            field=models.CharField(max_length=3000, null=True),
        ),
    ]