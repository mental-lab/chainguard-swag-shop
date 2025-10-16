"""
Shopping Flow E2E Tests

Comprehensive tests for the complete shopping experience
including cart management, product browsing, and checkout.
"""

import pytest
import re
from playwright.sync_api import Page, expect


class TestProductBrowsing:
    """Tests for product browsing functionality."""
    
    def test_view_product_details(self, page: Page, base_url: str):
        """Test viewing individual product details."""
        page.goto(f"{base_url}/products.html")
        page.wait_for_load_state("networkidle")
        
        # Click on first product link/image
        product_link = page.locator("a[href*='product/'], .product-link").first
        product_link.click()
        
        # Should navigate to product detail page
        page.wait_for_url("**/product/*.html")
        expect(page).to_have_url(re.compile(r"product/\d+\.html"))
        
        # Verify product details are displayed
        expect(page.locator("h1, h2")).to_be_visible()
        expect(page.locator("img")).to_be_visible()
        
        # Verify add to cart button exists
        add_to_cart = page.locator("button:has-text('Add to Cart'), form[action*='add_to_cart']")
        expect(add_to_cart.first).to_be_visible()
    
    def test_products_have_images(self, page: Page, base_url: str):
        """Test that all products have valid images."""
        page.goto(f"{base_url}/products.html")
        page.wait_for_load_state("networkidle")
        
        # Get all product images
        images = page.locator("img[src*='gitlab'], .product img")
        
        # Verify at least one image exists
        assert images.count() > 0, "No product images found"
        
        # Check first image loads successfully
        first_image = images.first
        expect(first_image).to_be_visible()


class TestCartManagement:
    """Tests for shopping cart functionality."""
    
    def test_add_multiple_products(self, page: Page, base_url: str):
        """Test adding multiple different products to cart."""
        page.goto(f"{base_url}/products.html")
        page.wait_for_load_state("networkidle")
        
        # Add first product
        page.locator("form[action*='add_to_cart']").nth(0).locator("button, input[type='submit']").click()
        page.wait_for_url("**/cart.html")
        
        # Go back to products
        page.goto(f"{base_url}/products.html")
        page.wait_for_load_state("networkidle")
        
        # Add second product
        page.locator("form[action*='add_to_cart']").nth(1).locator("button, input[type='submit']").click()
        page.wait_for_url("**/cart.html")
        
        # Verify cart has 2 items
        cart_rows = page.locator("table tbody tr, .cart-item")
        assert cart_rows.count() >= 2, "Cart should contain at least 2 items"
    
    def test_update_cart_quantity(self, page: Page, base_url: str):
        """Test updating product quantity in cart."""
        # Add product to cart first
        page.goto(f"{base_url}/products.html")
        page.locator("form[action*='add_to_cart']").first.locator("button, input[type='submit']").click()
        page.wait_for_url("**/cart.html")
        
        # Find quantity input
        quantity_input = page.locator("input[name='quantity'], input[type='number']").first
        
        if quantity_input.is_visible():
            # Update quantity
            quantity_input.fill("3")
            
            # Submit update
            update_button = page.locator("button:has-text('Update'), form[action*='update_cart'] button")
            if update_button.count() > 0:
                update_button.first.click()
                page.wait_for_load_state("networkidle")
                
                # Verify flash message
                flash = page.locator(".alert")
                expect(flash).to_be_visible()
    
    def test_remove_item_from_cart(self, page: Page, base_url: str):
        """Test removing an item from cart."""
        # Add product to cart
        page.goto(f"{base_url}/products.html")
        page.locator("form[action*='add_to_cart']").first.locator("button, input[type='submit']").click()
        page.wait_for_url("**/cart.html")
        
        # Find remove button
        remove_button = page.locator("a[href*='remove_from_cart'], button:has-text('Remove')").first
        
        if remove_button.is_visible():
            initial_count = page.locator("table tbody tr, .cart-item").count()
            
            remove_button.click()
            page.wait_for_load_state("networkidle")
            
            # Verify item was removed
            new_count = page.locator("table tbody tr, .cart-item").count()
            assert new_count < initial_count, "Item was not removed from cart"


class TestCheckout:
    """Tests for checkout process."""
    
    def test_checkout_form_validation(self, page: Page, base_url: str):
        """Test checkout form requires all fields."""
        # Add item to cart and go to checkout
        page.goto(f"{base_url}/products.html")
        page.locator("form[action*='add_to_cart']").first.locator("button, input[type='submit']").click()
        page.wait_for_url("**/cart.html")
        
        page.locator("a[href*='checkout']").click()
        page.wait_for_url("**/checkout.html")
        
        # Try to submit empty form
        submit_button = page.locator("button[type='submit'], input[type='submit']")
        submit_button.click()
        
        # HTML5 validation should prevent submission
        # or Flask should show error messages
        # The page should not navigate away
        page.wait_for_timeout(1000)
        expect(page).to_have_url(re.compile(r"checkout\.html"))
    
    def test_successful_order_placement(self, page: Page, base_url: str):
        """Test successful order placement with valid data."""
        # Add item and navigate to checkout
        page.goto(f"{base_url}/products.html")
        page.locator("form[action*='add_to_cart']").first.locator("button, input[type='submit']").click()
        page.wait_for_url("**/cart.html")
        page.locator("a[href*='checkout']").click()
        page.wait_for_url("**/checkout.html")
        
        # Fill form with valid data
        page.fill("input[name='name']", "John Doe")
        page.fill("input[name='email']", "john.doe@example.com")
        page.fill("input[name='address'], textarea[name='address']", "123 Main St, City, State 12345")
        
        # Submit order
        page.locator("button[type='submit'], input[type='submit']").click()
        page.wait_for_load_state("networkidle")
        
        # Verify success message
        flash = page.locator(".alert, .flash-message")
        expect(flash).to_contain_text(re.compile(r"order|success|thank", re.IGNORECASE))
