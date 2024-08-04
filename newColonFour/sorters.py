import logging

logger = logging.getLogger(__name__)

def sort_by_distance(event):
    """
    Sort key for distance-based sorting.
    """
    return (event[2], event[1], event[3], -event[4])

def sort_by_soonest(event):
    """
    Sort key for soonest-based sorting.
    """
    return (event[1], event[2], event[3], -event[4])

def sort_by_goers(event):
    """
    Sort key for goers-based sorting.
    """
    return (-event[4], event[2], event[1], event[3])

def sort_events(events_with_calculations, order_by):
    """
    Sort events based on calculated details.

    :param events_with_calculations: List of events with calculated details.
    :param order_by: Sorting criteria. Can be 'distance-a', 'soonest-a', 'goers-a'.
    :return: Sorted list of events.
    """
    
    if order_by.startswith('distance-a'):
        sort_key = sort_by_distance
    elif order_by.startswith('soonest-a'):
        sort_key = sort_by_soonest
    elif order_by.startswith('goers-a'):
        sort_key = sort_by_goers
    else:
        # Default to distance if no valid order_by criteria is provided
        sort_key = sort_by_distance
    
    # Perform sorting in ascending order
    sorted_events_with_calculations = sorted(events_with_calculations, key=sort_key)

    # Debug prints to visualize the sorted events
    logger.debug(f"Sorting events by {order_by.split('-')[0]} in ascending order:")
    for event in sorted_events_with_calculations:
        logger.debug(f"Event: {event[0].name}, "
                     f"Distance: {event[2]}, Days Until: {event[1]}, Start Time: {event[3]}, Goers Count: {event[4]}")

    # Extract and return the sorted events
    sorted_events = [item[0] for item in sorted_events_with_calculations]
    logger.debug(f"Sorted events count: {len(sorted_events)}")
    return sorted_events