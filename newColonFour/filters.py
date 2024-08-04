# filters.py
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import Dancer  # Adjust the import path based on your app's structure
import logging

logger = logging.getLogger(__name__)

class EventFilter:
    def __init__(self, queryset):
        self.queryset = queryset

    def apply(self, filters_dict):
        """
        Apply filters based on the filters_dict dictionary.
        """
        logger.debug(f"Applying filters: {filters_dict}")

        filter_methods = {
            "event-type": self.filter_by_event_type,
            "name": self.filter_by_name,
            "date-range": self.filter_by_date_range,
            "level": self.filter_by_level,
            "styles": self.filter_by_styles,
            "weekend-events": self.filter_weekend_events,
            "dancers": self.filter_by_dancers,
        }

        for filter_type, filter_value in filters_dict.items():
            filter_method = filter_methods.get(filter_type)
            if filter_method:
                self.queryset = filter_method(filter_value)
            else:
                logger.warning(f"Ignoring unknown filter type: {filter_type}")

        return self.queryset

    def filter_by_dancers(self, dancer_names):
        """
        Filter queryset by dancers.
        """
        logger.debug(f'Filtering events for dancers: {dancer_names}')
        
        if not dancer_names:
            logger.warning('No dancer names provided for filtering.')
            return self.queryset

        dancer_ids = Dancer.objects.filter(name__in=dancer_names).values_list('id', flat=True)
        if not dancer_ids:
            logger.warning(f'No dancers found for names: {dancer_names}')
            return self.queryset

        logger.debug(f'Found dancer IDs: {dancer_ids}')
        self.queryset = self.queryset.filter(Q(battle__judges__in=dancer_ids) | Q(battle__host__in=dancer_ids)).distinct()

        logger.debug(f'Filtered events: {self.queryset}')
        return self.queryset

    def filter_by_event_type(self, event_types):
        """
        Filter queryset by event types.
        """
        if event_types:
            self.queryset = self.queryset.filter(event_type__in=event_types)
        return self.queryset

    def filter_by_name(self, name_text):
        """
        Filter queryset by event names containing name_text.
        """
        if name_text:
            query = Q()
            for name_part in name_text:
                query |= Q(name__icontains=name_part)
            self.queryset = self.queryset.filter(query)
        return self.queryset

    def filter_by_date_range(self, date_range):
        """
        Filter queryset by date range.
        """
        logger.debug(f"Filtering by date range: {date_range}")

        if not date_range:
            logger.debug("No date range provided. Returning original queryset.")
            return self.queryset

        try:
            start_date, end_date = date_range[0].split(" - ")
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
        except ValueError:
            logger.error("Date range format is incorrect. Expected format: 'YYYY-MM-DD - YYYY-MM-DD'")
            return self.queryset

        if start_date and end_date:
            self.queryset = self.queryset.filter(
                Q(date__range=(start_date, end_date)) |
                Q(end_date__range=(start_date, end_date))
            )
        elif start_date:
            self.queryset = self.queryset.filter(
                Q(date__gte=start_date) |
                Q(end_date__gte=start_date)
            )
        elif end_date:
            self.queryset = self.queryset.filter(
                Q(date__lte=end_date) |
                Q(end_date__lte=end_date)
            )
        return self.queryset

    def filter_by_level(self, levels):
        """
        Filter queryset by levels.
        """
        if levels:
            self.queryset = self.queryset.filter(level__in=levels)
        return self.queryset

    def filter_by_styles(self, styles):
        """
        Filter queryset by styles.
        """
        logger.debug(f"Filtering by styles: {styles}")
        if styles:
            self.queryset = self.queryset.filter(styles__overlap=styles)
            for event in self.queryset:
                logger.debug(f"Event: {event.name}, Styles: {event.styles}")
        return self.queryset

    def filter_weekend_events(self, _):
        """
        Filter queryset to include events that fall on a weekend.
        """
        self.queryset = self.queryset.filter(
            Q(date__week_day__in=[6, 7, 1]) |  # Friday, Saturday, Sunday
            Q(end_date__week_day__in=[6, 7, 1])  # Friday, Saturday, Sunday
        )
        return self.queryset
