from django.contrib import admin
from .models import PrenatalVisit, PostnatalVisit, GeneralVisit


# Base admin class to handle common logic for all visit types
class BaseVisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'visit_date', 'visit_type', 'created_by', 'updated_by')
    search_fields = ('visit_date', 'visit_type')
    list_filter = ('visit_date', 'visit_type')
    readonly_fields = ('created_by', 'updated_by', 'visit_date')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # new object
            obj.created_by = request.user
        obj.updated_by = request.user
        if not obj.provider_id:
            obj.provider = request.user
        super().save_model(request, obj, form, change)


# Admin classes for each visit type with specific fieldsets
class PrenatalVisitAdmin(BaseVisitAdmin):
    fieldsets = (
        (None, {'fields': (
            'patient', 'blood_pressure', 'heart_rate',
            'hemoglobin_level', 'weight_kg', 'height_cm',
            'uterine_height_cm', 'fetal_heart_rate',
            'fetal_movement_count', 'fetal_weight_estimate_g', 'notes'
        )}),
        ('Audit Info', {'fields': ('created_by', 'updated_by', 'visit_date')}),
    )

    def save_model(self, request, obj, form, change):
        obj.visit_type = "ANC"  # auto-set antenatal
        super().save_model(request, obj, form, change)


# Postnatal visits have some different fields, so we create a separate admin class for them
class PostnatalVisitAdmin(BaseVisitAdmin):
    fieldsets = (
        (None, {'fields': (
            'patient', 'blood_pressure', 'heart_rate',
            'hemoglobin_level', 'weight_kg', 'height_cm',
            'notes', 'breastfeeding_status',
            'postpartum_complications', 'newborn_health_issues'
        )}),
        ('Audit Info', {'fields': ('created_by', 'updated_by', 'visit_date')}),
    )

    def save_model(self, request, obj, form, change):
        obj.visit_type = "PNC"  # auto-set postnatal
        super().save_model(request, obj, form, change)

# General visits can be used for any other type of visit, so we create a more generic admin class for them
class GeneralVisitAdmin(BaseVisitAdmin):
    fieldsets = (
        (None, {'fields': (
            'patient', 'blood_pressure', 'heart_rate', 'notes'
        )}),
        ('Audit Info', {'fields': ('created_by', 'updated_by', 'visit_date')}),
    )

    def save_model(self, request, obj, form, change):
        obj.visit_type = "General"  # auto-set general
        super().save_model(request, obj, form, change)


# Register proxies separately
admin.site.register(PrenatalVisit, PrenatalVisitAdmin)
admin.site.register(PostnatalVisit, PostnatalVisitAdmin)
admin.site.register(GeneralVisit, GeneralVisitAdmin)