from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import CustomUser


class RegistrationTest(APITestCase):
	def test_register_patient_returns_token(self):
		url = reverse('register')
		payload = {
			'username': 'testpatient',
			'email': 'patient@example.com',
			'password': 'StrongPass123!',
			'password2': 'StrongPass123!',
			'role': 'patient',
			'emergency_contact': 'John Doe - +15551234567'
		}

		response = self.client.post(url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('token', response.data)
		self.assertTrue(CustomUser.objects.filter(username='testpatient').exists())
