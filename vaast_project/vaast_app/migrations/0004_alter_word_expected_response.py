# Generated by Django 5.0.6 on 2024-08-02 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vaast_app', '0003_alter_experiment_instructions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='expected_response',
            field=models.CharField(choices=[('y', 'Yes'), ('n', 'No')], max_length=1, null=True),
        ),
    ]
