from django.contrib import admin
from .models import Patient


# PatientAdmin with comprehensive display, search, and filter capabilities to enhance admin usability and data integrity, including read-only fields for auto-computed age and linked user information.
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user','first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number', 'date_of_birth')
    search_fields = ('first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number')
    list_filter = ('marital_status', 'educational_level', 'occupation')
    fieldsets = (
        (None, {'fields': ('user', 'first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number', 'date_of_birth')}),
        ('Additional Info', {'fields': ('age', 'marital_status', 'educational_level', 'occupation', 'gravidity', 'parity', 'communication_language', 'address',)}),
    )
    # do not include user.date_of_birth in add form — cannot set it here
    add_fieldsets = (
        (None, {
            'classes': ('wide',), 'fields': ('user', 'first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number', 'age', 'address', 'martial_status', 'educational_level', 'occupation', 'gravidity', 'parity', 'communication_language')}),
    )
    readonly_fields = ('age',)  # age is auto-computed from date_of_birth, so make it read-only in admin

    # expose the linked user's date_of_birth as read-only
    def get_readonly_fields(self, request, obj=None):
        
        '''

        When editing an existing Patient (obj != None), 
        make the primary identity fields read-only so only the "Additional Info" 
        section is editable. Allow superusers to override and edit these fields.
        
        '''
        if obj and not request.user.is_superuser:
            return ('user', 'first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number', 'date_of_birth')
        return self.readonly_fields

    def get_autocomplete_fields(self, request):
        return super().get_autocomplete_fields(request) + ('user',)
        


admin.site.register(Patient, PatientAdmin) # Register Patient model with custom admin interface



