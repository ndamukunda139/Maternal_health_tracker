from rest_framework import serializers
from .models import Delivery


# Serializer for Delivery model, including all fields and read-only audit fields to ensure data integrity and proper tracking of changes, along with validation to ensure the delivery's patient matches the pregnancy's patient for consistency in obstetric records.
class DeliverySerializer(serializers.ModelSerializer):
    pregnancy_id = serializers.PrimaryKeyRelatedField(source='pregnancy', read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(source='patient', allow_null=True, read_only=True)

    class Meta:
        model = Delivery
        fields = '__all__'
        read_only_fields = ['delivery_date', 'created_by', 'updated_by', 'patient', 'pregnancy', 'patient_id', 'pregnancy_id']

    def validate(self, data):
        pregnancy = data.get("pregnancy")
        patient = data.get("patient")

        if pregnancy and patient and pregnancy.patient != patient:
            raise serializers.ValidationError("Delivery patient must match Delivery patient")
        if pregnancy and not patient:
            data["patient"] = pregnancy.patient
        return data