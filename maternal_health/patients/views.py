from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Patient
from .serializers import PatientProfileSerializer
from rest_framework import permissions, viewsets, filters
from .permissions import PatientProfilePermission
from rest_framework.response import Response


# PatientProfileViewSet with role-based access control, filtering/searching, and automatic setting of audit fields to ensure data integrity and proper tracking of changes.
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
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Associate the patient profile with the logged-in user

    # Patient can't create, update or delete their own or others profile
    def create(self, request, *args, **kwargs):
        if request.user.role == 'patient':
            return Response({'detail': 'Patients cannot create the profile.'}, status=403)
        return super().create(request, *args, **kwargs)


