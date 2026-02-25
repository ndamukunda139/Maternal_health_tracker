from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Delivery(models.Model):
    pregnancy = models.ForeignKey('pregnancies.Pregnancy', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)

    delivery_date = models.DateTimeField(auto_now_add=True)

    DELIVERY_MODES = [
        ("vaginal", "Vaginal"),
        ("cesarean", "Cesarean"),
        ("assisted", "Assisted"),
    ]
    delivery_mode = models.CharField(max_length=50, choices=DELIVERY_MODES, db_index=True)

    birth_weight_g = models.PositiveIntegerField(
        validators=[MinValueValidator(200), MaxValueValidator(7000)]
    )
    place_of_delivery = models.CharField(max_length=100, db_index=True)
    skilled_birth_attendant = models.BooleanField()

    # Newborn outcomes
    newborn_gender = models.CharField(max_length=10)
    apgar_score_1min = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    apgar_score_5min = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    alive = models.BooleanField(default=True)  
    congenital_anomalies = models.TextField(blank=True, null=True)  
    neonatal_complications = models.TextField(blank=True, null=True)  

    complications = models.TextField(blank=True, null=True)
    interventions = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.CustomUser', related_name='deliveries_created',
        on_delete=models.SET_NULL, null=True
    )
    updated_by = models.ForeignKey(
        'users.CustomUser', related_name='deliveries_updated',
        on_delete=models.SET_NULL, null=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['delivery_mode']),
            models.Index(fields=['place_of_delivery']),
            models.Index(fields=['delivery_date']), 
        ]
    # Enforce patient consistency with pregnancy
    def save(self, *args, **kwargs):
    # Always enforce patient consistency
        if self.pregnancy_id:
            # Assign patient directly from pregnancy_id relation
            from pregnancies.models import Pregnancy
            pregnancy = Pregnancy.objects.get(pk=self.pregnancy_id)
            self.patient = pregnancy.patient

            if self.patient and pregnancy.patient != self.patient:
                raise ValueError("Delivery patient must match pregnancy patient.")

        super().save(*args, **kwargs)