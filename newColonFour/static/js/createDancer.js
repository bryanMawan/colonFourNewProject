document.addEventListener('DOMContentLoaded', function() {
    // Get references to the form and button
    const form = document.getElementById('dancerForm');
    const submitButton = document.getElementById('dancerFormSubmit');
    const overlay = document.getElementById('loadingOverlay');

    // Function to show the overlay
    function showOverlay() {
        overlay.style.display = 'block';
    }

    // Function to hide the overlay
    function hideOverlay() {
        overlay.style.display = 'none';
    }

    // Add an event listener to the button
    submitButton.addEventListener('click', function(event) {
        // Prevent the default form submission
        event.preventDefault();
        
        // Show the loading overlay
        showOverlay();

        // Create a FormData object
        const formData = new FormData(form);

        // Get the CSRF token from the form
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Use the passed URL for AJAX request
        fetch(createDancerUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json'  // Expecting JSON response
            },
            body: formData
        })
        .then(response => {
            console.log('Response:', response);  // Log the full response for debugging
            if (!response.ok) {
                // If the response is not OK, throw an error with the response text
                return response.text().then(text => { throw new Error(text); });
            }
            return response.json();  // Parse the response as JSON
        })
        .then(data => {
            console.log('Data:', data);  // Log the data received from the server
            if (data.success) {
                alert('Dancer created successfully!');
                // Optionally, you can reset the form or close the offcanvas
                form.reset();
                var offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('dancerCreationOffcanvas'));
                offcanvas.hide();
                // Reload the current URL
                window.location.reload();
            } else {
                // Handle validation errors returned from the server
                alert('Error creating dancer: ' + data.errors.join(', '));
                // Hide the loading overlay if there's an error
                hideOverlay();
            }
        })
        .catch(error => {
            // Handle any errors that occur during the fetch
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);
            // Hide the loading overlay if there's an error
            hideOverlay();
        });
    });
});
