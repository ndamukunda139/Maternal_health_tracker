from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Pregnancy(models.Model):
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    gestational_age_weeks = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(46)])
    last_menstrual_period = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES, blank=True, null=True, db_index=True)
    hiv_status = models.BooleanField(default=False)
    diabetes_status = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['patient', 'last_menstrual_period'])]

    def __str__(self):
        return f"Pregnancy of {self.patient} - GA: {self.gestational_age_weeks} weeks"
