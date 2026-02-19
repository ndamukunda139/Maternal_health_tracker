from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, serializers
from .models import Visit
from .serializers import PrenatalVisitSerializer, PostnatalVisitSerializer, VisitSerializer
from rest_framework import permissions
from .permissions import VisitPermission
from rest_framework.response import Response
from deliveries.models import Delivery
from pregnancies.models import Pregnancy



class VisitViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, VisitPermission]

    def get_queryset(self):
        queryset = Visit.objects.all()
        patient_id = self.kwargs.get("patient_pk")
        pregnancy_id = self.kwargs.get("pregnancy_pk")
        delivery_id = self.kwargs.get("delivery_pk")

        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if pregnancy_id:
            queryset = queryset.filter(pregnancy_id=pregnancy_id)
        if delivery_id:
            queryset = queryset.filter(delivery_id=delivery_id)

        user = self.request.user
        if user.role == "patient":
            queryset = queryset.filter(patient__user=user)

        return queryset

    def get_serializer_class(self):
        if "pregnancy_pk" in self.kwargs:
            return PrenatalVisitSerializer
        elif "delivery_pk" in self.kwargs:
            return PostnatalVisitSerializer
        return VisitSerializer  # fallback for general visits

    def perform_create(self, serializer):
        patient_id = self.kwargs.get("patient_pk")
        pregnancy_id = self.kwargs.get("pregnancy_pk")
        delivery_id = self.kwargs.get("delivery_pk")

        delivery = None
        pregnancy = None

        if delivery_id:
            delivery = get_object_or_404(Delivery, pk=delivery_id, patient_id=patient_id)

        if pregnancy_id:
            pregnancy = get_object_or_404(Pregnancy, pk=pregnancy_id, patient_id=patient_id)



        serializer.save(
            created_by=self.request.user,
            patient_id=patient_id,
            delivery=delivery,
            pregnancy=pregnancy,
        )

    # Override to provide custom error responses for validation errors
    def handle_exception(self, exc):
        if isinstance(exc, serializers.ValidationError):
            return Response(
                {"detail": "Validation failed", "error": exc.detail}, 
                status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)

