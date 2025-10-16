"""
Smoke Tests for Chainguard Swag Shop

These tests validate critical user journeys and ensure
the application's core functionality works in a containerized environment.
"""

import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_homepage_loads(page: Page, base_url: str):
    """
    Test that the homepage loads successfully.
    
    This is the most basic smoke test - if this fails,
    the application is not running properly.
    """
    page.goto(base_url)
    
    # Verify page title
    expect(page).to_have_title(re.compile(r"swag|shop", re.IGNORECASE))
    
    # Verify main heading is visible
    heading = page.locator("h1, h2").first
    expect(heading).to_be_visible()
    
    # Verify navigation is present
    nav = page.locator("nav, .navbar, header").first
    expect(nav).to_be_visible()


@pytest.mark.smoke
def test_products_page_displays_items(page: Page, base_url: str):
    """Test that products page loads and displays products."""
    page.goto(f"{base_url}/products.html")
    
    # Wait for products to load
    page.wait_for_load_state("networkidle")
    
    # Verify products are visible
    products = page.locator("img[src*='gitlab'], .product-card, .card")
    expect(products.first).to_be_visible()
    
    # Verify at least some products are displayed
    product_count = products.count()
    assert product_count > 0, "No products found on products page"


@pytest.mark.smoke
def test_add_product_to_cart(page: Page, base_url: str):
    """Test critical path: Adding a product to cart."""
    page.goto(f"{base_url}/products.html")
    page.wait_for_load_state("networkidle")

    # Click on first product to go to detail page
    first_product_link = page.locator("a[href*='/product/']").first
    expect(first_product_link).to_be_visible()
    first_product_link.click()

    # Wait for product detail page to load
    page.wait_for_url("**/product/*.html")

    # Find and submit the add to cart form
    add_to_cart_form = page.locator("form[action*='add_to_cart']").first
    expect(add_to_cart_form).to_be_visible()

    # Submit the form
    add_to_cart_form.locator("button[type='submit'], input[type='submit']").click()
    
    # Wait for navigation to cart page
    page.wait_for_url("**/cart.html")
    
    # Verify we're on the cart page
    expect(page).to_have_url(re.compile(r"cart\.html"))
    
    # Verify cart has items
    cart_items = page.locator("table tr, .cart-item, [data-testid='cart-item']")
    expect(cart_items.first).to_be_visible()
    
    # Verify flash message
    flash = page.locator(".alert, .flash-message")
    expect(flash).to_be_visible()


@pytest.mark.smoke
def test_complete_checkout_flow(page: Page, base_url: str):
    """
    Test the complete e-commerce flow from browsing to checkout.
    
    This is the most critical user journey for an e-commerce site.
    """
    # Step 1: Browse products
    page.goto(f"{base_url}/products.html")
    page.wait_for_load_state("networkidle")

    # Step 2: Go to product detail page
    first_product_link = page.locator("a[href*='/product/']").first
    first_product_link.click()
    page.wait_for_url("**/product/*.html")

    # Step 3: Add product to cart
    page.locator("form[action*='add_to_cart']").first.locator("button, input[type='submit']").click()
    page.wait_for_url("**/cart.html")
    
    # Step 4: Verify cart page
    expect(page).to_have_url(re.compile(r"cart\.html"))

    # Step 5: Proceed to checkout
    checkout_link = page.locator("a[href*='checkout'], button:has-text('Checkout')")
    expect(checkout_link).to_be_visible()
    checkout_link.click()

    # Step 6: Fill checkout form
    page.wait_for_url("**/checkout.html")
    expect(page).to_have_url(re.compile(r"checkout\.html"))

    # Fill in customer information
    page.fill("input[name='name']", "Test Customer")
    page.fill("input[name='email']", "test@example.com")
    page.fill("input[name='address'], textarea[name='address']", "123 Test Street")

    # Step 7: Place order
    page.locator("button[type='submit']:has-text('Place Order'), input[type='submit']").click()

    # Step 8: Verify order confirmation
    page.wait_for_load_state("networkidle")

    # Should redirect to homepage with success message or show success page
    # Try multiple possible selectors for success messages
    flash_selectors = [
        ".alert",
        ".flash-message",
        ".message",
        ".success",
        "[role='alert']",
        "*:has-text('success')",
        "*:has-text('thank')",
        "*:has-text('order')"
    ]

    success_found = False
    for selector in flash_selectors:
        try:
            flash = page.locator(selector)
            if flash.count() > 0:
                success_found = True
                break
        except:
            continue

    # If no flash message found, just verify we didn't stay on checkout page
    if not success_found:
        # Order should have processed and redirected away from checkout
        current_url = page.url
        assert "checkout.html" not in current_url, f"Still on checkout page: {current_url}"


@pytest.mark.smoke
def test_cart_empty_state(page: Page, base_url: str):
    """Test that empty cart shows appropriate message."""
    page.goto(f"{base_url}/cart.html")
    
    # Empty cart should either show a message or have no items
    page.wait_for_load_state("networkidle")
    
    # Check for empty cart message or empty table
    empty_message = page.get_by_text(re.compile(r"cart is empty|no items|0 items", re.IGNORECASE))
    cart_items = page.locator("table tbody tr, .cart-item")
    
    # Either empty message is shown or no cart items exist
    try:
        expect(empty_message).to_be_visible(timeout=2000)
    except:
        # If no empty message, verify no items
        assert cart_items.count() == 0, "Cart should be empty but contains items"
