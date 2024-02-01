from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch  # Import the patch function
from ..models import Dancer
from datetime import datetime, timedelta
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
            'picture': '',
            'styles': 'Hip Hop',
            'dancer_has_consented': True,
        }

        # Capture logs to the console
        with self.assertLogs('newColonFour.views', level='DEBUG') as log_output:
            response = self.client.post(reverse('create_dancer'), data=form_data)

        # Check that the dancer is created in the database
        self.assertEqual(response.status_code, 302)
        dancer = Dancer.objects.get(name='Test Dancer')
        self.assertEqual(dancer.country, 'USA')
        self.assertIn('Hip Hop', dancer.styles)

        # Check log content for console output
        expected_log_message = f'DEBUG:newColonFour.views:User "Test User" created a dancer: "Test Dancer"'
        self.assertIn(expected_log_message, log_output.output)

    def test_create_dancer_rate_limiting(self):
        # Log in the user
        self.client.login(email='testuser@example.com', password='testpassword')

        # Mock datetime to control the passage of time
        with patch('django.utils.timezone.now') as mock_now:
            # Set the initial time
            mock_now.return_value = datetime(2022, 1, 1, 12, 0, 0)

            # Create 14 dancers within a minute
            for i in range(14):
                form_data = {
                    'name': f'TestDancer{i}',
                    'country': 'USA',
                    'picture': '',  # You may need to handle file uploads appropriately
                    'styles': 'Hip Hop',
                    'dancer_has_consented': True,
                }
                response = self.client.post(reverse('create_dancer'), data=form_data)
                self.assertEqual(response.status_code, 302)  # Expect a redirect status code

            # Advance time by 59 seconds
            mock_now.return_value += timedelta(seconds=59)

            # Try to create one more dancer within the same minute
            form_data = {
                'name': 'TestDancer15',
                'country': 'USA',
                'picture': '',
                'styles': 'Hip Hop',
                'dancer_has_consented': True,
            }
            response = self.client.post(reverse('create_dancer'), data=form_data)
            self.assertEqual(response.status_code, 302)  # Expect a redirect status code

            # Advance time by 2 seconds (total elapsed time is now 1 minute)
            mock_now.return_value += timedelta(seconds=2)

            # Try to create one more dancer after a minute
            form_data = {
                'name': 'TestDancer16',
                'country': 'USA',
                'picture': '',
                'styles': 'Hip Hop',
                'dancer_has_consented': True,
            }
        # Capture logs for rate limit exceeded
        with self.assertLogs('newColonFour.views', level='WARNING') as log_output:
            response = self.client.post(reverse('create_dancer'), data=form_data)
            self.assertEqual(response.status_code, 403)  # Expect a forbidden status code

        # Check log content for rate limit exceeded
        expected_log_message = 'WARNING:newColonFour.views:Rate limit exceeded for creating dancers'
        self.assertIn(expected_log_message, log_output.output)

    def tearDown(self):
        # Clean up the log file after the test
        log_file_path = 'colonFourNewProject/logs/newColonFour.log'
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
        
