document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("search-form").addEventListener("submit", function() {
      // Capture the current UTC time in ISO format
      const nowUtcDateIso = new Date().toISOString();
      
      // Set the UTC time as the value of the hidden input
      document.getElementById("utc-date").value = nowUtcDateIso;
    });
  });
  