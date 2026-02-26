from django.contrib import admin
from .models import Pregnancy

# PregnancyAdmin with audit fields and filtering/search capabilities to enhance admin usability and data integrity.
class PregnancyAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'blood_type', 'hiv_status', 'diabetes_status', 'hypertension_status', 'multiple_pregnancy', 'created_by', 'updated_by')
    search_fields = ('hiv_status', 'blood_type')
    list_filter = ('expected_delivery_date', 'blood_type')
    fieldsets = (
        (None, {'fields': ('patient', 'gestational_age_weeks','last_menstrual_period','blood_type', 'hiv_status', 'diabetes_status', 'hypertension_status', 'multiple_pregnancy')}),
        ('Audit Info', {'fields': ('created_by', 'updated_by')}), 
    )
    readonly_fields = ('created_by', 'updated_by')  # audit fields should be read-only in admin
    
    # Create audit fields on save
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Pregnancy, PregnancyAdmin) # Register Pregnancy model with custom admin interface