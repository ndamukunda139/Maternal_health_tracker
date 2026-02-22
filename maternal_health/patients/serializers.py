from rest_framework import serializers
from .models import Patient
from datetime import date

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'username', 'email', 'role', 'emergency_contact']

class PatientProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id',
            'username', 'email', 'role',
            'first_name', 'last_name', 'medical_record_number',
            'date_of_birth', 'age', 'address', 'marital_status',
            'national_id', 'phone_number', 'educational_level',
            'occupation', 'gravidity', 'parity', 'communication_language'
        ]
        read_only_fields = ['username', 'email', 'role', 'age']

    def get_age(self, obj):
        if obj.date_of_birth:
            today = date.today()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None

    def validate(self, data):
        # Example of data validation only
        if data.get('gravidity') and data.get('parity'):
            if data['parity'] > data['gravidity']:
                raise serializers.ValidationError("Parity cannot exceed gravidity.")
        return data
