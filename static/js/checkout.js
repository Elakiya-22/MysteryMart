/**
 * MysteryMart — Checkout & Weather Integration Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  const cityInput = document.getElementById('cityInput');
  const weatherBadge = document.getElementById('checkoutWeatherBadge');
  const weatherText = document.getElementById('checkoutWeatherText');

  let weatherTimer = null;

  if (cityInput) {
    cityInput.addEventListener('input', () => {
      clearTimeout(weatherTimer);
      const city = cityInput.value.trim();
      if (city.length < 3) return;

      weatherTimer = setTimeout(async () => {
        if (weatherText) {
          weatherText.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Checking destination weather...';
        }

        try {
          const res = await fetch(`/checkout/weather-check?city=${encodeURIComponent(city)}`);
          const data = await res.json();

          if (data.available && weatherText) {
            weatherText.innerHTML = `
              <strong>${data.icon} ${data.city}:</strong> ${data.temperature}°C, ${data.condition}. 
              <span class="text-success ms-1"><i class="bi bi-shield-check"></i> ${data.delivery_impact}</span>
            `;
          } else if (weatherText) {
            weatherText.innerHTML = `<strong>📦 Standard Dispatch:</strong> ${data.delivery_impact || 'All packages are weather-sealed.'}`;
          }
        } catch (e) {
          if (weatherText) {
            weatherText.innerHTML = '<strong>📦 Standard Dispatch:</strong> Deliveries proceed on regular schedule.';
          }
        }
      }, 600);
    });
  }

  // Simulated Payment Option Radio switches
  const paymentRadios = document.querySelectorAll('input[name="payment_method"]');
  const cardDetailsSection = document.getElementById('simulatedCardDetails');

  paymentRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      if (cardDetailsSection) {
        if (radio.value.includes('Card')) {
          cardDetailsSection.style.display = 'block';
        } else {
          cardDetailsSection.style.display = 'none';
        }
      }
    });
  });
});
