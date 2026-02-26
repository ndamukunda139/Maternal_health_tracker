from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from patients.models import Patient
from pregnancies.models import Pregnancy
from .models import Delivery
from datetime import date

User = get_user_model()


class DeliverySummaryAuthorizationTests(TestCase):
    """Test patient authentication and authorization for delivery analytics endpoints"""

    def setUp(self):
        """Create test users and patients"""
        # Create patient users (Patient records auto-created via signal)
        self.patient_user_1 = User.objects.create_user(
            username='patient1',
            password='testpass123',
            role='patient',
            first_name='Jane',
            last_name='Doe'
        )
        self.patient_user_2 = User.objects.create_user(
            username='patient2',
            password='testpass123',
            role='patient',
            first_name='Mary',
            last_name='Smith'
        )

        # Get auto-created Patient records and update them
        self.patient_1 = Patient.objects.get(user=self.patient_user_1)
        self.patient_1.date_of_birth = date(1990, 5, 15)
        self.patient_1.address = '123 Main St'
        self.patient_1.marital_status = 'married'
        self.patient_1.educational_level = 'Graduate'
        self.patient_1.occupation = 'Teacher'
        self.patient_1.phone_number = '555-0001'
        self.patient_1.save()

        self.patient_2 = Patient.objects.get(user=self.patient_user_2)
        self.patient_2.date_of_birth = date(1992, 3, 20)
        self.patient_2.address = '456 Oak Ave'
        self.patient_2.marital_status = 'single'
        self.patient_2.educational_level = 'Bachelor'
        self.patient_2.occupation = 'Nurse'
        self.patient_2.phone_number = '555-0002'
        self.patient_2.save()

        # Create clinician users (no Patient records created for non-patient roles)
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            password='testpass123',
            role='doctor',
            first_name='John',
            last_name='Doctor'
        )
        self.nurse_user = User.objects.create_user(
            username='nurse1',
            password='testpass123',
            role='nurse',
            first_name='Nancy',
            last_name='Nurse'
        )
        self.admin_user = User.objects.create_user(
            username='admin1',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User'
        )

        # Create pregnancies for patient 1
        self.pregnancy_1 = Pregnancy.objects.create(
            patient=self.patient_1,
            gestational_age_weeks=12,
            last_menstrual_period=date(2022, 10, 15),
            expected_delivery_date=date(2023, 7, 22),
            blood_type='O+'
        )
        self.pregnancy_2 = Pregnancy.objects.create(
            patient=self.patient_1,
            gestational_age_weeks=20,
            last_menstrual_period=date(2024, 1, 20),
            expected_delivery_date=date(2024, 10, 27),
            blood_type='A-'
        )

        # Create pregnancy for patient 2
        self.pregnancy_3 = Pregnancy.objects.create(
            patient=self.patient_2,
            gestational_age_weeks=16,
            last_menstrual_period=date(2023, 3, 10),
            expected_delivery_date=date(2023, 12, 17),
            blood_type='B+'
        )

        # Create deliveries for patient 1
        self.delivery_1 = Delivery.objects.create(
            pregnancy=self.pregnancy_1,
            patient=self.patient_1,
            delivery_date=date(2023, 1, 15),
            delivery_mode='vaginal',
            birth_weight_g=3500,
            place_of_delivery='Hospital A',
            skilled_birth_attendant=True,
            newborn_gender='Female',
            apgar_score_1min=8,
            apgar_score_5min=9,
            alive=True
        )
        self.delivery_2 = Delivery.objects.create(
            pregnancy=self.pregnancy_2,
            patient=self.patient_1,
            delivery_date=date(2024, 6, 20),
            delivery_mode='vaginal',
            birth_weight_g=3200,
            place_of_delivery='Hospital A',
            skilled_birth_attendant=True,
            newborn_gender='Male',
            apgar_score_1min=7,
            apgar_score_5min=8,
            alive=True
        )

        # Create delivery for patient 2
        self.delivery_3 = Delivery.objects.create(
            pregnancy=self.pregnancy_3,
            patient=self.patient_2,
            delivery_date=date(2023, 8, 10),
            delivery_mode='cesarean',
            birth_weight_g=3800,
            place_of_delivery='Hospital B',
            skilled_birth_attendant=True,
            newborn_gender='Male',
            apgar_score_1min=9,
            apgar_score_5min=10,
            alive=True
        )

        self.client = APIClient()

    def test_patient_access_own_delivery_summary(self):
        """Patient should be able to access their own delivery summary"""
        self.client.force_authenticate(user=self.patient_user_1)
        response = self.client.get(f'/api/patients/{self.patient_1.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 2)
        self.assertIn('by_mode', data)
        self.assertIn('average_birth_weight_g', data)

    def test_patient_cannot_access_other_patient_delivery_summary(self):
        """Patient should be forbidden from accessing another patient's delivery summary"""
        self.client.force_authenticate(user=self.patient_user_1)
        response = self.client.get(f'/api/patients/{self.patient_2.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_cannot_access_global_delivery_summary(self):
        """Patient should be forbidden from accessing global delivery summary"""
        self.client.force_authenticate(user=self.patient_user_1)
        response = self.client.get('/api/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_can_access_patient_delivery_summary(self):
        """Doctor should be able to access any patient's delivery summary"""
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get(f'/api/patients/{self.patient_1.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 2)

    def test_nurse_can_access_patient_delivery_summary(self):
        """Nurse should be able to access any patient's delivery summary"""
        self.client.force_authenticate(user=self.nurse_user)
        response = self.client.get(f'/api/patients/{self.patient_2.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 1)

    def test_admin_can_access_patient_delivery_summary(self):
        """Admin should be able to access any patient's delivery summary"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/patients/{self.patient_1.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 2)

    def test_clinician_can_access_global_delivery_summary(self):
        """Clinician (doctor) should be able to access global delivery summary"""
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get('/api/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 3)  # all deliveries

    def test_unauthenticated_user_cannot_access_summary(self):
        """Unauthenticated user should not be able to access delivery summary"""
        response = self.client.get(f'/api/patients/{self.patient_1.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_access_own_delivery_summary(self):
        """Patient should be able to access their own delivery summary"""
        self.client.force_authenticate(user=self.patient_user_1)
        response = self.client.get(f'/api/patients/{self.patient_1.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 2)
        self.assertIn('by_mode', data)
        self.assertIn('average_birth_weight_g', data)

    def test_patient_cannot_access_other_patient_delivery_summary(self):
        """Patient should be forbidden from accessing another patient's delivery summary"""
        self.client.force_authenticate(user=self.patient_user_1)
        response = self.client.get(f'/api/patients/{self.patient_2.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_cannot_access_global_delivery_summary(self):
        """Patient should be forbidden from accessing global delivery summary"""
        self.client.force_authenticate(user=self.patient_user_1)
        response = self.client.get('/api/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_can_access_patient_delivery_summary(self):
        """Doctor should be able to access any patient's delivery summary"""
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get(f'/api/patients/{self.patient_1.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 2)

    def test_nurse_can_access_patient_delivery_summary(self):
        """Nurse should be able to access any patient's delivery summary"""
        self.client.force_authenticate(user=self.nurse_user)
        response = self.client.get(f'/api/patients/{self.patient_2.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 1)

    def test_admin_can_access_patient_delivery_summary(self):
        """Admin should be able to access any patient's delivery summary"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/patients/{self.patient_1.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 2)

    def test_clinician_can_access_global_delivery_summary(self):
        """Clinician (doctor) should be able to access global delivery summary"""
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get('/api/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_deliveries'], 3)  # all deliveries

    def test_unauthenticated_user_cannot_access_summary(self):
        """Unauthenticated user should not be able to access delivery summary"""
        response = self.client.get(f'/api/patients/{self.patient_1.id}/analytics/deliveries/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
