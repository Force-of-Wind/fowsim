from django.db import migrations

from fowsim import constants as CONS


def create_paradoxical_type(apps, schema_editor):
    Type = apps.get_model("cardDatabase", "Type")
    Type.objects.get_or_create(name=CONS.CARD_TYPE_PARADOXICAL)


def remove_paradoxical_type(apps, schema_editor):
    Type = apps.get_model("cardDatabase", "Type")
    Type.objects.filter(name=CONS.CARD_TYPE_PARADOXICAL).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cardDatabase", "0072_card_display_name_card_grouping_key_card_modal_face_and_more"),
    ]

    operations = [
        migrations.RunPython(create_paradoxical_type, remove_paradoxical_type),
    ]
