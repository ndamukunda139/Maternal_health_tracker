from .models import Pregnancy
from .serializers import PregnancySerializer
from rest_framework import permissions, viewsets, filters
from django.shortcuts import get_object_or_404
from patients.models import Patient

class PregnancyViewSet(viewsets.ModelViewSet):
    serializer_class = PregnancySerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filters and Search

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['status', 'notes', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['last_menstrual_period', 'expected_delivery_date']
    ordering = ['expected_delivery_date']


    def get_queryset(self):
        patient_id = self.kwargs.get("patient_pk")
        queryset = Pregnancy.objects.all()
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        user = self.request.user
        if hasattr(user, "role") and user.role == "patient":
            queryset = queryset.filter(patient__user=user)

        return queryset

    def perform_create(self, serializer):
        patient_id = self.kwargs.get("patient_pk")
        patient = get_object_or_404(Patient, pk=patient_id)
        serializer.save(
            patient=patient,
            created_by=self.request.user,
            updated_by=self.request.user
        )

