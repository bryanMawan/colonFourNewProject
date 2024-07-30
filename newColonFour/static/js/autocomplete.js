function initializeAutocomplete(inputId, callback) {
    var input = document.getElementById(inputId);
    if (!input) return;
  
    var autocomplete = new google.maps.places.Autocomplete(input, {
      types: ['geocode']
    });
  
    autocomplete.addListener('place_changed', function() {
      var place = autocomplete.getPlace();
      if (!place.geometry) {
        console.log("Place details not found for input: " + input.value);
        return;
      }
  
      console.log("Place selected: ", place);
      if (callback) callback(place);
    });
  }
  