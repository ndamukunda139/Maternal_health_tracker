from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .models import CustomUser, DoctorProfile, NurseProfile, PatientProfile
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import RegistrationSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


# User registration view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    # registration should be open
    permission_classes = [AllowAny]

    # avoid SessionAuthentication (which enforces CSRF) for this open endpoint
    authentication_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user, token = serializer.save()  # make sure serializer returns both
                return Response({
                    'message': f'{user.role.capitalize()} - {user.username.capitalize()} registered successfully',
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Login view
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')  # use password1 as the actual password
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


# logout view
@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        from django.contrib.auth import logout
        logout(request)
        return JsonResponse({'message': 'Logout successful'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

# Create profile view
@login_required
@csrf_exempt
def profile(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            profile_data = {
                'username': user.username,  
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'is_staff': user.is_staff
            }
            
            # Add role-specific profile data
            if user.role == 'doctor':
                try:
                    doctor_profile = DoctorProfile.objects.get(user=user)
                    profile_data.update({
                        'specialization': doctor_profile.specialization,
                        'license_number': doctor_profile.license_number,
                        'hospital_affiliation': doctor_profile.hospital_affiliation,
                        'phone_number': doctor_profile.phone_number,
                        'office_address': doctor_profile.office_address,
                    })
                except DoctorProfile.DoesNotExist:
                    profile_data['error'] = 'Doctor profile not found'
                    
            elif user.role == 'nurse':
                try:
                    nurse_profile = NurseProfile.objects.get(user=user)
                    profile_data.update({
                        'department': nurse_profile.department,
                        'license_number': nurse_profile.license_number,
                        'hospital_affiliation': nurse_profile.hospital_affiliation,
                        'certifications': nurse_profile.certifications,
                        'shift_schedule': nurse_profile.shift_schedule,
                        'phone_number': nurse_profile.phone_number,
                        'office_address': nurse_profile.office_address,
                    })
                except NurseProfile.DoesNotExist:
                    profile_data['error'] = 'Nurse profile not found'
                    
            elif user.role == 'patient':
                try:
                    patient_profile = PatientProfile.objects.get(user=user)
                    profile_data.update({
                        'emergency_contact': patient_profile.emergency_contact,
                    })
                except PatientProfile.DoesNotExist:
                    profile_data['error'] = 'Patient profile not found'
            
            return JsonResponse(profile_data)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)






@login_required
@csrf_exempt
def admin_dashboard(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        if request.user.role != 'admin':
            return JsonResponse({'error': 'Access denied. Admins only.'}, status=403)

        users = CustomUser.objects.all()
        users_data = [
            {
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
            }
            for user in users
        ]
        return JsonResponse({'users': users_data})

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)