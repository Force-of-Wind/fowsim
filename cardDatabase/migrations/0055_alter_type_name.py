# Generated by Django 3.2.6 on 2024-11-06 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardDatabase', '0054_auto_20241106_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='type',
            name='name',
            field=models.CharField(choices=[('Regalia', 'Regalia'), ('Chant', 'Chant'), ('Rune', 'Rune'), ('Master Rune', 'Master Rune'), ('Magic Stone', 'Magic Stone'), ('Basic Magic Stone', 'Basic Magic Stone'), ('Special Magic Stone', 'Special Magic Stone'), ('True Magic Stone', 'True Magic Stone'), ('Ruler', 'Ruler'), ('Basic J-Ruler', 'Basic J-Ruler'), ('J-RulerSpell:Chant-Standby', 'J-RulerSpell:Chant-Standby'), ('Resonator', 'Resonator'), ('Sub-ruler', 'Sub-ruler'), ('Extension Rule', 'Extension Rule'), ('Darkness Magic Stone', 'Darkness Magic Stone'), ('Fire Magic Stone', 'Fire Magic Stone'), ('Light Magic Stone', 'Light Magic Stone'), ('Water Magic Stone', 'Water Magic Stone'), ('Wind Magic Stone', 'Wind Magic Stone'), ('Void Magic Stone', 'Void Magic Stone')], max_length=200),
        ),
    ]