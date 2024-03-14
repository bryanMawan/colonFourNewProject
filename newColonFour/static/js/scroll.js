document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector('.scroll-container');
    const cards = document.querySelectorAll('.card');

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
            } else {
                card.classList.remove('scale-up');
            }
        });
    }

    container.addEventListener('scroll', updateScale);
    updateScale(); // Run initially to scale the card in the center when the page loads
});