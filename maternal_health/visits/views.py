from django.shortcuts import render
from rest_framework import viewsets
from .models import Visit
from .serializers import VisitSerializer
from rest_framework import permissions
from .permissions import VisitPermission



class VisitViewSet(viewsets.ModelViewSet):
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated, VisitPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = Visit.objects.all()

        # If nested under patient
        patient_id = self.kwargs.get("patient_pk")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        # Restrict patients to their own visits
        if user.role == "patient":
            queryset = queryset.filter(patient__user=user)

        return queryset

    def perform_create(self, serializer):
        patient_id = self.kwargs.get("patient_pk")
        serializer.save(created_by=self.request.user, patient_id=patient_id)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


