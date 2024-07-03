# selectors.py
from .models import Dancer
from django.db.models import Q
from django.db.models import F, ExpressionWrapper, fields
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Event
from .servicesFolder.services import distance_between_cities

def get_all_dancers():
    return Dancer.objects.all()

def get_sorted_events(search_query, utc_date_str):

    # Parse the UTC date string
    utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%S.%f%z") if utc_date_str else None


    # Filter events on or after the specified date and time(add filter to omit hidden events)
    events = Event.objects.filter(
        Q(date__gt=utc_date.date()) | 
        Q(date=utc_date.date(), start_time__gte=utc_date.time())
    )

    # Step 2: Calculate Days Until, Distances, and prepare for sorting
    events_with_calculations = [
        (
            event,
            event.days_until(utc_date),  # Calculate days until the event
            distance_between_cities(event.get_trimmed_location(), search_query),  # Calculate distance
            event.start_time  # No calculation needed, direct attribute
        )
        for event in events
    ]
     
    
    # Step 3: Sort Events by days_until, distance, and then start_time
    sorted_events_with_calculations = sorted(events_with_calculations, key=lambda x: (x[2], x[1], x[3]))

    # Extract sorted events
    sorted_events = [item[0] for item in sorted_events_with_calculations]

    return sorted_events

def get_unique_styles():
    return list(Event.objects.values_list('styles', flat=True).distinct())

def get_unique_event_types():
    return list(Event.objects.values_list('event_type', flat=True).distinct())

def get_unique_levels():
    return list(Event.objects.values_list('level', flat=True).distinct())
