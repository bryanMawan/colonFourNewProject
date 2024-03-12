from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import make_aware
from datetime import datetime
from ..models import Event, CustomUser
from ..forms import BattleForm  # Assuming you have this form for event creation
from ..views import SearchHomePage
from ..servicesFolder.services import update_event_location_point, set_battle_organizer

class SearchHomePageTest(TestCase):
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

        self.factory = RequestFactory()
        
        # Define your events here
        self.events_data = [
            {"name": "City Dance Festival", "date": "2024-04-15", "location": "10 Downing Street, London, UK", "start_time": "14:00", "address": "10 Downing Street, London, UK"},
            {"name": "Urban Dance Competition", "date": "2024-04-15", "location": "5 Av. Anatole France, Paris, France", "start_time": "18:00", "address": "5 Av. Anatole France, Paris, France"},
            {"name": "Breakdance Battle Royale", "date": "2024-04-15", "location": "5 Platz der Deutschen Einheit, Berlin, Germany", "start_time": "16:00", "address": "5 Platz der Deutschen Einheit, Berlin, Germany"},
            {"name": "Street Dance Showdown", "date": "2024-04-16", "location": "1 Infinite Loop, Cupertino, USA", "start_time": "19:00", "address": "1 Infinite Loop, Cupertino, USA"},
            {"name": "Rhythm and Flow Dance Night", "date": "2024-04-14", "location": "7 Chome-1-2 Nishishinjuku, Tokyo, Japan", "start_time": "20:00", "address": "7 Chome-1-2 Nishishinjuku, Tokyo, Japan"},
        ]

        for event_data in self.events_data:
            self.create_battle_event(event_data)

    def create_battle_event(self, event_data):
        # Adjust this method to fit how your BattleForm and models are defined
        form_data = {
            'name': event_data['name'],
            'date': event_data['date'],
            'location': event_data['location'],
            'description': 'A dance event',
            'start_time': event_data['start_time'],
            'end_time': '22:00',  # Assuming an end time
            'styles': ['popping'],  # Assuming a style
            'level': 'Open',
            'type': '1vs1',
        }

        form = BattleForm(data=form_data)  # Assuming your form needs a user
        if form.is_valid():
            battle_instance = form.save(commit=False)
            battle_instance = set_battle_organizer(battle_instance, self.user)  # Manually assign the organizer
            update_event_location_point(battle_instance)
            battle_instance.save()
            form.save_m2m()  # If there are many-to-many fields to save
        else:
            print(form.errors)  # Log form errors to understand what went wrong

    def test_event_ordering(self):
        request = self.factory.get(reverse('home'))  # Assume this is your search page URL
        view = SearchHomePage()
        view.setup(request)
        queryset = view.get_queryset()

        expected_order_names = [
            "Rhythm and Flow Dance Night",
            "Urban Dance Competition",
            "City Dance Festival",
            "Breakdance Battle Royale",
            "Street Dance Showdown",
        ]
        
        queryset_order_names = [event.name for event in queryset]
        self.assertEqual(queryset_order_names, expected_order_names)
