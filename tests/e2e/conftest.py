"""
Pytest configuration and fixtures for E2E tests using Playwright.

This configuration is specific to E2E tests running against
a containerized Flask application.
"""

import pytest
import os
import time
from playwright.sync_api import Page, expect
from typing import Generator


# Environment configuration
@pytest.fixture(scope="session")
def base_url() -> str:
    """Get base URL from environment or use default."""
    return os.getenv("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "record_video_dir": "test-results/videos/",
        "record_video_size": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="function")
def page(page: Page, base_url: str) -> Generator[Page, None, None]:
    """Configure page with base URL and common settings."""
    # Set default timeout
    page.set_default_timeout(30000)  # 30 seconds
    
    # Set base URL for navigation
    page.context.base_url = base_url
    
    yield page
    
    # Cleanup: Take screenshot on failure
    # (handled by pytest-playwright automatically)


@pytest.fixture(scope="function")
def authenticated_page(page: Page, base_url: str) -> Page:
    """Page with authenticated session (if needed in the future)."""
    # Currently, swag-shop doesn't have authentication
    # This fixture is here for future use
    return page


@pytest.fixture(scope="function")
def page_with_cart(page: Page, base_url: str) -> Page:
    """Page with items already added to cart."""
    page.goto(f"{base_url}/products.html")
    
    # Add first product to cart
    page.locator(".add-to-cart").first.click()
    
    # Wait for cart update
    page.wait_for_timeout(500)
    
    return page


# Helper function fixtures
@pytest.fixture
def wait_for_app_ready(base_url: str):
    """Wait for the Flask app to be ready."""
    def wait():
        import requests
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(base_url, timeout=2)
                if response.status_code == 200:
                    return True
            except (requests.ConnectionError, requests.Timeout):
                pass
            time.sleep(1)
        raise RuntimeError(f"Flask app not ready after {max_attempts} seconds")
    
    return wait


# Custom assertions for E2E tests
class E2EAssertions:
    """Custom assertions specific to swag-shop E2E tests."""
    
    @staticmethod
    def assert_product_card_visible(page: Page):
        """Assert that product cards are visible on the page."""
        product_cards = page.locator(".product-card, .card, [data-testid='product']")
        expect(product_cards.first).to_be_visible()
    
    @staticmethod
    def assert_cart_count(page: Page, expected_count: int):
        """Assert cart badge shows expected count."""
        cart_badge = page.locator(".cart-count, .badge, [data-testid='cart-count']")
        if expected_count > 0:
            expect(cart_badge).to_contain_text(str(expected_count))
    
    @staticmethod
    def assert_flash_message(page: Page, message_text: str):
        """Assert flash message is displayed."""
        flash_msg = page.locator(".alert, .flash, [data-testid='flash-message']")
        expect(flash_msg).to_contain_text(message_text)


@pytest.fixture
def e2e_assertions():
    """Provide E2E-specific assertion helpers."""
    return E2EAssertions


# Pytest configuration for E2E tests
def pytest_configure(config):
    """Configure pytest markers for E2E tests."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test (critical paths)"
    )
    config.addinivalue_line(
        "markers", "visual: mark test for visual regression testing"
    )
    config.addinivalue_line(
        "markers", "performance: mark test for performance testing"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark all tests in e2e/ directory as e2e tests."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
