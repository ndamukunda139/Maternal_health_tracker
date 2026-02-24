from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Patient
from .serializers import PatientProfileSerializer
from rest_framework import permissions, viewsets, filters
from .permissions import PatientProfilePermission



class PatientProfileViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, PatientProfilePermission]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # Exact filters (must be real model fields)
    filterset_fields = ['date_of_birth']

    # Search across text fields
    search_fields = ['first_name', 'last_name', 'national_id', 'phone_number', 'user__email']

    # Ordering
    ordering_fields = ['first_name', 'last_name', 'date_of_birth']
    ordering = ['last_name']


    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Patient.objects.filter(user=user)  # Patients can only see their own profile
        return Patient.objects.all()  # Doctors, nurses, and admins can see all profiles


