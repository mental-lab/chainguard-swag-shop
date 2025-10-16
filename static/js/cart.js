// JavaScript for main functionality

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', function() {
            mainNav.classList.toggle('active');
        });
    }
    
    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.display = 'none';
            }, 4000); // Hide messages after 4 seconds
        });
    }
    
    // Quantity controls in product detail page
    const quantityInput = document.getElementById('quantity');
    const minusButton = document.querySelector('.quantity-button.minus');
    const plusButton = document.querySelector('.quantity-button.plus');
    
    if (quantityInput && minusButton && plusButton) {
        minusButton.addEventListener('click', function() {
            if (quantityInput.value > 1) {
                quantityInput.value = parseInt(quantityInput.value) - 1;
            }
        });
        
        plusButton.addEventListener('click', function() {
            if (quantityInput.value < 12) {
                quantityInput.value = parseInt(quantityInput.value) + 1;
            }
        });
    }
    
    // Quantity controls in cart page
    const updateForms = document.querySelectorAll('.update-quantity-form');
    
    if (updateForms.length > 0) {
        updateForms.forEach(form => {
            const input = form.querySelector('input[type="number"]');
            const minusBtn = form.querySelector('.quantity-button.minus');
            const plusBtn = form.querySelector('.quantity-button.plus');
            
            if (input && minusBtn && plusBtn) {
                minusBtn.addEventListener('click', function() {
                    if (input.value > 1) {
                        input.value = parseInt(input.value) - 1;
                    }
                });
                
                plusBtn.addEventListener('click', function() {
                    if (input.value < 12) {
                        input.value = parseInt(input.value) + 1;
                    }
                });
            }
        });
    }
    
    // Radio toggle for pickup/delivery in checkout
    const pickupRadio = document.getElementById('pickup');
    const deliveryRadio = document.getElementById('delivery');
    const pickupOptions = document.getElementById('pickup-options');
    const deliveryOptions = document.getElementById('delivery-options');
    const deliveryFeeLine = document.getElementById('delivery-fee-line');
    const orderTotal = document.getElementById('order-total');
    
    if (pickupRadio && deliveryRadio && pickupOptions && deliveryOptions) {
        pickupRadio.addEventListener('change', function() {
            if (this.checked) {
                pickupOptions.classList.remove('hidden');
                deliveryOptions.classList.add('hidden');
                
                if (deliveryFeeLine && orderTotal) {
                    deliveryFeeLine.classList.add('hidden');
                    updateTotal(false);
                }
            }
        });
        
        deliveryRadio.addEventListener('change', function() {
            if (this.checked) {
                pickupOptions.classList.add('hidden');
                deliveryOptions.classList.remove('hidden');
                
                if (deliveryFeeLine && orderTotal) {
                    deliveryFeeLine.classList.remove('hidden');
                    updateTotal(true);
                }
            }
        });
        
        function updateTotal(includeDelivery) {
            if (!orderTotal) return;
            
            const subtotalText = document.querySelector('.summary-line:first-child span:last-child').textContent;
            const subtotal = parseFloat(subtotalText.replace('
```
, ''));
            
            const taxText = document.querySelector('.summary-line:nth-child(2) span:last-child').textContent;
            const tax = parseFloat(taxText.replace('
```
, ''));
            
            let total = subtotal + tax;
            
            if (includeDelivery) {
                const deliveryFeeText = deliveryFeeLine.querySelector('span:last-child').textContent;
                const deliveryFee = parseFloat(deliveryFeeText.replace('
```
, ''));
                total += deliveryFee;
            }
            
            orderTotal.textContent = '
```
 + total.toFixed(2);
        }
    }
    
    // Email validation for subscription form
    const subscribeForms = document.querySelectorAll('.subscribe-form, .subscribe-form-banner');
    
    if (subscribeForms.length > 0) {
        subscribeForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const emailInput = this.querySelector('input[type="email"]');
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                
                if (!emailRegex.test(emailInput.value)) {
                    e.preventDefault();
                    alert('Please enter a valid email address.');
                }
            });
        });
    }
    
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    if (anchorLinks.length > 0) {
        anchorLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                
                if (targetId === '#') return;
                
                e.preventDefault();
                
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
});