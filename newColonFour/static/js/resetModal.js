document.addEventListener('DOMContentLoaded', function() {
    // ... your existing event listeners and functions

    var goingModal = document.getElementById('goingModal');

    // Event listener for the modal close event
    goingModal.addEventListener('hidden.bs.modal', function () {
      // Reset the phone number and SMS code fields
      document.getElementById('phoneNumber').value = '';
      document.getElementById('smsCode').value = '';
      document.getElementById('smsCode').disabled = true;

      // Reset the toggle switch to its default state, if needed
      document.getElementById('flexSwitchCheckDefault').checked = false; // or false, depending on your default

      // Show the send code button again if it was hidden
      var sendCodeBtn = document.querySelector('.btn-primary.mb-2');
      sendCodeBtn.style.display = 'block';

      // Ensure the send code button is centered
      sendCodeBtn.style.marginRight = 'auto';
      sendCodeBtn.style.marginLeft = 'auto';

      // You can also reset any other states or styles as required
    });
  });