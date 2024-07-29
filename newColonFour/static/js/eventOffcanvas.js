
document.addEventListener('DOMContentLoaded', function() {
    const viewEventBtn = document.getElementById('view-event-btn');
    const carouselInner = document.getElementById('carousel-inner');
    const carouselIndicators = document.querySelector('.carousel-indicators');
    const noSlides = document.getElementById('no-slides');
    const battleDetails = document.getElementById('battle-details');
    const offcanvasTitle = document.getElementById('battleoffcanvasLabel');
    const lastCentermostEventId = document.getElementById('lastCentermostEventId');
    const scrollableRow = document.getElementById('scrollable-row');
    const instagramLink = document.getElementById('instagramLink');
    const stylesContainer = document.getElementById('stylesBadgesContainer');


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
                    populateDancerCards(data.dancers);
                    populateStylesBadges(data.styles); // Added line to populate styles

                })
                .catch(error => console.error('Error fetching event details:', error))
                .finally(hidePlaceholders);
        }
    });

    function fetchEventDetails(eventId) {
        return fetch(`/get_event_details/${eventId}/`)
            .then(response => response.json());
    }



    function populateDancerCards(dancers) {
        const scrollableRow = document.getElementById('scrollable-row');
    
        if (!scrollableRow) {
            console.error('Scrollable row not found.');
            return;
        }
    
        scrollableRow.innerHTML = '';
    
        if (dancers.length > 0) {
            dancers.forEach(dancer => {
                console.debug('Dancer data:', dancer); // Debug print for dancer data
                console.debug('Dancer image URL:', dancer.image_url); // Debug print for image URL  
                console.debug('Dancer instagram_url:', dancer.instagram_url); 

                const instagramSvg = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-instagram" viewBox="0 0 16 16">
                    <path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.9 3.9 0 0 0-1.417.923A3.9 3.9 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.9 3.9 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.9 3.9 0 0 0-.923-1.417A3.9 3.9 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599s.453.546.598.92c.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.5 2.5 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.5 2.5 0 0 1-.92-.598 2.5 2.5 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233s.008-2.388.046-3.231c.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92s.546-.453.92-.598c.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92m-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217m0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334"/>
                </svg>
            `; 
 
                const cardHTML = `
                    <div class="dance-card">
                        <img src="${dancer.image_url}" alt="${dancer.name}">
                        <h5 class="mt-1"><strong>${dancer.name}</strong> ${dancer.country}</h5>
                        <p>${dancer.role}</p>
                    ${dancer.instagram_url ? `<a href="${dancer.instagram_url}" target="_blank">${instagramSvg}</a>` : ''}
                    </div>
                `;
                scrollableRow.insertAdjacentHTML('beforeend', cardHTML);
            });

            scrollableRow.style.display = 'flex';
        } else {
            console.log('No dancers available for this event.');
        }
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

        if (organizerInstagram) {
            instagramLink.setAttribute('href', organizerInstagram);
        } else {
            instagramLink.setAttribute('href', '#');
        }
    }

    function updateCarousel(images) {
        carouselInner.innerHTML = '';
        carouselIndicators.innerHTML = '';

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

    /**
 * Populates the styles badges in the stylesBadgesContainer.
 * @param {Array} styles - Array of style strings.
 */
    function populateStylesBadges(styles) {
        const stylesContainer = document.getElementById('stylesBadgesContainer');
        
        if (!stylesContainer) {
            console.error('Styles Badges Container not found.');
            return;
        }
    
        stylesContainer.innerHTML = ''; // Clear existing badges
    
        if (styles.length > 0) {
            styles.forEach(style => {
                const badge = createBadge(style);
                stylesContainer.appendChild(badge);
            });
        } else {
            console.log('No styles available for this event.');
        }
    }

    /**
     * Creates a badge element for a given sub-option.
     * @param {string} suboption - The sub-option text.
     * @returns {HTMLElement} - The created badge element.
     */
    function createBadge(suboption) {
        const badge = document.createElement('button');
        badge.className = 'badge-filter btn btn-outline-primary me-1'; // Added margin for spacing
        badge.textContent = suboption;
        return badge;
    }

    function updateBattleDetails(description) {
        battleDetails.innerHTML = `
            <h5>Description</h5>
            <p>${description}</p>
        `;
    }

    function resetOffcanvasContent() {
        offcanvasTitle.textContent = 'Battle Details';
        instagramLink.setAttribute('href', '#');
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
        scrollableRow.innerHTML = '';
        stylesContainer.innerHTML = ''; // Clear existing badges
        scrollableRow.style.display = 'none';
    }

    document.getElementById('battleoffcanvas').addEventListener('hidden.bs.offcanvas', resetOffcanvasContent);
});
