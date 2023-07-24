# Generated by Django 3.2.6 on 2023-07-12 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardDatabase', '0044_alter_type_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='rarity',
            field=models.CharField(blank=True, choices=[('C', 'Common'), ('U', 'Uncommon'), ('R', 'Rare'), ('SR', 'Super Rare'), ('XR', 'Extension Rare'), ('T', 'Token'), ('MR', 'Marvel Rare'), ('RR', 'Ruler'), ('JR', 'J-Ruler'), ('JR*', 'Colossal J-Ruler'), ('N', 'Normal'), ('AR', 'Ascended Ruler'), ('JAR', 'Ascended J-ruler')], max_length=200),
        ),
    ]