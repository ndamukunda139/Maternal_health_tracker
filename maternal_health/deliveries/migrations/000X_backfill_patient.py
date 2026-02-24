from django.db import migrations

def backfill_patient(apps, schema_editor):
    Delivery = apps.get_model('deliveries', 'Delivery')
    for delivery in Delivery.objects.filter(patient__isnull=True):
        if delivery.pregnancy and delivery.pregnancy.patient:
            delivery.patient = delivery.pregnancy.patient
            delivery.save(update_fields=['patient'])

class Migration(migrations.Migration):

    dependencies = [
        ('deliveries', '0004_alter_delivery_patient'),  # replace with your last migration
    ]

    operations = [
        migrations.RunPython(backfill_patient),
    ]