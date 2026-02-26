from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from django.conf import settings

# Pregnancy model with comprehensive fields, including risk factors and audit fields for created_by and updated_by to track changes and ensure data integrity.
class Pregnancy(models.Model):
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    gestational_age_weeks = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(46)]
    )
    last_menstrual_period = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)

    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    blood_type = models.CharField(
        max_length=3, choices=BLOOD_TYPES, blank=True, null=True, db_index=True
    )

    # Risk factors
    hiv_status = models.BooleanField(default=False)
    diabetes_status = models.BooleanField(default=False)
    hypertension_status = models.BooleanField(default=False) 
    multiple_pregnancy = models.BooleanField(default=False) 
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pregnancies_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pregnancies_updated'
    )

    class Meta:
        indexes = [
            models.Index(fields=['patient', 'last_menstrual_period']),
            models.Index(fields=['expected_delivery_date']), 
        ]

    def __str__(self):
        return f"Pregnancy of {self.patient} - GA: {self.gestational_age_weeks} weeks"

   
    """
    Helper function to auto-calc Expected Delivery Date 
    from Last Mansuation Period if not set.
        
    """
    
    def save(self, *args, **kwargs):
        if self.last_menstrual_period and not self.expected_delivery_date:
            self.expected_delivery_date = self.last_menstrual_period + timedelta(days=280)
        super().save(*args, **kwargs)
