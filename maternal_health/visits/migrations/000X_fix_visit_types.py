# visits/migrations/000X_fix_visit_types.py
from django.db import migrations

def fix_visit_types(apps, schema_editor):
    Visit = apps.get_model('visits', 'Visit')

    # Normalize ANC → antenatal
    Visit.objects.filter(visit_type="ANC").update(visit_type="Antenatal")

    # Normalize PNC → postnatal
    Visit.objects.filter(visit_type="PNC").update(visit_type="Postnatal")

class Migration(migrations.Migration):

    dependencies = [
        ('visits', '0003_alter_visit_visit_type'),
    ]

    operations = [
        migrations.RunPython(fix_visit_types),
    ]