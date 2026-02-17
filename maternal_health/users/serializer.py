from rest_framework import serializers
from .models import CustomUser, DoctorProfile, NurseProfile, PatientProfile
from django.contrib.auth.password_validation import validate_password
from datetime import datetime, timedelta
from django.contrib.auth import password_validation
from rest_framework.authtoken.models import Token
import re

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)

    # Optional fields
    date_of_birth = serializers.DateField(required=False)
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    emergency_contact = serializers.CharField(required=False)

    # Doctor-specific
    specialization = serializers.CharField(required=False)
    license_number = serializers.CharField(required=False)
    hospital_affiliation = serializers.CharField(required=False)
    office_address = serializers.CharField(required=False)

    # Nurse-specific
    department = serializers.CharField(required=False)
    certifications = serializers.CharField(required=False)
    shift_schedule = serializers.CharField(required=False)

    #Patient-specific
    emergency_contact = serializers.CharField(required=False)

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Run Django’s built-in password validators
        try:
            password_validation.validate_password(data['password'], user=CustomUser(username=data['username'], email=data['email']))
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        
        # Unique username/email checks
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username is already taken."})
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email is already registered."})
        
        # Date of birth validation
        dob = data.get('date_of_birth')
        if dob:
            if dob > datetime.now().date():
                raise serializers.ValidationError({"date_of_birth": "Cannot be in the future."})
            if data['role'] in ['doctor', 'nurse', 'admin']:
                age_limit_date = datetime.now().date() - timedelta(days=18*365)
                if dob > age_limit_date:
                    raise serializers.ValidationError({"date_of_birth": f"{data['role'].capitalize()} must be at least 21 years old."})
        # Phone validation
        phone = data.get('phone_number')
        if phone:
            phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_pattern.match(phone):
                raise serializers.ValidationError({"phone_number": "Invalid phone number format."})
        
        # Validate role-specific fields
        role = data['role']
        if role == 'doctor':
            required_fields = ['specialization', 'license_number', 'hospital_affiliation', 'phone_number', 'office_address']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f"{field.replace('_', ' ').capitalize()} is required for doctors."}) 
        elif role == 'nurse':
            required_fields = ['department', 'license_number', 'hospital_affiliation', 'certifications', 'shift_schedule', 'phone_number', 'office_address']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f"{field.replace('_', ' ').capitalize()} is required for nurses."})
        elif role == 'patient':
            if not data.get('emergency_contact'):
                raise serializers.ValidationError({"emergency_contact": "Emergency contact is required for patients."})


        return data
    
    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password') # use password1 as the actual password
        validated_data.pop('password2') # remove password2 as it's not needed for user creation

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            role=role
        )

        # Role-specific profile creation
        if role == 'doctor':
            DoctorProfile.objects.create(
                user=user,
                specialization=validated_data['specialization'],
                license_number=validated_data['license_number'],
                hospital_affiliation=validated_data.get('hospital_affiliation', ''),
                phone_number=validated_data['phone_number'],
                office_address=validated_data['office_address'] 
            )
        elif role == 'nurse':
            NurseProfile.objects.create(
                user=user,
                department=validated_data['department'],
                license_number=validated_data['license_number'],
                hospital_affiliation=validated_data['hospital_affiliation'],
                certifications=validated_data.get('certifications', ''),
                shift_schedule=validated_data.get('shift_schedule', ''),
                phone_number=validated_data['phone_number'],
                office_address=validated_data['office_address'],
            )
        elif role == 'patient':
            PatientProfile.objects.create(
                user=user,
                emergency_contact=validated_data['emergency_contact']
            )
        # create and run token for the user
        token, _ = Token.objects.get_or_create(user=user)
        return user, token








