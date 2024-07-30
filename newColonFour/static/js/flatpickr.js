// Include Flatpickr JS
document.write('<script src="https://cdn.jsdelivr.net/npm/flatpickr"><\/script>');

document.addEventListener('DOMContentLoaded', function() {
    initializeFlatpickr();
});

function initializeFlatpickr() {
    flatpickr("#date_range", {
        mode: "range",
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        minDate: getMinDate(), // Set the minimum date to 1 day after today
        onChange: handleDateRangeChange
    });
}

function getMinDate() {
    // Calculate the date that is 1 day after today
    const today = new Date();
    today.setDate(today.getDate() + 1);
    return today.toISOString().split('T')[0] + ' 00:00'; // Format as "Y-m-d H:i"
}

function handleDateRangeChange(selectedDates, dateStr, instance) {
    try {
        const [start, end] = selectedDates;

        if (start && end) {
            setDateAndTime(start, end);
        } else if (start) {
            setDateAndTime(start, start);
        }
    } catch (error) {
        console.error("An error occurred while processing date range changes: ", error);
    }
}

function setDateAndTime(startDate, endDate) {
    try {
        const startDateFormatted = flatpickr.formatDate(startDate, "Y-m-d");
        const endDateFormatted = flatpickr.formatDate(endDate, "Y-m-d");
        const endTimeFormatted = flatpickr.formatDate(endDate, "H:i");

        document.getElementById('id_date').value = startDateFormatted;
        document.getElementById('id_end_date').value = endDateFormatted;
        document.getElementById('id_start_time').value = endTimeFormatted;

    } catch (error) {
        console.error("Failed to set date and time: ", error);
    }
}
