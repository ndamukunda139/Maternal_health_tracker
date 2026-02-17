from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, NurseProfile, DoctorProfile, PatientProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'license_number', 'hospital_affiliation', 'phone_number', 'office_address']


class NurseProfileForm(forms.ModelForm):
    class Meta:
        model = NurseProfile
        fields = ['department', 'license_number', 'hospital_affiliation', 'certifications', 'shift_schedule', 'phone_number', 'office_address']


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['emergency_contact']


# User Change form
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role')


