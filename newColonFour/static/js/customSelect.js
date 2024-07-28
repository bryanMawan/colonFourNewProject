function initializeSelect2() {
    // Initialize Select2 on the element with id 'id_judges'
    $('#id_judges').select2({
        placeholder: "Select Judges...",
        width: 'resolve', // Adjust width based on container
        tags: true, // Allow tagging
    });

    // Initialize Select2 on the element with id 'id_host'
    $('#id_host').select2({
        placeholder: "Search Hosts...",
        width: 'resolve', // Adjust width based on container
        tags: true, // Allow tagging
    });

    console.log('Select2 initialized for the judges and hosts fields.');
}

// Initialize Select2 elements on document ready
document.addEventListener('DOMContentLoaded', () => {
    initializeSelect2();
});
