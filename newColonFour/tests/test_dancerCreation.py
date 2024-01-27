from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Dancer
from ..forms import DancerForm
import os

class DancerCreateViewTest(TestCase):
    def setUp(self):
        # Create a user for testing
        form_data = {
            'email': 'testuser@example.com',
            'name': 'Test User',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'gdpr_consented': True
        }
        self.client.post(reverse('register'), form_data)
        self.client.get(reverse('logout'))
        self.client = Client()

    def test_create_dancer_unauthenticated_user_redirects_to_login(self):
        response = self.client.get(reverse('create_dancer'))
        self.assertEqual(response.status_code, 302)  # Expect a redirect status code
        self.assertRedirects(response, f'/login/?next={reverse("create_dancer")}')

    def test_create_dancer_authenticated_user_can_access_page(self):
        # Log in the user
        self.client.login(email='testuser@example.com', password='testpassword')
        
        response = self.client.get(reverse('create_dancer'))
        self.assertEqual(response.status_code, 200)  # Expect a successful response

    def test_create_dancer_form_submission(self):
        # Log in the user
        self.client.login(email='testuser@example.com', password='testpassword')

        # Submit the form data
        form_data = {
            'name': 'Test Dancer',
            'country': 'USA',
            'picture': '',  # You may need to handle file uploads appropriately
            'styles': 'Hip Hop',
            'dancer_has_consented': True,
        }

        response = self.client.post(reverse('create_dancer'), data=form_data)

        # Check that the dancer is created in the database
        self.assertEqual(response.status_code, 302)  # Expect a redirect status code
        dancer = Dancer.objects.get(name='Test Dancer')
        self.assertEqual(dancer.country, 'USA')
        # Ensure the submitted style is in the list of styles
        submitted_style = 'Hip Hop'
        self.assertIn(submitted_style, dancer.styles)
    def test_create_dancer_with_unauthenticated_user_redirects_to_login(self):
        # Log in the user
        self.client.login(email='testuser@example.com', password='testpassword')

        # Log out the user
        self.client.logout()

        # Try to access the dancer creation page again
        response = self.client.get(reverse('create_dancer'))
        self.assertEqual(response.status_code, 302)  # Expect a redirect status code
        self.assertRedirects(response, f'/login/?next={reverse("create_dancer")}')

    def test_create_dancer_logs_created_dancer(self):
        # Log in the user
        self.client.login(email='testuser@example.com', password='testpassword')

        # Submit the form data
        form_data = {
            'name': 'Test Dancer',
            'country': 'USA',
            'picture': '',  # You may need to handle file uploads appropriately
            'styles': 'Hip Hop',  # Assuming styles is a list
            'dancer_has_consented': True,
        }

        # Capture logs using Django's LogCapture
        with self.assertLogs('newColonFour.views', level='DEBUG') as log_output:
            response = self.client.post(reverse('create_dancer'), data=form_data)

        # Check that the dancer is created in the database
        self.assertEqual(response.status_code, 302)  # Expect a redirect status code
        dancer = Dancer.objects.get(name='Test Dancer')
        self.assertEqual(dancer.country, 'USA')

        # Ensure the submitted style is in the list of styles
        submitted_style = 'Hip Hop'
        self.assertIn(submitted_style, dancer.styles)

        # Check log content
        expected_log_message = f'DEBUG:newColonFour.views:User "Test User" created a dancer: "Test Dancer"'
        self.assertIn(expected_log_message, log_output.output)

    def tearDown(self):
        # Clean up the log file after the test
        log_file_path = 'colonFourNewProject/logs/newColonFour.log'
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
