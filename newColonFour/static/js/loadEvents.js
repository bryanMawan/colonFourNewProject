$(document).ready(function() {
    console.log("Document is ready.");
    console.log("Event AJAX URL:", eventAjaxUrl);

    // Function to get URL parameters
    function getUrlParams() {
        let params = {};
        let queryString = window.location.search.substring(1);
        let urlParams = new URLSearchParams(queryString);

        urlParams.forEach((value, key) => {
            params[key] = value;
        });

        return params;
    }

    // Function to load events via AJAX
    function loadEvents() {
        console.log("loadEvents function called.");

        // Log individual form field values
        console.log("Search Box Value:", $('input[name="search-box"]').val());

        // Serialize form data
        let serializedFormData = $('#search-form').serialize();
        console.log("Serialized form data:", serializedFormData);

        // Get URL parameters and append them to serialized form data
        let urlParams = getUrlParams();
        console.log("URL Parameters:", urlParams);

        let combinedData = serializedFormData;
        for (let key in urlParams) {
            if (urlParams.hasOwnProperty(key)) {
                combinedData += `&${encodeURIComponent(key)}=${encodeURIComponent(urlParams[key])}`;
            }
        }
        console.log("Combined Data:", combinedData);

        $.ajax({
            url: eventAjaxUrl,
            method: 'GET',
            data: combinedData,
            beforeSend: function() {
                console.log("AJAX request about to be sent.");
                $('.scroll-container').html('<div class="card card-spinner"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>');
            },
            success: function(response) {
                console.log("AJAX request successful.");
                console.log("Response:", response);

                // Debug: Print the events data received
                if (response.events) {
                    console.log("Events data received from backend:");
                    console.log(response.events);

                    $('.scroll-container').empty();

                    response.events.forEach(function(event) {
                        // Debug: Print each event object
                        console.log("Processing event:", event);

                        let eventCard = `<div class="card position-relative" data-event-id="${event.id}" data-event-date="${event.formatted_date}" data-event-location="${event.location}">
                                            ${event.poster_url ? `<img src="${event.poster_url}" alt="${event.name}" class="event-poster">` : ''}
                                            <p class="event-name">${event.name}</p>
                                            <span class="badge badge-goers rounded-pill">${event.get_number_of_goers} <span class="visually-hidden">goings</span></span>
                                            <span class="badge badge-type rounded-pill">${event.get_event_type_display} <span class="visually-hidden">type</span></span>
                                            <span class="badge badge-level rounded-pill">${event.level} <span class="visually-hidden">level</span></span>
                                          </div>`;

                        // Debug: Print the HTML for each event card
                        console.log("Event card HTML:", eventCard);

                        $('.scroll-container').append(eventCard);
                    });

                    // Call updateScale after events are loaded
                    updateScale();
                } else if (response.error) {
                    console.error("Error in response:", response.error);
                    $('.scroll-container').html('<p>Error loading events.</p>');
                } else {
                    console.warn("Unexpected response format:", response);
                    $('.scroll-container').html('<p>No events found.</p>');
                }
            },
            error: function(xhr, status, error) {
                console.error("AJAX request failed.");
                console.error("Status:", status);
                console.error("Error:", error);
                $('.scroll-container').html('<p>An error occurred while loading events.</p>');
            }
        });
    }

    // Load events when the page loads
    loadEvents();

    // Load events when the form is submitted
    $('#search-form').on('submit', function(event) {
        console.log("Form submitted.");
        event.preventDefault(); // Prevent default form submission
        loadEvents(); // Trigger event loading
    });
});
