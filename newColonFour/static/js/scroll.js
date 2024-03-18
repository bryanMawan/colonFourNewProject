document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector('.scroll-container');
    const cards = document.querySelectorAll('.card');
    const eventDateDisplay = document.querySelector('#eventDateDisplay span');
    const eventLocationDisplay = document.querySelector('#eventLocationDisplay span');

    // Debounce function to limit how often a function is executed
    function debounce(func, wait, immediate) {
        var timeout;
        return function() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }

    function findCenterMostCard() {
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

    function updateScale() {
        const centerMostCard = findCenterMostCard();
        cards.forEach(card => {
            if (card === centerMostCard) {
                card.classList.add('scale-up');
                // Directly access data attributes
                eventDateDisplay.textContent = card.getAttribute('data-event-date');
                eventLocationDisplay.textContent = card.getAttribute('data-event-location');
            } else {
                card.classList.remove('scale-up');
            }
        });
    }

    // Debounce the updateScale function to improve performance during scroll
    const debouncedUpdateScale = debounce(updateScale, 22);

    container.addEventListener('scroll', debouncedUpdateScale);
    updateScale(); // Run initially to scale the card in the center when the page loads
});
