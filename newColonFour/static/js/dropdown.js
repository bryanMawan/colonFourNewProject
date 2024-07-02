document.addEventListener('DOMContentLoaded', () => {
    const filterDropdown = document.getElementById('filterDropdown');
    const filterBadgesContainer = document.getElementById('filterBadgesContainer');

    filterDropdown.addEventListener('change', handleDropdownChange);
});

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

async function fetchSuboptions(option) {
    const response = await fetch(`/fetch_suboptions/?option=${option}`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data.suboptions;
}

function displaySuboptions(suboptions) {
    const filterBadgesContainer = document.getElementById('filterBadgesContainer');
    filterBadgesContainer.innerHTML = ''; // Clear previous badges

    suboptions.forEach(suboption => {
        const badge = createBadge(suboption);
        filterBadgesContainer.appendChild(badge);
    });
}

function createBadge(suboption) {
    const badge = document.createElement('button');
    badge.className = 'btn btn-outline-secondary badge-filter';
    badge.textContent = suboption;
    badge.addEventListener('click', handleBadgeClick);
    return badge;
}

function handleBadgeClick(event) {
    const badgeText = event.target.textContent;
    console.log('Badge clicked:', badgeText);
    // Add logic to handle badge click event
}
