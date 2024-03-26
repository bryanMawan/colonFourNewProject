document.addEventListener('DOMContentLoaded', function() {
    let lastTouchTime = 0;
    let touchDurationTimer;

    function onDoubleTap(event, eventId) {
        event.preventDefault(); // Prevent default to disable double click to zoom for mobile devices
        const now = Date.now();
        const timeSinceLastTouch = now - lastTouchTime;

        console.log("DT this is event id: " + eventId)
        document.getElementById('current-event-id').value = eventId;

    
        if (timeSinceLastTouch < 300 && timeSinceLastTouch > 0) {
            showModal('goingModal', eventId);
        }
    
        lastTouchTime = now;
    }

    function onLongPressStart(event) {
        // Start a timer to detect long press
        touchDurationTimer = setTimeout(() => {
            showModal('detailsModal');
        }, 500); // Trigger after 500 milliseconds
    }

    function onLongPressEnd(event) {
        // If the touch ends before 500ms, clear the timer
        clearTimeout(touchDurationTimer);
    }

    function showModal(modalId, eventId) {
        // Assuming you have a modal with an id of modalId
        if (eventId !== null) {
            document.getElementById('current-event-id').value = eventId;
        }
        $('#' + modalId).modal('show'); // This example uses Bootstrap's modal, adjust accordingly if you're using something else
    }

    // Add touch event listeners to each event card
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('touchend', function(event) {
            onDoubleTap(event, card.getAttribute('data-event-id'));
        });        
        card.addEventListener('touchstart', onLongPressStart);
        card.addEventListener('touchend', onLongPressEnd);
        card.addEventListener('touchcancel', onLongPressEnd); // Handle case where the touch is cancelled
    });
});
