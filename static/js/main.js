/**
 * MysteryMart — Core Client-side Scripts
 * Cart updates, toasts, search bar interactions, and smooth transitions
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Navbar Scrolled Shadow
  const navbar = document.querySelector('.mm-navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // 2. AJAX Add-to-Cart Buttons
  const addToCartForms = document.querySelectorAll('.ajax-add-to-cart');
  addToCartForms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.innerHTML : '';
      
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Adding...';
      }

      const formData = new FormData(form);
      const payload = {
        product_id: formData.get('product_id'),
        quantity: formData.get('quantity') || 1
      };

      try {
        const response = await fetch('/cart/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok && data.success) {
          // Update cart badge everywhere
          const cartBadges = document.querySelectorAll('.cart-badge');
          cartBadges.forEach(badge => {
            badge.textContent = data.item_count;
            badge.classList.add('animate__animated', 'animate__rubberBand');
          });

          showToast('Success', data.message || 'Added to mystery cart!', 'success');
        } else {
          showToast('Notice', data.message || 'Could not add product', 'warning');
        }
      } catch (err) {
        console.error('Add to cart failed:', err);
        showToast('Error', 'Connection issue. Please retry.', 'danger');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }
      }
    });
  });

  // 3. Auto-dismiss alerts after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {}
    }, 6000);
  });
});

/**
 * Global dynamic toast notification
 */
function showToast(title, message, type = 'info') {
  let toastContainer = document.getElementById('mm-toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'mm-toast-container';
    toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
    toastContainer.style.zIndex = '1090';
    document.body.appendChild(toastContainer);
  }

  const bgClass = type === 'success' ? 'bg-success text-white' :
                  type === 'danger' ? 'bg-danger text-white' :
                  type === 'warning' ? 'bg-warning text-dark' : 'bg-primary text-white';

  const toastId = 'toast_' + Math.random().toString(36).substr(2, 9);
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : type === 'danger' ? 'bi-exclamation-triangle-fill' : 'bi-info-circle-fill'}"></i>
          <div>
            <strong>${title}:</strong> ${message}
          </div>
        </div>
        <button type="button" class="btn-close ${type === 'warning' ? '' : 'btn-close-white'} me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  const toastEl = document.getElementById(toastId);
  if (toastEl && window.bootstrap) {
    const toast = new bootstrap.Toast(toastEl, { delay: 4500 });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
  }
}
