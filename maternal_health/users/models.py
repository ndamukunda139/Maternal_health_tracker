from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


# User model extending AbstractUser
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Administrator'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return f"{self.username} ({self.role})"
    
# Role-specific profile models    
class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    hospital_affiliation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, db_index=True)
    office_address = models.TextField()

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"
    
# Nurses may have different fields than doctors, so we create a separate model for them
class NurseProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    hospital_affiliation = models.CharField(max_length=100)
    certifications = models.TextField()
    shift_schedule = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, db_index=True)
    office_address = models.TextField()

    def __str__(self):
        return f"Nurse {self.user.get_full_name()} - {self.department}"
    
    
# Patients may have different fields than doctors and nurses, so we create a separate model for them    
class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    emergency_contact = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.get_full_name()} - Patient Profile"

