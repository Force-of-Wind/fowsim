# Generated by Django 3.2.6 on 2022-10-17 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cardDatabase', '0039_profile_is_judge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ruling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cardDatabase.profile')),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cardDatabase.card')),
            ],
        ),
    ]
