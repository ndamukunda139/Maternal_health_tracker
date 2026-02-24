from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from .models import Visit
from .serializers import VisitSerializer, PrenatalVisitSerializer, PostnatalVisitSerializer
from deliveries.models import Delivery
from pregnancies.models import Pregnancy
from patients.models import Patient
from rest_framework import serializers, status, filters
from rest_framework.response import Response


class VisitViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
    lookup_url_kwarg = "visit_pk"   # optional, but makes nested kwargs clearer

    # Implementing filter and search

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['visit_type', 'notes', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['visit_date']
    ordering = ['visit_date']

    def get_queryset(self):
        queryset = Visit.objects.all()

        patient_id = self.kwargs.get("patient_pk")
        pregnancy_id = self.kwargs.get("pregnancy_pk")
        delivery_id = self.kwargs.get("delivery_pk")

        # Filter by patient if nested
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        # Filter by pregnancy if nested
        if pregnancy_id:
            queryset = queryset.filter(pregnancy_id=pregnancy_id)

        # Filter by delivery if nested
        if delivery_id:
            queryset = queryset.filter(delivery_id=delivery_id)

        # Restrict patients to only their own visits
        user = self.request.user
        if hasattr(user, "role") and user.role == "patient":
            queryset = queryset.filter(patient__user=user)

        return queryset

    def get_serializer_class(self):
        if "pregnancy_pk" in self.kwargs:
            return PrenatalVisitSerializer
        elif "delivery_pk" in self.kwargs:
            return PostnatalVisitSerializer
        return VisitSerializer

    def perform_create(self, serializer):
    
        patient_id = self.kwargs.get("patient_pk")
        pregnancy_id = self.kwargs.get("pregnancy_pk")
        delivery_id = self.kwargs.get("delivery_pk")

        patient = get_object_or_404(Patient, pk=patient_id) if patient_id else None
        pregnancy = get_object_or_404(Pregnancy, pk=pregnancy_id, patient_id=patient_id) if pregnancy_id else None
        delivery = get_object_or_404(Delivery, pk=delivery_id) if delivery_id else None

         # Decide visit type automatically
        if pregnancy_id:
            visit_type = "Antenatal"
        elif delivery_id:
            visit_type = "Postnatal"
        else:
            visit_type = "General"



        # Optional consistency check
        if delivery and patient and delivery.patient_id != int(patient_id):
            raise serializers.ValidationError("Delivery does not belong to this patient.")

        serializer.save(
            patient=patient,
            pregnancy=pregnancy,
            delivery=delivery,
            visit_type=visit_type,
            provider=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user
        )


        # Override to provide custom error responses for validation errors
    def handle_exception(self, exc):
        if isinstance(exc, serializers.ValidationError):
            return Response(
                {"detail": "Validation failed", "error": exc.detail}, 
                status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)