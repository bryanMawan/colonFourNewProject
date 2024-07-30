google.maps.event.addDomListener(window, 'load', function() {
    initializeAutocomplete('autocomplete', function(place) {
      document.getElementById('utc-date').value = new Date().toISOString();
    });
  });