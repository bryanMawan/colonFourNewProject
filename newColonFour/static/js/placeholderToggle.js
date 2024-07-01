document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.form-control.search-box'); // Update to select by class
  const searchInputLabel = document.getElementById('floatingSearchLabel');
  
  function updateLabelOnFocus() {
    searchInputLabel.textContent = '"city, country"';
  }

  function resetLabelOnBlur() {
    if (!searchInput.value.trim()) {
      searchInputLabel.textContent = 'WHERE ARE YOU...';
    }
  }

  function updateBorderOnInputChange() {
    const value = searchInput.value.trim();
    const regex = /^\w+, \w+$/;

    if (value && !regex.test(value)) {
      searchInput.style.borderWidth = '2px'; // Default border width
      searchInput.style.borderColor = 'red'; // Red border color
    } else {
      searchInput.style.borderWidth = '1.3px'; // 30% thicker border
      searchInput.style.borderColor = '#dcdcdc'; // Default border color
    }
  }

  searchInput.addEventListener('focus', updateLabelOnFocus);
  searchInput.addEventListener('blur', resetLabelOnBlur);
  searchInput.addEventListener('input', updateBorderOnInputChange);
});
