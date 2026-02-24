from rest_framework import serializers
from .models import Visit


# Serializer for prenatal visits, showing only relevant fields
class PrenatalVisitSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.username", read_only=True)

    class Meta:
        model = Visit
        fields = [
            "id", "patient", "patient_name", "pregnancy",'provider',
            "visit_date", "visit_type",'blood_pressure', 'heart_rate', 'hemoglobin_level', 'weight_kg', 'height_cm',
            "uterine_height_cm", "fetal_heart_rate",
            "fetal_movement_count", "fetal_weight_estimate_g",'follow_up_date',
            "notes", "created_by", "updated_by",
        ]
        read_only_fields = ["created_by", "updated_by", "visit_type", "patient", "pregnancy", "provider"]

# Serializer for postnatal visits, with fields relevant to postpartum care and newborn health.
class PostnatalVisitSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.username", read_only=True)

    class Meta:
        model = Visit
        fields = [
            "id", "patient", "patient_name", "pregnancy", "delivery","provider",
            "visit_date", "visit_type",'blood_pressure', 'heart_rate', 'hemoglobin_level', 'weight_kg', 'height_cm',
            "breastfeeding_status", "postpartum_complications",
            "newborn_health_issues", "follow_up_date", "notes",
            "created_by", "updated_by",
        ]
        read_only_fields = ["created_by", "updated_by", "visit_type", "patient", "pregnancy", "provider", "delivery"]





'''
Serializer for the Visit model, with dynamic fields based on visit type.
This allows us to show/hide fields relevant to prenatal vs postnatal visits.

'''
class VisitSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.username", read_only=True)

    class Meta:
        model = Visit
        fields = [
            "id", "patient", "patient_name",
            "pregnancy", "delivery",
            "visit_date", "visit_type",

            # Prenatal fields
            "uterine_height_cm", "fetal_heart_rate",
            "fetal_movement_count", "fetal_weight_estimate_g",

            # Postnatal fields
            "breastfeeding_status", "postpartum_complications",
            "newborn_health_issues",

            # Common fields
            "notes", "created_by", "updated_by",
        ]
        read_only_fields = ["created_by", "updated_by", "visit_type", "patient", "pregnancy", "provider", "delivery"]


# Additional validation to ensure linked pregnancy/delivery belongs to the same patient
def validate(self, data):
    patient = data.get("patient")
    delivery = data.get("delivery")
    pregnancy = data.get("pregnancy")

    if delivery and patient and delivery.patient != patient:
        raise serializers.ValidationError(
        {"delivery": "Delivery must belong to the same patient as the visit."}
    )

    if pregnancy and patient and pregnancy.patient != patient:
        raise serializers.ValidationError(
        {"pregnancy": "Pregnancy must belong to the same patient as the visit."}
    )

    return data
