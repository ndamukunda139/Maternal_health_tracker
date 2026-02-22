from django.shortcuts import render, redirect
from .forms import PatientRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Patient
from .serializers import PatientProfileSerializer
from rest_framework import permissions
from rest_framework import viewsets
from .permissions import PatientProfilePermission


class PatientProfileViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, PatientProfilePermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Patient.objects.filter(user=user)  # Patients can only see their own profile
        return Patient.objects.all()  # Doctors, nurses, and admins can see all profiles


