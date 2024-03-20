document.addEventListener('DOMContentLoaded', function() {
    let lastTouchTime = 0;
    let touchDurationTimer;
    let twoFingerTouchTimer; // Timer for two finger touch

    function onDoubleTap(event) {
        event.preventDefault();
        const now = Date.now();
        const timeSinceLastTouch = now - lastTouchTime;

        if (timeSinceLastTouch < 300 && timeSinceLastTouch > 0) {
            showModal('goingModal');
        }

        lastTouchTime = now;
    }

    function onLongPressStart(event) {
        if(event.touches.length === 1) { // Ensure single touch for long press
            touchDurationTimer = setTimeout(() => {
                showModal('detailsModal');
            }, 500);
        }
    }

    function onLongPressEnd(event) {
        clearTimeout(touchDurationTimer);
    }

    function twoFingerLongPressStart(event) {
        if (event.touches.length === 2) { // Check for two finger touch
            twoFingerTouchTimer = setTimeout(() => {
                showModal('filtersModal');
            }, 500);
        }
    }

    function twoFingerLongPressEnd(event) {
        clearTimeout(twoFingerTouchTimer);
    }

    function showModal(modalId) {
        $('#' + modalId).modal('show');
    }

    // Add touch event listeners to each event card
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('touchend', onDoubleTap);
        card.addEventListener('touchstart', onLongPressStart);
        card.addEventListener('touchend', onLongPressEnd);
        card.addEventListener('touchcancel', onLongPressEnd);
        // Two-finger long press listeners
        card.addEventListener('touchstart', twoFingerLongPressStart);
        card.addEventListener('touchend', twoFingerLongPressEnd);
        card.addEventListener('touchcancel', twoFingerLongPressEnd);
    });
});
