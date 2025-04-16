// Simple form validation for index.html
window.addEventListener('DOMContentLoaded', function() {
  var form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', function(event) {
      var numPort = document.getElementById('num_port').value;
      var rfRate = document.getElementById('risk_free_rate').value;
      if (numPort < 1000 || numPort > 20000) {
        alert('Number of simulations must be between 1,000 and 20,000.');
        event.preventDefault();
      }
      if (isNaN(rfRate)) {
        alert('Please enter a valid risk-free rate.');
        event.preventDefault();
      }
    });
  }
});
