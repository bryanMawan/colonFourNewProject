from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import now
from ..models import Event
from ..views import SearchHomePage

class SearchHomePageTest(TestCase):
    def setUp(self):
        # Setup request factory to create mock requests
        self.factory = RequestFactory()
        
        # Create test events
        Event.objects.create(name="Event in Paris", location="Paris, France", start_time=now())
        Event.objects.create(name="Event in New York", location="New York, USA", start_time=now())
        # Add more events as needed

    def test_search_home_page_with_default_query(self):
        # Create a request with a default search query (i.e., 'Paris, France')
        request = self.factory.get(reverse('search_home'), {'searchQuery': 'Paris, France'})
        
        # Instantiate the View
        view = SearchHomePage()
        view.setup(request)

        # Get the queryset
        queryset = view.get_queryset()
        
        # Assuming your sorting logic is correct, validate the queryset
        # For example, check if "Event in Paris" is in queryset and comes before "Event in New York"
        self.assertIn(Event.objects.get(name="Event in Paris"), queryset)
        # Add more assertions based on your specific sorting and filtering logic

    def test_search_home_page_with_specific_date(self):
        # Create a request with a specific UTC date string
        request = self.factory.get(reverse('search_home'), {'utc-date': '2024-01-01T00:00:00Z'})
        
        # Instantiate and setup the View
        view = SearchHomePage()
        view.setup(request)

        # Get the queryset
        queryset = view.get_queryset()

        # Validate the queryset based on the specific date
        # This requires your events to have varying start times to test effectively
        # Add assertions to validate the sorting based on the specific date
