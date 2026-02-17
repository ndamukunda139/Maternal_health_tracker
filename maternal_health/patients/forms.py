from django import forms
from .models import Patient

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'medical_record_number',
            'date_of_birth', 'age', 'address', 'marital_status',
            'national_id', 'phone_number', 'educational_level',
            'occupation', 'gravidity', 'parity', 'communication_language'

        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
