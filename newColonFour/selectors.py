from django.db.models import Q
from .models import Dancer, Event, Battle
from .servicesFolder.services import distance_between_cities
import logging
from django.utils import timezone  # Import timezone from django.utils
from django.core.cache import cache
from .filters import EventFilter
from .sorters import sort_events


logger = logging.getLogger(__name__)


def get_all_dancers():
    """
    Retrieve all dancers from the database.
    This is the fastest method using Django's QuerySet methods.
    """
    try:
        dancers = Dancer.objects.all().only('name')  # Retrieve only the necessary fields
        return dancers
    except Exception as e:
        logger.error(f"Error retrieving dancers: {e}")
        return Dancer.objects.none()
    
def get_orphaned_dancers():
    """
    Returns a queryset of dancers who are neither judges nor hosts in any battles.
    """
    return Dancer.objects.filter(
        ~Q(battle_judges__isnull=False) & ~Q(battle_hosts__isnull=False)
    ).distinct()

def get_past_events():
    """
    Returns a queryset of events that have ended.
    """
    # Get the current time
    now = timezone.now()
    
    # Filter events that have ended
    return Event.objects.filter(end_date__lt=now)


def get_sorted_events(search_query, filters, order_by='distance-a'):
    """
    Get sorted events based on various filters and sorting criteria.

    :param search_query: Search query string.
    :param utc_date_str: UTC date string.
    :param filters: Dictionary of filters.
    :param order_by: Sorting criteria. Can be 'distance-a', 'distance-d', 'soonest-a', 'soonest-d', 'goers-a', 'goers-d'.
    :return: Sorted list of events.
    """
    utc_date = timezone.now()  # Use the current UTC time instead of parsing from a string
    
    logger.debug(f"UTC date: {utc_date}")
    logger.debug(f"Search query: {search_query}")

    queryset = Event.objects.filter(
        Q(end_date__gt=utc_date.date()) |
        Q(end_date=utc_date.date(), start_time__gte=utc_date.time())
    )

    logger.debug(f"Initial queryset count: {queryset.count()}")

    # Instantiate the EventFilter class
    event_filter = EventFilter(queryset)

    logger.debug(f"Applying filter: {filters}")

    # Apply filters using the EventFilter class
    queryset = event_filter.apply(filters)

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


def get_unique_styles():
    """
    Get unique styles from Event model with caching.
    """
    cache_key = 'unique_styles'
    unique_styles = cache.get(cache_key)
    
    if unique_styles is None:
        styles_lists = list(Event.objects.values_list('styles', flat=True).distinct())
        unique_styles_set = {item for sublist in styles_lists for item in sublist if item}
        unique_styles = list(unique_styles_set)
        cache.set(cache_key, unique_styles, timeout=3600)  # Cache for 1 hour
        print(f"Cache miss for unique styles. Retrieved and cached: {unique_styles}")
    else:
        print(f"Cache hit for unique styles: {unique_styles}")
    
    return unique_styles


def get_unique_event_types():
    """
    Get unique event types from Event model with caching.
    """
    cache_key = 'unique_event_types'
    unique_event_types = cache.get(cache_key)
    
    if unique_event_types is None:
        unique_event_types = list(Event.objects.values_list('event_type', flat=True).distinct())
        cache.set(cache_key, unique_event_types, timeout=3600)  # Cache for 1 hour
        print(f"Cache miss for unique event types. Retrieved and cached: {unique_event_types}")
    else:
        print(f"Cache hit for unique event types: {unique_event_types}")
    
    return unique_event_types


def get_unique_levels():
    """
    Get unique levels from Event model with caching.
    """
    cache_key = 'unique_levels'
    unique_levels = cache.get(cache_key)
    
    if unique_levels is None:
        unique_levels = list(Event.objects.values_list('level', flat=True).distinct())
        cache.set(cache_key, unique_levels, timeout=3600)  # Cache for 1 hour
        print(f"Cache miss for unique levels. Retrieved and cached: {unique_levels}")
    else:
        print(f"Cache hit for unique levels: {unique_levels}")
    
    return unique_levels


def get_dancers_info(event):
    """
    Get dancers information for a specific event with caching.
    """
    cache_key = f'dancers_info_{event.id}'
    dancers_info = cache.get(cache_key)
    
    if dancers_info is None:
        dancers_info = []

        if event.event_type == Event.BATTLE:
            print(f'Event {event} is a Battle. Retrieving host and judges.')

            try:
                battle_event = Battle.objects.get(id=event.id)
                print(f'Battle event found: {battle_event}')
            except Battle.DoesNotExist:
                print(f'Battle event with id {event.id} does not exist.')
                return []

            host = battle_event.host.all()

            if host:
                print(f'Hosts found: {host}')
                for each_host in host:
                    host_info = {
                        'name': each_host.name,
                        'image_url': each_host.picture.url if each_host.picture else '',
                        'country': each_host.country,
                        'role': 'Host', 
                        'instagram_url': each_host.instagram_url
                    }
                    dancers_info.append(host_info)
            else:
                print('No host found for this battle event.')

            judges = battle_event.judges.all()
            if judges:
                print(f'Judges found: {judges}')
                for judge in judges:
                    judge_info = {
                        'name': judge.name,
                        'image_url': judge.picture.url if judge.picture else '',
                        'country': judge.country,
                        'role': 'Judge',
                        'instagram_url': judge.instagram_url
                    }
                    dancers_info.append(judge_info)
            else:
                print('No judges found for this battle event.')
        else:
            print(f'Event {event} is not a Battle (type: {event.event_type}). Returning empty dancers info.')
            return []

        for dancer in event.dancers.all():
            dancer_info = {
                'name': dancer.name,
                'image_url': dancer.picture.url if dancer.picture else '',
                'country': dancer.country,
                'role': 'Dancer',
                'instagram_url': dancer.instagram_url
            }
            dancers_info.append(dancer_info)

        print('Dancers Info:', dancers_info)
        cache.set(cache_key, dancers_info, timeout=3600)  # Cache for 1 hour
        print(f"Cache miss for dancers info. Retrieved and cached: {dancers_info}")
    else:
        print(f"Cache hit for dancers info: {dancers_info}")
    
    return dancers_info


 # gpt: CACHE THISSSS
def get_event_styles(event):
    """
    Fetch the styles associated with a given event.

    :param event: The event instance to retrieve styles from.
    :return: A list of styles associated with the event.
    """
    styles = event.styles.all()  # Assuming styles is a ManyToManyField
    styles_list = [style.name for style in styles]  # Extract style names
    logger.debug(f"Fetched styles for event {event.name}: {styles_list}")
    return styles_list


