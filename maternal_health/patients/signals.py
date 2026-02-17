from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from uuid import uuid4

from .models import Patient

# Signal to auto-create a Patient profile when a new user with role 'patient' is created or updated. This ensures that every patient user has a corresponding Patient profile, even if the user data is sparse at creation time.

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_for_new_user(sender, instance, created,  **kwargs):
    """Auto-create a Patient profile when a new user with role 'patient' is created .

    We use get_or_create with generated unique identifiers for required unique
    fields so the profile can be created even if upstream user data is sparse.
    """
    # Create a Patient profile when the user has role 'patient', or
    # remove it when the user no longer has that role.
    # This covers both new users (created=True) and existing users that
    # are updated to change roles. `get_or_create` prevents duplicates;
    # `filter(...).delete()` safely removes any existing profile.
    role = getattr(instance, 'role', None)
    if role == 'patient':
        defaults = {
            'first_name': getattr(instance, 'first_name', '') or '',
            'last_name': getattr(instance, 'last_name', '') or '',
            'medical_record_number': f"MRN-{instance.username}-{uuid4().hex[:8]}",
            'national_id': f"MHS-{instance.username}-{uuid4().hex[:8]}",
            'phone_number': getattr(instance, 'phone_number', '') or '',
            'date_of_birth': getattr(instance, 'date_of_birth', None),
            'age': None,
            'address': '',
            'marital_status': '',
            'educational_level': '',
            'occupation': '',
            'gravidity': 0,
            'parity': 0,
            'communication_language': '',
        }

        Patient.objects.get_or_create(user=instance, defaults=defaults)
    else:
        # If the user's role is not 'patient', remove any existing Patient profile
        # so the patient list stays accurate when roles are changed.
        Patient.objects.filter(user=instance).delete()
