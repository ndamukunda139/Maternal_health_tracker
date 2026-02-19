from rest_framework import serializers
from .models import Pregnancy

class PregnancySerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.username', read_only=True)
    class Meta:
        model = Pregnancy
        fields = '__all__'
        read_only_fields = ['expected_delivery_date']  # EDD is auto-calculated from Last Manstuation Period (LMP)