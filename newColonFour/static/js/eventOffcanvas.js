document.addEventListener('DOMContentLoaded', function() {
    const viewEventBtn = document.getElementById('view-event-btn');
    const carouselInner = document.getElementById('carousel-inner');
    const carouselIndicators = document.querySelector('.carousel-indicators');
    const noSlides = document.getElementById('no-slides');
    const battleDetails = document.getElementById('battle-details');
    const offcanvasTitle = document.getElementById('battleoffcanvasLabel');
    const lastCentermostEventId = document.getElementById('lastCentermostEventId');

    viewEventBtn.addEventListener('click', function() {
        const eventId = lastCentermostEventId.value;
        console.debug('Centermost event ID:', eventId);

        if (eventId) {
            showPlaceholders();
            fetchEventDetails(eventId)
                .then(data => {
                    console.debug('Event details:', data);
                    updateOffcanvasTitle(data.name, data.organizer_instagram);
                    updateCarousel(data.images);
                    updateBattleDetails(data.description);
                })
                .catch(error => console.error('Error fetching event details:', error))
                .finally(hidePlaceholders);
        }
    });

    function fetchEventDetails(eventId) {
        return fetch(`/get_event_details/${eventId}/`)
            .then(response => response.json());
    }

    function togglePlaceholders(show) {
        const placeholders = document.querySelectorAll('.placeholder-glow');
        
        placeholders.forEach(placeholder => {
            if (show) {
                placeholder.classList.remove('hidden');
            } else {
                placeholder.classList.add('hidden');
            }
        });
    }
    
    function showPlaceholders() {
        togglePlaceholders(true);
    }
    
    function hidePlaceholders() {
        togglePlaceholders(false);
    }

function updateOffcanvasTitle(eventName, organizerInstagram) {
    offcanvasTitle.textContent = `${eventName} Details`;

    // Update Instagram SVG href and show it if organizerInstagram exists
    const instagramLink = document.getElementById('instagramLink');
    if (organizerInstagram) {
        instagramLink.classList.remove('d-none');
        instagramLink.setAttribute('href', organizerInstagram);
    } else {
        instagramLink.classList.add('d-none');
        instagramLink.removeAttribute('href');
    }
}

    

    function updateCarousel(images) {
        carouselInner.innerHTML = ''; // Clear existing items
        carouselIndicators.innerHTML = ''; // Clear existing indicators

        if (images.length === 0) {
            noSlides.style.display = 'block';
        } else {
            noSlides.style.display = 'none';
            images.forEach((image, index) => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'carousel-item' + (index === 0 ? ' active' : '');
                const img = document.createElement('img');
                img.src = image.url;
                img.className = 'd-block w-100';
                itemDiv.appendChild(img);
                carouselInner.appendChild(itemDiv);

                const indicator = document.createElement('button');
                indicator.type = 'button';
                indicator.setAttribute('data-bs-target', '#battleCarousel');
                indicator.setAttribute('data-bs-slide-to', index.toString());
                indicator.setAttribute('aria-label', `Slide ${index + 1}`);
                if (index === 0) {
                    indicator.classList.add('active');
                    indicator.setAttribute('aria-current', 'true');
                }
                carouselIndicators.appendChild(indicator);
            });
        }
    }

    function updateBattleDetails(description) {
        battleDetails.innerHTML = `
            <h5>Description</h5>
            <p>${description}</p>
        `;
    }

    function resetOffcanvasContent() {
        offcanvasTitle.textContent = 'Battle Details';
        carouselInner.innerHTML = `
            <div class="placeholder-glow">
                <div class="placeholder" style="height: 200px;"></div>
            </div>
        `;
        carouselIndicators.innerHTML = '';
        battleDetails.innerHTML = `
            <h5>Description</h5>
            <p class="placeholder-glow">
                <span class="placeholder col-12"></span>
                <span class="placeholder col-12"></span>
                <span class="placeholder col-12"></span>
            </p>
        `;
        noSlides.style.display = 'none';
    }

    document.getElementById('battleoffcanvas').addEventListener('hidden.bs.offcanvas', resetOffcanvasContent);
});
