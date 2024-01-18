from django.test import TestCase
from django.urls import reverse
from ..models import CustomUser, OrganizerProfile
from ..forms import OrganizerRegistrationForm
from django.contrib.auth import get_user_model
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colonFourNewProject.settings.py" )


class TestCaseUser(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(email='test@example.com', password='testpass123', name='Test User')

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

class TestOrganizerRegistrationForm(TestCase):
    
    def test_form_valid(self):
        form_data = {'email': 'testuser@example.com', 'name': 'Test User', 'password1': 'complexpassword', 'password2': 'complexpassword', 'gdpr_consented': True}
        form = OrganizerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form = OrganizerRegistrationForm(data={})
        self.assertFalse(form.is_valid())

class TestRegisterView(TestCase):

    def test_get_register(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration.html')

    def test_post_register(self):
        response = self.client.post(reverse('register'), {'email': 'newuser@example.com', 'name': 'New User', 'password1': 'newpassword123', 'password2': 'newpassword123', 'gdpr_consented': True})
        self.assertRedirects(response, reverse('home'))

class TestLoginLogout(TestCase):

    def setUp(self):
        form_data = {
            'email': 'user@example.com',
            'name': 'Test User 2',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'gdpr_consented': True
        }
        self.client.post(reverse('register'), form_data)
        self.client.get(reverse('logout'))

        self.user = CustomUser.objects.get(email='user@example.com')

    def test_login(self):
        response = self.client.post(reverse('login'), {'username': 'user@example.com', 'password': 'testpass123'})
        self.assertRedirects(response, reverse('home'))

    def test_logout(self):
        self.client.login(email='user@example.com', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))

class TestAccessControl(TestCase):

    def setUp(self):
        form_data = {
            'email': 'user2@example.com',
            'name': 'Test User 2',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'gdpr_consented': True
        }
        self.client.post(reverse('register'), form_data)

        user = CustomUser.objects.get(email='user2@example.com')
        self.organizer_profile = user.organizerprofile
        self.slug = self.organizer_profile.slug


    def test_organizer_profile_detail_view(self):
        response = self.client.get(reverse('logout'))

        # Use the slug from the organizer_profile created in setUp
        response = self.client.get(reverse('organizer-profile-detail', kwargs={'slug': self.slug}))
        print(self.organizer_profile)
        self.assertEqual(response.status_code, 302)  # Redirects to login page
