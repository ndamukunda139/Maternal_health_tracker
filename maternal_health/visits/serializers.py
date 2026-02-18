from rest_framework import serializers
from .models import Visit

'''
Serializer for the Visit model, with dynamic fields based on visit type.
This allows us to show/hide fields relevant to prenatal vs postnatal visits.

'''
class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = "__all__"

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        visit_type = None

        # If creating, check request data
        if request and request.method == "POST":
            visit_type = request.data.get("visit_type")

        # If updating, check instance
        elif self.instance:
            visit_type = getattr(self.instance, "visit_type", None)

        # Hide fields based on visit type
        if visit_type == "ANC":
            # Remove postnatal-only fields
            for f in ["breastfeeding_status", "postpartum_complications", "newborn_health_issues"]:
                fields.pop(f, None)

        elif visit_type == "PNC":
            # Remove prenatal-only fields
            for f in ["uterine_height_cm", "fetal_heart_rate", "fetal_movement_count", "fetal_weight_estimate_g"]:
                fields.pop(f, None)

        return fields