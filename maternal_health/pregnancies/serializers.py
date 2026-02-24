from rest_framework import serializers
from .models import Pregnancy


class PregnancySerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = Pregnancy
        fields = '__all__'
        read_only_fields = ['expected_delivery_date'] # Hide expected_delivery_date on 
