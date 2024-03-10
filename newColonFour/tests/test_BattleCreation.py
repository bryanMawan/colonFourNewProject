from django.test import TestCase
from django.urls import reverse
from ..models import Battle, OrganizerProfile, CustomUser
from ..forms import BattleForm
from ..servicesFolder.services import set_battle_organizer

class BattleCreateViewTest(TestCase):
    def setUp(self):
        form_data = {
            'email': 'test@example.com',
            'name': 'Test User 2',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'gdpr_consented': True
        }
        self.client.post(reverse('register'), form_data)
        self.client.get(reverse('logout'))

        self.user = CustomUser.objects.get(email='test@example.com')
        self.organizer = self.user.organizerprofile  # Assuming the related name is 'organizerprofile'
        

    def test_battle_creation_unauthenticated_user_redirects_to_login(self):
        self.client.logout()  # Ensure the user is logged out
        response = self.client.get(reverse('create_battle'))
        self.assertEqual(response.status_code, 302)  # Check for redirection
        self.assertTrue(response.url.startswith('/login/'))  # Ensure redirection to login page

    def test_battle_creation_authenticated_user_can_access_page(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('create_battle'))
        self.assertEqual(response.status_code, 200)  # Authenticated user should access the page

    def test_battle_form_submission(self):
        self.client.login(email='test@example.com', password='testpass123')

        # Simulated form data
        form_data = {
            'name': 'Test Battle',
            'date': '2024-01-01',
            'location': 'Test Location',
            'description': 'Test Description',
            'start_time': '10:00',
            'end_time': '12:00',
            'styles': ['popping'],
            'level': 'Open',
            'type': '1vs1',
        }

        # Instantiate the form with the data
        form = BattleForm(data=form_data)
        
        # Validate the form
        self.assertTrue(form.is_valid())

        # Save the form to create a Battle instance
        battle_instance = form.save(commit=False)
        battle_instance = set_battle_organizer(battle_instance, self.user)  # Manually assign the organizer
        battle_instance.save()
        form.save_m2m()  # Save many-to-many data

        # Retrieve the saved instance
        saved_instance = Battle.objects.get(name='Test Battle')
        
        # Assert that the saved instance data matches the form data
        self.assertEqual(saved_instance.name, form_data['name'])
        self.assertEqual(saved_instance.location, form_data['location'])
        self.assertEqual(saved_instance.description, form_data['description'])
        self.assertEqual(saved_instance.level, form_data['level'])
        self.assertEqual(saved_instance.type, form_data['type'])

    def test_create_battle_logs_created_battle(self):
        # Log in the user
        self.client.login(email='test@example.com', password='testpass123')

        # Submit the form data for creating a battle
        form_data = {
            'name': 'Epic Battle',
            'date': '2024-01-01',
            'location': 'Test Arena',
            'description': 'A showdown of epic proportions.',
            'start_time': '15:00',
            'end_time': '17:00',
            'styles': ['Breaking'],
            'level': 'Open',
            'type': 'Crew vs Crew',
            # Add any other required fields for the battle creation
        }

        # Capture logs to the console
        with self.assertLogs('newColonFour.views', level='DEBUG') as log_output:
            response = self.client.post(reverse('create_battle'), data=form_data)

        # Check that the battle is created in the database
        self.assertEqual(response.status_code, 302)  # Assuming you're redirecting after successful creation
        battle = Battle.objects.get(name='Epic Battle')
        self.assertEqual(battle.location, 'Test Arena')
        self.assertEqual(battle.description, 'A showdown of epic proportions.')

        # Check log content for the expected output
        expected_log_message = f'DEBUG:newColonFour.views:User "{self.user.get_full_name()}" created a battle: "Epic Battle"'
        self.assertTrue(any(expected_log_message in message for message in log_output.output),
                        "The expected log message was not found in the output.")
