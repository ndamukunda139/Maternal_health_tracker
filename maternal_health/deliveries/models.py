from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Delivery(models.Model):
    pregnancy = models.ForeignKey('pregnancies.Pregnancy', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, null=True, blank=True)
    delivery_date = models.DateTimeField(auto_now_add=True)
    delivery_mode = models.CharField(max_length=50, db_index=True)  # e.g., 'vaginal', 'cesarean'
    birth_weight_g = models.PositiveIntegerField(validators=[MinValueValidator(200), MaxValueValidator(7000)])
    place_of_delivery = models.CharField(max_length=100, db_index=True)  # e.g., 'hospital', 'home'
    skilled_birth_attendant = models.BooleanField()
    newborn_gender = models.CharField(max_length=10)
    apgar_score_1min = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    apgar_score_5min = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    complications = models.TextField(blank=True, null=True)
    interventions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.CustomUser', related_name='deliveries_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey('users.CustomUser', related_name='deliveries_updated', on_delete=models.SET_NULL, null=True)

    class Meta:
        indexes = [models.Index(fields=['delivery_mode']), models.Index(fields=['place_of_delivery'])]

    def __str__(self):
        return f"Delivery {self.id} - Pregnancy {self.pregnancy} - Date {self.delivery_date.strftime('%Y-%m-%d')}"
