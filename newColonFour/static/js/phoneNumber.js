document.addEventListener('DOMContentLoaded', function() {
    var sendCodeBtn = document.querySelector('.btn-primary.mb-2'); // Adjust the selector if needed
    sendCodeBtn.addEventListener('click', function() {
      var phoneNumber = document.getElementById('phoneNumber').value;
      var csrftoken = getCookie('csrftoken'); // Function to get the value of the CSRF token cookie
      var sendCodeUrl = sendCodeBtn.getAttribute('data-url'); // Retrieve the URL from the data attribute

      // AJAX request to send the code
      fetch(sendCodeUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrftoken, // Include CSRF token in header
        },
        body: 'phoneNumber=' + encodeURIComponent(phoneNumber)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Code has been sent, so enable the SMS code field and hide the send code button
          document.getElementById('smsCode').disabled = false;
          sendCodeBtn.style.display = 'none';
        } else {
          // Handle the case where the code was not sent successfully
          console.error('Failed to send code:', data.message);
        }
      });
    });

    // Helper function to get CSRF token value
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  });
