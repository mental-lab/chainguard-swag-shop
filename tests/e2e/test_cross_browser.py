"""
Cross-Browser Compatibility Tests

Tests that verify the application works correctly
across different browsers (Chromium, Firefox, WebKit).

Usage:
    pytest tests/e2e/test_cross_browser.py --browser chromium --browser firefox --browser webkit

Note: browser_name parameter is automatically provided by pytest-playwright
      based on --browser CLI flags. No @pytest.mark.parametrize needed.
"""

import pytest
import re
from playwright.sync_api import Page, expect


class TestCrossBrowserCompatibility:
    """Tests run across all major browsers.

    The browser_name parameter in test methods is automatically injected
    by pytest-playwright based on the --browser CLI flags used.
    """
    
    def test_homepage_renders_correctly(self, page: Page, base_url: str, browser_name: str):
        """Test homepage renders in all browsers."""
        page.goto(base_url)
        
        # Basic rendering checks
        expect(page.locator("body")).to_be_visible()
        expect(page.locator("nav, header")).to_be_visible()
        
    def test_shopping_flow_works(self, page: Page, base_url: str, browser_name: str):
        """Test basic shopping flow in all browsers."""
        # Navigate to products
        page.goto(f"{base_url}/products.html")
        page.wait_for_load_state("networkidle")
        
        # Add to cart
        page.locator("form[action*='add_to_cart']").first.locator("button, input[type='submit']").click()
        page.wait_for_url("**/cart.html")
        
        # Verify cart page loads
        expect(page).to_have_url(re.compile(r"cart\.html"))
