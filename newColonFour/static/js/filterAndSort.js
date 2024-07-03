document.addEventListener('DOMContentLoaded', () => {
    const filterDropdown = document.getElementById('filterDropdown');
    const searchBar = document.getElementById('searchBar'); // Get the search bar element


    // Event listener for dropdown change
    filterDropdown.addEventListener('change', handleDropdownChange);

        // Event listener for search bar input
    searchBar.addEventListener('input', handleSearchInput);
});

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
 * Handles the dropdown change event, fetches sub-options, and displays them as badges.
 * @param {Event} event - The change event of the dropdown.
 */
async function handleDropdownChange(event) {
    const selectedOption = event.target.value;
    if (selectedOption) {
        try {
            const suboptions = await fetchSuboptions(selectedOption);
            displaySuboptions(suboptions);
        } catch (error) {
            console.error('Error fetching suboptions:', error);
        }
    }
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
        const badge = createBadge(suboption);
        if (suboption.toLowerCase().includes(searchText)) {
            badge.style.display = ''; // Show badge if it matches search text
        } else {
            badge.style.display = 'none'; // Hide badge if it doesn't match search text
        }
        filterBadgesContainer.appendChild(badge);
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
    const combinedText = `${dropdownText}: ${badgeText}`;
    
    const chosenFiltersBody = document.getElementById('chosenFiltersBody');
    const existingButtons = chosenFiltersBody.getElementsByClassName('filter-button');

    for (const button of existingButtons) {
        const buttonText = button.textContent.replace('×', '').trim();
        console.log(`Checking button with text: ${buttonText}`); // Debug statement
        if (buttonText === combinedText) {
            console.log(`Duplicate found: ${combinedText}`); // Debug statement
            return; // Do not add the button if it already exists
        }
    }

    console.log(`No duplicate found, adding filter button: ${combinedText}`); // Debug statement
    createAndAppendFilterButton(combinedText);
}


/**
 * Handles the create button click event by creating a filter button with the input text.
 */
function handleCreateFilterButton() {
    const filterText = document.getElementById('badgeText').value.trim();
    
    if (filterText !== '') {
        createAndAppendFilterButton(filterText);
        // Clear input field after button creation
        document.getElementById('badgeText').value = '';
    }
}

/**
 * Creates a filter button with the given text and appends it to the chosen filters section.
 * If a filter button with the same text already exists, it won't be added again.
 * @param {string} text - The text for the filter button.
 */
function createAndAppendFilterButton(text) {
    const chosenFiltersBody = document.getElementById('chosenFiltersBody');
    const existingButtons = chosenFiltersBody.getElementsByClassName('filter-button');

    for (const button of existingButtons) {
        if (button.textContent.trim() === text) {
            return; // Do not add the button if it already exists
        }
    }

    const button = createFilterButton(text);
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
