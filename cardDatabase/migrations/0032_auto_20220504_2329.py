# Generated by Django 3.2.6 on 2022-05-04 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardDatabase', '0031_auto_20220427_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decklist',
            name='name',
            field=models.CharField(max_length=100000),
        ),
        migrations.AlterField(
            model_name='decklistzone',
            name='name',
            field=models.CharField(max_length=10000),
        ),
    ]
