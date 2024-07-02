document.addEventListener('DOMContentLoaded', function () {
  
    // Function to create a button with custom styling
    function createFilterButton(text) {
      // Create the button element
      const button = document.createElement('button');
      button.classList.add('filter-button', 'btn', 'btn-outline-primary', 'me-1', 'mb-1');
      button.textContent = text;
      
      // Create the close icon for the button
      const closeIcon = document.createElement('span');
      closeIcon.innerHTML = '&times;'; // Close icon (×)
      closeIcon.classList.add('filter-close-icon', 'ms-1');
      
      // Append close icon to button
      button.appendChild(closeIcon);
      
      // Event listener to remove button on click
      button.addEventListener('click', function () {
        button.remove(); // Remove button when clicked
      });
      
      return button;
    }
    
    // Function to handle button creation on button click
    function handleCreateFilterButton() {
      const filterText = document.getElementById('badgeText').value.trim();
      
      if (filterText !== '') {
        const button = createFilterButton(filterText);
        const chosenFiltersBody = document.getElementById('chosenFiltersBody');
        chosenFiltersBody.appendChild(button); // Append button to chosen filters body
        
        // Clear input field after button creation
        document.getElementById('badgeText').value = '';
      }
    }
    
    // Event listener for create button click
    const createButton = document.getElementById('createBadgeBtn');
    createButton.addEventListener('click', handleCreateFilterButton);
    
  });
  