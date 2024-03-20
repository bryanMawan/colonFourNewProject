document.addEventListener('DOMContentLoaded', function() {
    let lastTouchTime = 0;
    let touchDurationTimer;
    let lastTouchType = ''; // Track the type of the last touch (single or double)

    function onDoubleTap(event) {
        event.preventDefault(); // Prevent default to disable double click to zoom for mobile devices
        const now = Date.now();
        const timeSinceLastTouch = now - lastTouchTime;
        const touchType = event.touches.length === 2 ? 'double' : 'single';

        if (timeSinceLastTouch < 300 && timeSinceLastTouch > 0) {
            // Distinguish between single and double finger double taps
            if (touchType === 'single' && lastTouchType === 'single') {
                // Single-finger double tap
                showModal('goingModal');
            } else if (touchType === 'double' && lastTouchType === 'double') {
                // Two-finger double tap
                showModal('filtersModal');
            }
        }

        lastTouchTime = now;
        lastTouchType = touchType; // Update the last touch type
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

    function showModal(modalId) {
        // Assuming you have a modal with an id of modalId
        $('#' + modalId).modal('show'); // This example uses Bootstrap's modal, adjust accordingly if you're using something else
    }

    // Add touch event listeners to each event card
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('touchend', onDoubleTap);
        card.addEventListener('touchstart', onLongPressStart);
        card.addEventListener('touchend', onLongPressEnd);
        card.addEventListener('touchcancel', onLongPressEnd); // Handle case where the touch is cancelled
    });
});
