from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Visit(models.Model):
    VISIT_TYPES = [
        ('ANC', 'Antenatal Care'),
        ('PNC', 'Postnatal Care')
    ]
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    provider = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    pregnancy = models.ForeignKey('pregnancies.Pregnancy', on_delete=models.CASCADE, blank=True, null=True)
    delivery = models.ForeignKey('deliveries.Delivery', on_delete=models.SET_NULL, blank=True, null=True)
    visit_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visit_type = models.CharField(max_length=100, choices=VISIT_TYPES, db_index=True)
    blood_pressure = models.CharField(max_length=7)
    heart_rate = models.PositiveSmallIntegerField(validators=[MinValueValidator(30), MaxValueValidator(220)])
    hemoglobin_level = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(0)], null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)

    # Pregnancy-specific fields
    uterine_height_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    fetal_heart_rate = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(50), MaxValueValidator(220)])
    fetal_movement_count = models.PositiveSmallIntegerField(blank=True, null=True)
    fetal_weight_estimate_g = models.PositiveIntegerField(blank=True, null=True)

    # Postnatal-specific fields
    breastfeeding_status = models.BooleanField(null=True, blank=True)
    postpartum_complications = models.TextField(blank=True, null=True)
    newborn_health_issues = models.TextField(blank=True, null=True)

    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    complications = models.TextField(blank=True, null=True)
    interventions = models.TextField(blank=True, null=True)
    referrals = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('users.CustomUser', related_name='visit_created_by', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey('users.CustomUser', related_name='visit_updated_by', on_delete=models.SET_NULL, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['provider']),
            models.Index(fields=['visit_date']),
        ]

    def __str__(self):
        return f"Visit {self.id} - Patient {self.patient} "

# Proxy models for specific visit types
class PrenatalVisit(Visit):
    class Meta:
        proxy = True
        verbose_name = "Prenatal Visit"
        verbose_name_plural = "Prenatal Visits"

class PostnatalVisit(Visit):
    class Meta:
        proxy = True
        verbose_name = "Postnatal Visit"
        verbose_name_plural = "Postnatal Visits"

class GeneralVisit(Visit):
    class Meta:
        proxy = True
        verbose_name = "General Visit"
        verbose_name_plural = "General Visits"