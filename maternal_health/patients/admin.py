from django.contrib import admin
from .models import Patient


# register models in admin portal
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user','first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number', 'date_of_birth')
    search_fields = ('first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number')
    list_filter = ('age', 'marital_status', 'educational_level', 'occupation')
    fieldsets = (
        (None, {'fields': ('user', 'first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number', 'date_of_birth')}),
        ('Additional Info', {'fields': ('age', 'address', 'marital_status', 'educational_level', 'occupation', 'gravidity', 'parity', 'communication_language')}),
    )
    # do not include user.date_of_birth in add form — cannot set it here
    add_fieldsets = (
        (None, {
            'classes': ('wide',), 'fields': ('user', 'first_name', 'last_name', 'medical_record_number', 'national_id', 'phone_number', 'age', 'address', 'martial_status', 'educational_level', 'occupation', 'gravidity', 'parity', 'communication_language')}),
    )

    # expose the linked user's date_of_birth as read-only
    '''
    readonly_fields = ('date_of_birth',)

    def date_of_birth(self, obj):
        return getattr(obj.user, 'date_of_birth', None)
    date_of_birth.admin_order_field = 'user__date_of_birth'
    date_of_birth.short_description = 'Date of birth' 
    
     # make primary identity fields read-only when editing an existing Patient profile, but allow superusers to edit them.
    
    '''

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
        


admin.site.register(Patient, PatientAdmin)



