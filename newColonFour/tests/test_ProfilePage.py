import os
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone  # Import timezone
from ..models import CustomUser, OrganizerProfile, Event
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colonFourNewProject.settings.py" )

class OrganizerProfilePageTests(TestCase):

    def setUp(self):
        # Create a user and organizer profile
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
        
        # Create events and associate them with the organizer
        for i in range(5):  # Creating 5 events
            event_date = timezone.now()  # Use current time for event date
            Event.objects.create(name=f'Event {i}', date=event_date, location='Location', description='Description', organizer=self.organizer)

        self.client = Client()
        self.url = reverse('organizer-profile-detail', kwargs={'slug': self.organizer.slug})
        self.default_image_url = '/static/images/photoDefault.jpg'

    def test_organizer_profile_page_displays_info(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.organizer.user.get_full_name())
        self.assertContains(response, self.organizer.profile_picture.url if self.organizer.profile_picture else self.default_image_url)
        self.assertContains(response, f'Number of events: {self.organizer.organizer_events.count()}')

        # Check for each event
        for event in self.organizer.organizer_events.all():
            self.assertContains(response, event.name)
