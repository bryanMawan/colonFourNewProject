document.addEventListener('DOMContentLoaded', () => {
    const filterDropdown = document.getElementById('filterDropdown');
    const searchBar = document.getElementById('searchBar');
    const addDateRangeFilterBtn = document.getElementById('addDateRangeFilterBtn');
    const addWeekendFilterBtn = document.getElementById('addWeekendFilterBtn');
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    const chosenFiltersBody = document.getElementById('chosenFiltersBody');
    const orderSoonestBtn = document.getElementById('orderSoonestBtn');
    const orderClosestBtn = document.getElementById('orderClosestBtn');
    const orderPopularBtn = document.getElementById('orderPopularBtn');
    const addThisWeekFilterBtn = document.getElementById('addThisWeekFilterBtn');
    const addNextWeekFilterBtn = document.getElementById('addNextWeekFilterBtn');
    const addTodayFilterBtn = document.getElementById('addTodayFilterBtn');

    // Event listeners
    filterDropdown.addEventListener('change', handleDropdownChange);
    searchBar.addEventListener('input', handleSearchInput);
    addDateRangeFilterBtn.addEventListener('click', handleAddDateRangeFilter);
    addWeekendFilterBtn.addEventListener('click', handleAddWeekendFilter);
    applyFiltersBtn.addEventListener('click', handleApplyFilters);
    clearFiltersBtn.addEventListener('click', handleClearFilters);
    orderSoonestBtn.addEventListener('click', () => handleOrderBy('Soonest'));
    orderClosestBtn.addEventListener('click', () => handleOrderBy('Closest'));
    orderPopularBtn.addEventListener('click', () => handleOrderBy('Popular'));
    addThisWeekFilterBtn.addEventListener('click', handleAddThisWeekFilter);
    addNextWeekFilterBtn.addEventListener('click', handleAddNextWeekFilter);
    addTodayFilterBtn.addEventListener('click', handleAddTodayFilter);
    // Initialize filters from URL
    initializeFiltersFromURL();

    console.log('Event listeners attached and filters initialized'); // Debug statement


});

/**
 * Parses the URL parameters and initializes the filters.
 */
function initializeFiltersFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    for (const [filterType, filterValues] of urlParams.entries()) {
        const values = filterValues.split(',').map(value => decodeURIComponent(value.trim()));
        values.forEach(value => {
            createAndAppendFilterButton(value, filterType);
        });
    }
    console.log('Filters initialized from URL'); // Debug statement
}


/**
 * Handles the search bar input event, filters the displayed badges based on the search input.
 * @param {Event} event - The input event of the search bar.
 */
function handleSearchInput(event) {
    const searchText = event.target.value.toLowerCase();
    const filterBadgesContainer = document.getElementById('filterBadgesContainer');
    const badges = filterBadgesContainer.getElementsByClassName('badge-filter');

    for (const badge of badges) {
        if (badge.textContent.toLowerCase().includes(searchText)) {
            badge.style.display = ''; // Show badge
        } else {
            badge.style.display = 'none'; // Hide badge
        }
    }
}

/**
 * Handles the dropdown change event, fetches sub-options if applicable, and displays either the input field for "Name" or the date range picker.
 * @param {Event} event - The change event of the dropdown.
 */
async function handleDropdownChange(event) {
    const selectedOption = event.target.value;
    const filterBadgesContainer = document.getElementById('filterBadgesContainer');
    const dateRangePickerContainer = document.getElementById('dateRangePickerContainer');
    
    // Clear previous content
    filterBadgesContainer.innerHTML = '';
    dateRangePickerContainer.style.display = 'none';

    if (selectedOption === 'name') {
        displayNameInputField();
    } else if (selectedOption === 'date-range') {
        // gpt: move this to its own modular method(in this method, add functionality to the addDateRangeFilterBtn so its takes the date range from the fields ad sends to the the active filter as filter badge in format "mm/dd - mm/dd" )
        dateRangePickerContainer.style.display = 'block';
    } else if (selectedOption) {
        try {
            const suboptions = await fetchSuboptions(selectedOption);
            displaySuboptions(suboptions);
        } catch (error) {
            console.error('Error fetching suboptions:', error);
        }
    }
}


/**
 * Displays the input field and button for adding a "Name" filter.
 */
function displayNameInputField() {
    const filterBadgesContainer = document.getElementById('filterBadgesContainer');
    const dropdownText = document.getElementById('filterDropdown').value;


    const nameInputField = document.createElement('input');
    nameInputField.type = 'text';
    nameInputField.className = 'form-control mb-2';
    nameInputField.placeholder = 'Enter name';

    const addButton = document.createElement('button');
    addButton.className = 'btn btn-outline-primary';
    addButton.textContent = 'Add to filter';
    addButton.addEventListener('click', () => {
        const nameText = nameInputField.value.trim();
        if (nameText !== '') {
            createAndAppendFilterButton(nameText, dropdownText); // Pass null for dropdownText
            nameInputField.value = ''; // Clear input field after adding
        }
    });

    filterBadgesContainer.appendChild(nameInputField);
    filterBadgesContainer.appendChild(addButton);
}


/**
 * Fetches sub-options from the server based on the selected dropdown option.
 * @param {string} option - The selected dropdown option.
 * @returns {Promise<Array>} - A promise that resolves to an array of sub-options.
 */
async function fetchSuboptions(option) {
    const response = await fetch(`/fetch_suboptions/?option=${option}`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    console.log('Fetched suboptions:', data); // Debugging line
    return data.suboptions;
}


/**
 * Displays sub-options as badges and filters them based on the search input.
 * @param {Array} suboptions - An array of sub-options.
 */
function displaySuboptions(suboptions) {
    const filterBadgesContainer = document.getElementById('filterBadgesContainer');
    const searchBar = document.getElementById('searchBar');
    const searchText = searchBar.value.toLowerCase();

    filterBadgesContainer.innerHTML = ''; // Clear previous badges

    suboptions.forEach(suboption => {
        if (typeof suboption === 'string') { // Ensure suboption is a string
            const badge = createBadge(suboption);
            if (suboption.toLowerCase().includes(searchText)) {
                badge.style.display = ''; // Show badge if it matches search text
            } else {
                badge.style.display = 'none'; // Hide badge if it doesn't match search text
            }
            filterBadgesContainer.appendChild(badge);
        } else {
            console.error('Suboption is not a string:', suboption); // Debugging line
        }
    });
}



/**
 * Creates a badge element for a given sub-option.
 * @param {string} suboption - The sub-option text.
 * @returns {HTMLElement} - The created badge element.
 */
function createBadge(suboption) {
    const badge = document.createElement('button');
    badge.className = 'badge-filter btn btn-outline-primary';
    badge.textContent = suboption;
    badge.addEventListener('click', handleBadgeClick);
    return badge;
}

/**
 * Handles the badge click event by creating a filter button with the badge text.
 * Checks if a filter button with the same text already exists before adding.
 * @param {Event} event - The click event of the badge.
 */
function handleBadgeClick(event) {
    const badgeText = event.target.textContent;
    const dropdownText = document.getElementById('filterDropdown').value;
    createAndAppendFilterButton(badgeText, dropdownText);
}



/**
 * Handles the create button click event by creating a filter button with the input text.
 */
function handleCreateFilterButton() {
    const filterText = document.getElementById('badgeText').value.trim();
    const dropdownText = document.getElementById('filterDropdown').value;


    if (filterText !== '') {
        createAndAppendFilterButton(filterText, dropdownText); // Pass null for dropdownText
        document.getElementById('badgeText').value = ''; // Clear input field after button creation
    }
}

/**
 * Creates a filter button with the given text and appends it to the chosen filters section.
 * If a filter button with the same text already exists, it won't be added again.
 * @param {string} badgeText - The text for the filter button.
 * @param {string} dropdownText - The dropdown text.
 */
function createAndAppendFilterButton(badgeText, dropdownText) {
    // Ensure only one "date-range" filter button can be added
    if (dropdownText === 'date-range') {
        const chosenFiltersBody = document.getElementById('chosenFiltersBody');
        const existingButtons = chosenFiltersBody.getElementsByClassName('filter-button');
        for (const button of existingButtons) {
            if (button.textContent.includes('date-range')) {
                showAlert('Only one date-range filter can be added.');
                return;
            }
        }
    }

    const combinedText = dropdownText ? `${dropdownText}: ${badgeText}` : badgeText;
    const chosenFiltersBody = document.getElementById('chosenFiltersBody');
    const existingButtons = chosenFiltersBody.getElementsByClassName('filter-button');

    for (const button of existingButtons) {
        if (button.textContent.replace('×', '').trim() === combinedText) {
            return; // Do not add the button if it already exists
        }
    }

    const button = createFilterButton(combinedText);
    chosenFiltersBody.appendChild(button); // Append button to chosen filters body
}

/**
 * Creates a filter button element with the given text.
 * @param {string} text - The text for the filter button.
 * @returns {HTMLElement} - The created filter button element.
 */
function createFilterButton(text) {
    const button = document.createElement('button');
    button.classList.add('filter-button', 'btn', 'btn-outline-primary', 'me-1', 'mb-1');
    button.textContent = text;
    
    const closeIcon = document.createElement('span');
    closeIcon.innerHTML = '&times;'; // Close icon (×)
    closeIcon.classList.add('filter-close-icon', 'ms-1');
    
    button.appendChild(closeIcon);
    
    button.addEventListener('click', () => {
        button.remove(); // Remove button when clicked
    });
    
    return button;

}

/**
 * Clears the start and end date inputs.
 */
function clearDateInputs() {
    document.getElementById('startDateInput').value = '';
    document.getElementById('endDateInput').value = '';
}

/**
 * Handles adding a date range filter based on selected start and end dates.
 */
function handleAddDateRangeFilter() {
    const dropdownText = document.getElementById('filterDropdown').value;
    const startDate = document.getElementById('startDateInput').value;
    const endDate = document.getElementById('endDateInput').value;

    if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);

        if (start > end) {
            showAlert('Start date must be before the end date.');
            return;
        }

        const formattedDateRange = `${formatDate(startDate)} - ${formatDate(endDate)}`;
        createAndAppendFilterButton(formattedDateRange, dropdownText);
        clearDateInputs();
    } else {
        showAlert('Please select both start and end dates.');
    }
}

/**
 * Formats the date in 'YYYY-MM-DD' format.
 * @param {string} date - The date to format.
 * @returns {string} - Formatted date string.
 */
function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
}

/**
 * Handles adding a "Weekend" filter badge to the active filters section.
 */
function handleAddWeekendFilter() {
    const dropdownText = "weekend-events";
    const weekendBadgeText = 'Weekend';
    createAndAppendFilterButton(weekendBadgeText, dropdownText);
}

/**
 * Shows an alert message.
 * @param {string} message - The message to display in the alert.
 */
function showAlert(message) {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    alertContainer.appendChild(alert);

    // Automatically remove the alert after a certain time (e.g., 5 seconds)
    setTimeout(() => {
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

function handleApplyFilters() {
    const chosenFiltersBody = document.getElementById('chosenFiltersBody');
    const filterButtons = chosenFiltersBody.getElementsByClassName('filter-button');
    const filtersDict = {};  // Dictionary to store filter types and their selected values

    for (const button of filterButtons) {
        const filterText = button.textContent.replace('×', '').trim();
        const [filterType, filterValue] = filterText.split(': ');  // Split into type and value

        // Append to existing values or initialize
        if (filtersDict[filterType]) {
            filtersDict[filterType] += `, ${filterValue}`;
        } else {
            filtersDict[filterType] = filterValue;
        }
    }

    console.log('Filters Dictionary:', filtersDict); // Debug statement

    // Convert filtersDict to a query string format
    const queryString = Object.entries(filtersDict)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
    
    const newUrl = `${window.location.pathname}?${queryString}`;
    console.log('New URL:', newUrl); // Debug statement
    window.location.href = newUrl;
}

function handleClearFilters() {
    const chosenFiltersBody = document.getElementById('chosenFiltersBody');
    chosenFiltersBody.innerHTML = '';
}

function handleOrderBy(orderType) {
    const existingOrderBadge = [...document.getElementsByClassName('filter-button')]
        .find(button => button.textContent.includes(orderType));
    if (existingOrderBadge) {
        toggleOrderBadge(existingOrderBadge);
    } else {
        addOrderBadge(orderType, true); // Add as ascending by default
    }
    console.log(`Ordering by ${orderType}`); // Debug statement
}

function toggleOrderBadge(button) {
    const isAscending = button.textContent.includes('↑');
    button.textContent = button.textContent.replace(isAscending ? '↑' : '↓', isAscending ? '↓' : '↑');
    console.log(`Toggled ${button.textContent}`); // Debug statement
}

function addOrderBadge(orderType, isAscending) {
    // Remove any existing order badge
    removeExistingOrderBadge();

    const badgeText = `${orderType} ${isAscending ? '↑' : '↓'}`;
    const button = createFilterButton('order-by: ' + badgeText);
    document.getElementById('chosenFiltersBody').appendChild(button);
    console.log(`Added ${badgeText} order badge`); // Debug statement
}
/**
 * Calculates the date range for a given period.
 * @param {string} periodType - The type of period ("today", "this-week", or "next-week").
 * @returns {string} - The date range in the format "YYYY-MM-DD - YYYY-MM-DD".
 */
function calculateDateRange(periodType) {
    const today = new Date();
    let startDate, endDate;

    if (periodType === "today") {
        // Today
        startDate = new Date(today);
        endDate = new Date(today);
    } else if (periodType === "this-week") {
        // This Week (Sunday to Saturday)
        const startOfWeek = today.getDate() - today.getDay();
        startDate = new Date(today.setDate(startOfWeek));
        endDate = new Date(today.setDate(startOfWeek + 6));
    } else if (periodType === "next-week") {
        // Next Week (Sunday to Saturday)
        const startOfNextWeek = today.getDate() - today.getDay() + 7;
        startDate = new Date(today.setDate(startOfNextWeek));
        endDate = new Date(today.setDate(startOfNextWeek + 6));
    }

    // Format dates to "YYYY-MM-DD"
    const formatDate = date => date.toISOString().split('T')[0];
    return `${formatDate(startDate)} - ${formatDate(endDate)}`;
}

/**
 * Handles adding a filter badge with a date range to the active filters section.
 * @param {string} weekType - The type of week ("this-week" or "next-week").
 * @param {string} filterText - The text for the filter badge (e.g., "This Week").
 */
function handleAddFilterWithDateRange(weekType, filterText) {
    const dateRange = calculateDateRange(weekType);
    createAndAppendFilterButton(`${dateRange}`, `date-range`);
    console.log(`Added ${filterText} filter with date range: ${dateRange}`); // Debug statement
}

/**
 * Handles adding a "This Week" filter badge with a date range to the active filters section.
 */
function handleAddThisWeekFilter() {
    handleAddFilterWithDateRange("this-week", "This Week");
}

/**
 * Handles adding a "Next Week" filter badge with a date range to the active filters section.
 */
function handleAddNextWeekFilter() {
    handleAddFilterWithDateRange("next-week", "Next Week");
}

function handleAddTodayFilter() {
    handleAddFilterWithDateRange("today", "Today");
}




function removeExistingOrderBadge() {
    const chosenFiltersBody = document.getElementById('chosenFiltersBody');
    const existingOrderBadge = [...chosenFiltersBody.getElementsByClassName('filter-button')]
        .find(button => button.textContent.includes('Soonest') || button.textContent.includes('Closest') || button.textContent.includes('Popular'));
    if (existingOrderBadge) {
        existingOrderBadge.remove();
        console.log('Removed existing order badge'); // Debug statement
    }
}
