// autocomplete_battle.js

document.addEventListener('DOMContentLoaded', function() {
    // Ensure that the Google Maps API is loaded
    if (typeof initializeAutocomplete === 'function') {
      initializeAutocomplete('id_location', function(place) {
        console.log('Place selected in battle page:', place);
      });
    } else {
      console.error('initializeAutocomplete is not defined');
    }
  });
  