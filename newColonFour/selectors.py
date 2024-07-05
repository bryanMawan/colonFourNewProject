from datetime import datetime
from django.db.models import Q, Count
from .models import Dancer, Event
from .servicesFolder.services import distance_between_cities
import logging

logger = logging.getLogger(__name__)

def get_all_dancers():
    """
    Retrieve all dancers from the database.
    """
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
            # INDEX 0 FOR THE ONLY DATE RANGE IN THE LIST
            start_date, end_date = filter_value[0].split(" - ")
            queryset = filter_by_date_range(queryset, start_date, end_date)
        elif filter_type == "level":
            queryset = filter_by_level(queryset, filter_value)
        elif filter_type == "styles":
            queryset = filter_by_styles(queryset, filter_value)
        elif filter_type == "weekend-events":
            queryset = filter_weekend_events(queryset)
        else:
            logger.warning(f"Ignoring unknown filter type: {filter_type}")
    return queryset

def filter_by_event_type(queryset, event_types):
    """
    Filter queryset by event types.
    """
    if event_types:
        return queryset.filter(event_type__in=event_types)
    return queryset

def filter_by_name(queryset, name_text):
    """
    Filter queryset by event names containing name_text.
    """

    if name_text:
        query = Q()
        for name_part in name_text:
            query |= Q(name__icontains=name_part)
        return queryset.filter(query)
    return queryset

def filter_by_date_range(queryset, start_date, end_date):
    """
    Filter queryset by date range.
    """
    logger.debug(f"Filtering by date range: {start_date} - {end_date}")
    if start_date and end_date:
        return queryset.filter(date__range=[start_date, end_date])
    elif start_date:
        return queryset.filter(date__gte=start_date)
    elif end_date:
        return queryset.filter(date__lte=end_date)
    return queryset

def filter_by_level(queryset, levels):
    """
    Filter queryset by levels.
    """
    if levels:
        return queryset.filter(level__in=levels)
    return queryset

def filter_by_styles(queryset, styles):
    """
    Filter queryset by styles.
    
    :param queryset: Initial queryset of events.
    :param styles: List of styles to filter by.
    :return: Filtered queryset.
    """
    if styles:
        # Debug: Print event name and its styles for verification
        for event in queryset.filter(styles__overlap=styles):
            logger.debug(f"Event: {event.name}, Styles: {event.styles}")
        return queryset.filter(styles__overlap=styles)
    return queryset

def filter_weekend_events(queryset):
    """
    Filter queryset to include only weekend events.
    """
    return queryset.filter(
        Q(date__week_day=6) |  # Friday
        Q(date__week_day=7) |  # Saturday
        Q(date__week_day=1)    # Sunday
    )

def get_sorted_events(search_query, utc_date_str, filters, order_by='distance-a'):
    """
    Get sorted events based on various filters and sorting criteria.

    :param search_query: Search query string.
    :param utc_date_str: UTC date string.
    :param filters: Dictionary of filters.
    :param order_by: Sorting criteria. Can be 'distance-a', 'distance-d', 'soonest-a', 'soonest-d', 'goers-a', 'goers-d'.
    :return: Sorted list of events.
    """
    utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%S.%f%z") if utc_date_str else None
    
    logger.debug(f"UTC date: {utc_date}")
    logger.debug(f"Search query: {search_query}")

    queryset = Event.objects.filter(
        Q(date__gt=utc_date.date()) |
        Q(date=utc_date.date(), start_time__gte=utc_date.time())
    )

    logger.debug(f"Initial queryset count: {queryset.count()}")

    logger.debug(f"Applying filter: {filters}")
    queryset = apply_filter(queryset, filters)

    events_with_calculations = calculate_event_details(queryset, search_query, utc_date)

    sorted_events = sort_events(events_with_calculations, order_by)

    return sorted_events


def calculate_event_details(queryset, search_query, utc_date):
    """
    Calculate additional event details for sorting.
    """
    events_with_calculations = [
        (
            event,
            event.days_until(utc_date),  # Calculate days until the event
            distance_between_cities(event.get_trimmed_location(), search_query),  # Calculate distance
            event.start_time,  # Direct attribute access
            event.number_of_goings  # Include number of goers
        )
        for event in queryset
    ]

    logger.debug(f"Events with calculations count: {len(events_with_calculations)}")
    return events_with_calculations


def sort_events(events_with_calculations, order_by):
    """
    Sort events based on calculated details.

    :param events_with_calculations: List of events with calculated details.
    :param order_by: Sorting criteria. Can be 'distance-a', 'distance-d', 'soonest-a', 'soonest-d', 'goers-a', 'goers-d'.
    :return: Sorted list of events.
    """
    ascending = order_by.endswith('-a')
    key = None

    if order_by.startswith('distance'):
        key = lambda x: (x[2], x[1], x[3])
    elif order_by.startswith('soonest'):
        key = lambda x: (x[1], x[2], x[3])
    elif order_by.startswith('goers'):
        key = lambda x: (x[4], x[1], x[2], x[3])
    else:
        logger.warning(f"Unknown order_by value: {order_by}, defaulting to 'distance-a'")
        key = lambda x: (x[2], x[1], x[3])
        ascending = True

    sorted_events_with_calculations = sorted(events_with_calculations, key=key, reverse=not ascending)

    # Debug prints to visualize the order
    if order_by.startswith('distance'):
        logger.debug("Sorting events by distance:")
        for event in sorted_events_with_calculations:
            logger.debug(f"Event: {event[0].name}, Distance: {event[2]}, Days Until: {event[1]}, Start Time: {event[3]}")
    elif order_by.startswith('soonest'):
        logger.debug("Sorting events by soonest:")
        for event in sorted_events_with_calculations:
            logger.debug(f"Event: {event[0].name}, Days Until: {event[1]}, Distance: {event[2]}, Start Time: {event[3]}")
    elif order_by.startswith('goers'):
        logger.debug("Sorting events by popularity (number of goers):")
        for event in sorted_events_with_calculations:
            logger.debug(f"Event: {event[0].name}, Goers Count: {event[4]}, Days Until: {event[1]}, Distance: {event[2]}, Start Time: {event[3]}")

    sorted_events = [item[0] for item in sorted_events_with_calculations]
    logger.debug(f"Sorted events count: {len(sorted_events)}")
    return sorted_events



def get_unique_styles():
    """
    Get unique styles from Event model.
    """
    styles_lists = list(Event.objects.values_list('styles', flat=True).distinct())   

    # Flatten the list and remove empty lists
    # Using a set comprehension to flatten the list and normalize to lower case in one step
    unique_styles_set = {item.lower() for sublist in styles_lists for item in sublist}
    
    return list(unique_styles_set)

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
