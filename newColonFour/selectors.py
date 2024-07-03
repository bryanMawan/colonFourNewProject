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

def filter_by_event_type(queryset, event_type):
    if event_type:
        return queryset.filter(event_type=event_type)
    return queryset

def filter_by_name(queryset, name):
    if name:
        return queryset.filter(name__icontains=name)
    return queryset

def filter_by_date_range(queryset, start_date, end_date):
    if start_date and end_date:
        return queryset.filter(date__range=[start_date, end_date])
    elif start_date:
        return queryset.filter(date__gte=start_date)
    elif end_date:
        return queryset.filter(date__lte=end_date)
    return queryset

def filter_by_level(queryset, level):
    if level:
        return queryset.filter(level=level)
    return queryset

def filter_by_styles(queryset, styles):
    if styles:
        return queryset.filter(styles__overlap=styles)
    return queryset

def filter_weekend_events(queryset):
    # Filter events that fall on weekends (Friday, Saturday, or Sunday)
    return queryset.filter(
        Q(date__week_day=6) |  # Friday
        Q(date__week_day=7) |  # Saturday
        Q(date__week_day=1)    # Sunday
    )

def get_sorted_events(search_query, utc_date_str, filters, event_type=None, name=None, start_date=None, end_date=None, level=None, styles=None, order_by_goers=False):
    # Parse the UTC date string
    utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%S.%f%z") if utc_date_str else None

    # Initialize base queryset with date filter
    queryset = Event.objects.filter(
        Q(date__gt=utc_date.date()) | 
        Q(date=utc_date.date(), start_time__gte=utc_date.time())
    )

    print(f"Initial queryset count: {queryset.count()}")

    for filter in filters:
        key, value = filter.split(": ")
        if key == "format":
            queryset = queryset.filter(format=value)
        elif key == "event-type":
            queryset = queryset.filter(event_type=value)
        elif key == "level":
            queryset = queryset.filter(level=value)
        elif key == "date-range":
            start_date, end_date = value.split(" - ")
            queryset = queryset.filter(date__range=[start_date, end_date])

    # Optional ordering by number of goers
    if order_by_goers:
        print("todo")
        # Uncomment the following line to order by number of goers
        # queryset = queryset.order_by('-number_of_goers')

    # Step 2: Calculate Days Until, Distances, and prepare for sorting
    events_with_calculations = [
        (
            event,
            event.days_until(utc_date),  # Calculate days until the event
            distance_between_cities(event.get_trimmed_location(), search_query),  # Calculate distance
            event.start_time  # No calculation needed, direct attribute
        )
        for event in queryset
    ]

    print(f"Events with calculations count: {len(events_with_calculations)}")

    # Step 3: Sort Events by days_until, distance, and then start_time
    sorted_events_with_calculations = sorted(events_with_calculations, key=lambda x: (x[2], x[1], x[3]))

    # Extract sorted events
    sorted_events = [item[0] for item in sorted_events_with_calculations]

    print(f"Sorted events count: {len(sorted_events)}")

    return sorted_events

def get_unique_styles():
    return list(Event.objects.values_list('styles', flat=True).distinct())

def get_unique_event_types():
    return list(Event.objects.values_list('event_type', flat=True).distinct())

def get_unique_levels():
    return list(Event.objects.values_list('level', flat=True).distinct())
