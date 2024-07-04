from .models import Dancer
from django.db.models import Q
from django.db.models import F, ExpressionWrapper, fields
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Event
from .servicesFolder.services import distance_between_cities
import logging

logger = logging.getLogger(__name__)

def get_all_dancers():
    return Dancer.objects.all()

def apply_filter(queryset, filters_dict):
    """
    Apply filters based on the filters_dict dictionary.
    """
    for filter_type, filter_value in filters_dict.items():
        if filter_type == "event-type":
            queryset = filter_by_event_type(queryset, filter_value)
        elif filter_type == "name":
            queryset = filter_by_name(queryset, filter_value)
        elif filter_type == "date-range":
            start_date, end_date = filter_value.split(" - ")
            queryset = filter_by_date_range(queryset, start_date, end_date)
        elif filter_type == "level":
            queryset = filter_by_level(queryset, filter_value)
        elif filter_type == "styles":
            queryset = filter_by_styles(queryset, filter_value)
        elif filter_type == "weekend-events":
            queryset = filter_weekend_events(queryset)
        # Add more elif conditions for other filter types as needed
        else:
            # Handle unknown filter types gracefully
            pass
    return queryset

def filter_by_event_type(queryset, event_types):
    """
    Filter queryset by event types (comma-separated string).
    """
    if event_types:
        return queryset.filter(event_type__in=event_types)
    return queryset

def filter_by_name(queryset, name_text):
    """
    Filter queryset by event names where name_text is a subtext (comma-separated string).
    """
    if name_text:
        query = Q()
        name_parts = [name_part.strip() for name_part in name_text.split(',')]
        for name_part in name_parts:
            query |= Q(name__icontains=name_part)
        return queryset.filter(query)
    return queryset

def filter_by_date_range(queryset, start_date, end_date):
    """
    Filter queryset by date range.
    """
    print("dates: " + start_date + end_date)
    if start_date and end_date:
        
        return queryset.filter(date__range=[start_date, end_date])
    elif start_date:
        return queryset.filter(date__gte=start_date)
    elif end_date:
        return queryset.filter(date__lte=end_date)
    return queryset

def filter_by_level(queryset, levels):
    """
    Filter queryset by levels (comma-separated string).
    """
    if levels:
        return queryset.filter(level__in=levels)
    return queryset

def filter_by_styles(queryset, styles):
    """
    Filter queryset by styles (using overlap, comma-separated string).
    """
    if styles:
        return queryset.filter(styles__overlap=styles)
    return queryset

def filter_weekend_events(queryset):
    """
    Filter events that fall on weekends (Friday, Saturday, or Sunday).
    """
    return queryset.filter(
        Q(date__week_day=6) |  # Friday
        Q(date__week_day=7) |  # Saturday
        Q(date__week_day=1)    # Sunday
    )

def get_sorted_events(search_query, utc_date_str, filters, event_type=None, name=None, start_date=None, end_date=None, level=None, styles=None, order_by_goers=False):
    """
    Get sorted events based on various filters and sorting criteria.
    """
    utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%S.%f%z") if utc_date_str else None
    
    logger.debug(f"UTC date: {utc_date}")
    logger.debug(f"Search query: {search_query}")

    queryset = Event.objects.filter(
        Q(date__gt=utc_date.date()) |
        Q(date=utc_date.date(), start_time__gte=utc_date.time())
    )

    logger.debug(f"Initial queryset count: {queryset.count()}")

    # Iterate over filters dictionary
    logger.debug(f"Applying filter: {filters}")
    queryset = apply_filter(queryset, filters)

    # Optional ordering by number of goers
    if order_by_goers:
        logger.debug("Ordering by number of goers")
        # Uncomment the following line to order by number of goers
        # queryset = queryset.order_by('-number_of_goers')

    events_with_calculations = [
        (
            event,
            event.days_until(utc_date),  # Calculate days until the event
            distance_between_cities(event.get_trimmed_location(), search_query),  # Calculate distance
            event.start_time  # Direct attribute access
        )
        for event in queryset
    ]

    logger.debug(f"Events with calculations count: {len(events_with_calculations)}")

    sorted_events_with_calculations = sorted(events_with_calculations, key=lambda x: (x[2], x[1], x[3]))

    sorted_events = [item[0] for item in sorted_events_with_calculations]

    logger.debug(f"Sorted events count: {len(sorted_events)}")

    return sorted_events

def get_unique_styles():
    """
    Get unique styles from Event model.
    """
    return list(Event.objects.values_list('styles', flat=True).distinct())

def get_unique_event_types():
    """
    Get unique event types from Event model.
    """
    return list(Event.objects.values_list('event_type', flat=True).distinct())

def get_unique_levels():
    """
    Get unique levels from Event model.
    """
    return list(Event.objects.values_list('level', flat=True).distinct())
