# Generated by Django 3.2.6 on 2024-11-06 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cardDatabase', '0053_merge_20241106_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='rarity',
            field=models.CharField(blank=True, choices=[('C', 'Common'), ('U', 'Uncommon'), ('R', 'Rare'), ('SR', 'Super Rare'), ('XR', 'Extension Rare'), ('T', 'Token'), ('MR', 'Marvel Rare'), ('RR', 'Ruler'), ('JR', 'J-Ruler'), ('JR*', 'Colossal J-Ruler'), ('N', 'Normal'), ('AR', 'Ascended Ruler'), ('JAR', 'Ascended J-ruler'), ('SRR', 'SRR')], max_length=200),
        ),
        migrations.AlterField(
            model_name='cardability',
            name='special_style',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cardDatabase.abilitystyle'),
        ),
    ]
