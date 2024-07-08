document.addEventListener("DOMContentLoaded", function() {
    // Initialize the event handling
    initializeScrollEvent();
    updateScale(); // Run initially to scale the card in the center when the page loads
    console.debug('DOMContentLoaded: Event listener for scroll initialized.');
});

/**
 * Initialize scroll event listener with debouncing.
 */
function initializeScrollEvent() {
    const container = document.querySelector('.scroll-container');
    const debouncedUpdateScale = debounce(updateScale, 22);
    container.addEventListener('scroll', debouncedUpdateScale);
}

/**
 * Debounce function to limit how often a function is executed.
 * @param {Function} func - The function to debounce.
 * @param {number} wait - The wait time in milliseconds.
 * @param {boolean} immediate - Whether to execute the function immediately.
 * @returns {Function} - The debounced function.
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Find the card that is most centered in the container.
 * @returns {HTMLElement} - The center most card element.
 */
function findCenterMostCard() {
    const container = document.querySelector('.scroll-container');
    const cards = document.querySelectorAll('.card');
    let centerMostCard = null;
    let minDistanceToCenter = Infinity;

    const containerRect = container.getBoundingClientRect();
    const containerCenter = containerRect.left + containerRect.width / 2;

    cards.forEach(card => {
        const cardRect = card.getBoundingClientRect();
        const cardCenter = cardRect.left + cardRect.width / 2;
        const distanceToCenter = Math.abs(containerCenter - cardCenter);

        if (distanceToCenter < minDistanceToCenter) {
            centerMostCard = card;
            minDistanceToCenter = distanceToCenter;
        }
    });

    return centerMostCard;
}

/**
 * Update the scale of cards and modify related elements based on the center most card.
 */
function updateScale() {
    const centerMostCard = findCenterMostCard();
    const viewEventBtn = document.getElementById('view-event-btn');
    const eventDateDisplay = document.querySelector('#eventDateDisplay span');
    const eventLocationDisplay = document.querySelector('#eventLocationDisplay span');
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        if (card === centerMostCard) {
            updateCardScale(card, eventDateDisplay, eventLocationDisplay, viewEventBtn);
        } else {
            card.classList.remove('scale-up');
        }
    });
}

/**
 * Update the scale of a specific card and related elements.
 * @param {HTMLElement} card - The card element to update.
 * @param {HTMLElement} eventDateDisplay - The event date display element.
 * @param {HTMLElement} eventLocationDisplay - The event location display element.
 * @param {HTMLElement} viewEventBtn - The view event button element.
 */
function updateCardScale(card, eventDateDisplay, eventLocationDisplay, viewEventBtn) {
    card.classList.add('scale-up');
    // Directly access data attributes
    eventDateDisplay.textContent = card.getAttribute('data-event-date');
    eventLocationDisplay.textContent = card.getAttribute('data-event-location');
    // Update hidden input with event ID
    const eventId = card.getAttribute('data-event-id');
    document.getElementById('lastCentermostEventId').value = eventId;

    // Update the data-bs-target based on event type
    const eventTypeBadge = card.querySelector('.badge-type');
    if (eventTypeBadge) {
        const eventType = cleanEventType(eventTypeBadge.textContent);
        const target = getOffcanvasTarget(eventType);
        viewEventBtn.setAttribute('data-bs-target', target);
        console.debug(`Updated data-bs-target to ${target} for event type: ${eventType}`);
    } else {
        console.error('Event type badge not found in the card.');
    }
}

/**
 * Clean and extract the first word of the event type.
 * @param {string} eventType - The raw event type string.
 * @returns {string} - The cleaned event type.
 */
function cleanEventType(eventType) {
    return eventType.replace(/\s+/g, ' ').trim().split(' ')[0];
}

/**
 * Get the offcanvas target based on event type.
 * @param {string} eventType - The event type.
 * @returns {string} - The corresponding offcanvas target.
 */
function getOffcanvasTarget(eventType) {
    // Define mapping of event types to their respective offcanvas targets
    const offcanvasTargets = {
        'Type1': '#target1',
        'Type2': '#target2',
        'Battle': '#battleoffcanvas', // Example of mapping for 'Battle'
        // Add more mappings as needed
    };

    return offcanvasTargets[eventType] || '#defaultTarget';
}
