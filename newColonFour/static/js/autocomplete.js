// autocomplete.js

// Initialize the Google Places Autocomplete
function initAutocomplete() {
    var input = document.getElementById('autocomplete');
    var autocomplete = new google.maps.places.Autocomplete(input, {
        types: ['geocode']
    });

    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            console.log("Place details not found for input: " + input.value);
            return;
        }

        // You can access the selected place details here
        console.log("Place selected: ", place);

        // Optionally, update other fields based on the selected place
        // Example: Update hidden fields with place details
        document.getElementById('utc-date').value = new Date().toISOString();
    });
}

// Check if Google Maps API is loaded
google.maps.event.addDomListener(window, 'load', initAutocomplete);
