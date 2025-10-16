"""
Pytest configuration and shared fixtures for Chainguard Swag Shop tests.

This file contains fixtures and configuration that are available
to all test files in the tests/ directory.
"""

import pytest
import tempfile
import os
from app import app
from db import get_products, Product


@pytest.fixture(scope='session')
def test_app():
    """Create and configure a test Flask application."""
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain'
    })

    return app


@pytest.fixture(scope='function')
def client(test_app):
    """Create a test client for the Flask application."""
    with test_app.test_client() as client:
        with test_app.app_context():
            yield client


@pytest.fixture(scope='function')
def app_context(test_app):
    """Create an application context for testing."""
    with test_app.app_context():
        yield test_app


@pytest.fixture
def empty_cart_session(client):
    """Client with an empty cart session."""
    with client.session_transaction() as sess:
        sess['cart'] = []
    return client


@pytest.fixture
def cart_with_items(client):
    """Client with a cart containing test items."""
    with client.session_transaction() as sess:
        sess['cart'] = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 8, 'quantity': 1}
        ]
    return client


@pytest.fixture
def sample_products():
    """Sample product data for testing."""
    return [
        Product(1, "Test Product 1", "Description 1", 10.0, "http://example.com/1.jpg", "Test"),
        Product(2, "Test Product 2", "Description 2", 20.0, "http://example.com/2.jpg", "Test"),
        Product(3, "Test Product 3", "Description 3", 30.0, "http://example.com/3.jpg", "Test")
    ]


@pytest.fixture(scope='session')
def product_catalog():
    """The actual product catalog for reference."""
    return get_products()


@pytest.fixture
def valid_order_data():
    """Valid order form data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'address': '123 Main St, City, State 12345'
    }


@pytest.fixture
def invalid_order_data():
    """Invalid order form data for testing."""
    return {
        'name': '',
        'email': 'invalid-email',
        'address': ''
    }


# Pytest hooks and configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security-focused"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API-focused"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location and name."""
    for item in items:
        # Auto-mark tests based on filename patterns
        if "test_app.py" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_products.py" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Auto-mark slow tests
        if "performance" in item.name.lower() or "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)

        # Auto-mark security tests
        if "security" in item.name.lower() or "xss" in item.name.lower() or "injection" in item.name.lower():
            item.add_marker(pytest.mark.security)


@pytest.fixture(autouse=True)
def reset_application_state():
    """Reset application state before each test."""
    # This fixture runs automatically before each test
    # Add any cleanup or reset logic here if needed
    yield
    # Cleanup after test if needed


# Custom assertions for better test readability
class ProductAssertions:
    """Custom assertions for product testing."""

    @staticmethod
    def assert_valid_product(product):
        """Assert that a product has all required valid fields."""
        assert product is not None
        assert hasattr(product, 'id')
        assert hasattr(product, 'name')
        assert hasattr(product, 'description')
        assert hasattr(product, 'price')
        assert hasattr(product, 'image_url')
        assert hasattr(product, 'category')

        assert product.id is not None
        assert isinstance(product.name, str) and len(product.name.strip()) > 0
        assert isinstance(product.price, (int, float)) and product.price >= 0
        assert isinstance(product.image_url, str) and len(product.image_url.strip()) > 0
        assert isinstance(product.category, str) and len(product.category.strip()) > 0

    @staticmethod
    def assert_valid_response(response, expected_status=200):
        """Assert that a response is valid."""
        assert response.status_code == expected_status
        assert response.data is not None


@pytest.fixture
def product_assertions():
    """Provide custom assertion helpers."""
    return ProductAssertions


# Performance testing utilities
@pytest.fixture
def timing_context():
    """Context manager for timing operations."""
    class TimingContext:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.duration = None

        def __enter__(self):
            import time
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            import time
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time

        def assert_duration_less_than(self, max_duration):
            """Assert that the timed operation took less than max_duration seconds."""
            assert self.duration is not None, "Timing context was not used properly"
            assert self.duration < max_duration, f"Operation took {self.duration:.3f}s, expected < {max_duration}s"

    return TimingContext
