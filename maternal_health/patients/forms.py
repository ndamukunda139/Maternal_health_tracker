from django import forms
from .models import Patient

# PatientRegistrationForm for creating new patient profiles with validation and user-friendly widgets, including a date picker for date of birth to enhance the registration process and ensure accurate data entry.
class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'medical_record_number',
            'date_of_birth', 'address', 'marital_status',
            'national_id', 'phone_number', 'educational_level',
            'occupation', 'gravidity', 'parity', 'communication_language'

        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
