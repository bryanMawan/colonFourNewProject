from django.test import TestCase, Client
from django.urls import reverse
from ..models import CustomUser, OrganizerProfile
from django.contrib import messages

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colonFourNewProject.settings.py" )

class UserRegistrationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.home_url = reverse('home')
        self.registration_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password1': 'ComplexPassword123',
            'password2': 'ComplexPassword123',
            'gdpr_consented': True
        }

    def test_registration_without_gdpr_consent(self):
        response = self.client.post(self.register_url, {
            'email': 'test@example.com',
            'name': 'Test User',
            'password1': 'ComplexPassword123',
            'password2': 'ComplexPassword123',
            'gdpr_consented': False  # GDPR consent not given
        })
        self.assertNotEqual(CustomUser.objects.count(), 1)

    def test_registration_with_error(self):
        response = self.client.post(self.register_url, {
            'email': 'invalid-email',
            'name': 'Test User',
            'password1': 'ComplexPassword123',
            'password2': 'ComplexPassword123',
            'gdpr_consented': True
        })
        self.assertNotEqual(CustomUser.objects.count(), 1)

    def test_successful_registration_and_redirection(self):
        response = self.client.post(self.register_url, self.registration_data, follow=True)
        self.assertRedirects(response, self.home_url)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(response.context['user'].is_authenticated, True)

    def test_welcome_message_after_registration(self):
        response = self.client.post(self.register_url, self.registration_data, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertTrue("Welcome" in message.message)

    def test_user_and_organizer_profile_details(self):
            # Perform registration
            self.client.post(self.register_url, self.registration_data)

            # Retrieve the created user and organizer profile
            user = CustomUser.objects.get(email='test@example.com')
            organizer_profile = OrganizerProfile.objects.get(user=user)

            # Check that user details match the submitted data
            self.assertEqual(user.email, 'test@example.com')
            self.assertEqual(user.get_full_name(), 'Test User')

            # Assuming you want to check if the gdpr_consented value is stored correctly
            self.assertEqual(organizer_profile.gdpr_consented, self.registration_data['gdpr_consented'])
