from django.contrib import admin
from .models import Delivery

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'pregnancy', 'delivery_date', 'delivery_mode',
                    'place_of_delivery', 'newborn_gender', 'complications',
                    'created_by', 'updated_by')
    search_fields = ('delivery_mode',)
    list_filter = ('delivery_mode', 'place_of_delivery')
    fieldsets = (
        (None, {'fields': ('delivery_mode', 'complications', 'interventions', 'place_of_delivery', 'skilled_birth_attendant', 'newborn_gender', 'apgar_score_1min', 'apgar_score_5min', 'alive', 'congenital_anomalies', 'neonatal_complications', 'birth_weight_g', 'pregnancy')}),
        ('Audit Info', {'fields': ('created_by', 'updated_by')}),
    )
    readonly_fields = ('delivery_date', 'created_by', 'updated_by', 'patient_id')  # delivery_date and audit fields should be read-only in admin

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # new object
            obj.created_by = request.user
        obj.updated_by = request.user
        # Auto‑set delivery_date if needed
        if not obj.delivery_date:
            from django.utils import timezone
            obj.delivery_date = timezone.now().date()
        super().save_model(request, obj, form, change)

admin.site.register(Delivery, DeliveryAdmin)