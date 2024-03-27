document.addEventListener('DOMContentLoaded', function () {
    var sendCodeBtn = document.querySelector('.btn-primary.mb-2');
    var verifyCodeBtn = document.querySelector('.btn-success.mb-2');


    sendCodeBtn.addEventListener('click', function () {
        var phoneNumber = document.getElementById('phoneNumber').value;
        if (!phoneNumber) {
            alert('Please fill in your phone number.');
            return;
        }
        sendCode(phoneNumber);
    });

    verifyCodeBtn.addEventListener('click', function () {
        var phoneNumber = document.getElementById('phoneNumber').value;
        var smsCode = document.getElementById('smsCode').value;
        verifyCode(phoneNumber, smsCode);
    });

    function adjustAlert(show, type, message) {
        var alertDiv = document.querySelector('.alert');
        if (show) {
            alertDiv.style.display = ''; // Make the alert visible
            alertDiv.className = 'alert alert-' + type; // Set the alert type (e.g., 'alert-primary')
            alertDiv.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        } else {
            alertDiv.style.display = 'none'; // Hide the alert
        }
    }

    function sendCode(phoneNumber) {
        var csrftoken = getCookie('csrftoken');
        var sendCodeUrl = sendCodeBtn.getAttribute('data-url');

        fetch(sendCodeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: 'phoneNumber=' + encodeURIComponent(phoneNumber)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('smsCode').disabled = false;
                    sendCodeBtn.style.display = 'none';
                    verifyCodeBtn.style.display = 'inline-block';
                } else {
                    console.error('Failed to send code:', data.message);
                }
            });
    }

    function verifyCode(phoneNumber, smsCode) {
        var csrftoken = getCookie('csrftoken');
        var verifyCodeUrl = verifyCodeBtn.getAttribute('data-url');
        var eventId = document.getElementById('current-event-id').value; // Retrieve event ID



        fetch(verifyCodeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: `phoneNumber=${encodeURIComponent(phoneNumber)}&smsCode=${encodeURIComponent(smsCode)}&goingToggle=${document.getElementById('flexSwitchCheckDefault').checked}&eventId=${encodeURIComponent(eventId)}`
        })
            .then(response => response.json())
            .then(data => {
                const alertTrigger = data.valid
                if (alertTrigger) {
                    verifyCodeBtn.style.display = 'none';
                    appendAlert(data.message, 'success')
                } else {
                    appendAlert(data.message, 'danger')
                }
            });
    }


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

    const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
    const appendAlert = (message, type) => {
        const wrapper = document.createElement('div')
        wrapper.innerHTML = [
            `<div class="alert alert-${type} alert-dismissible" role="alert">`,
            `   <div>${message}</div>`,
            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'
        ].join('')

        alertPlaceholder.append(wrapper)
    }
});
