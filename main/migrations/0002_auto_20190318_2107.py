# Generated by Django 2.1.5 on 2019-03-18 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weather',
            name='date',
            field=models.FloatField(),
        ),
    ]
