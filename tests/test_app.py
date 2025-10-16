"""
Flask application tests using pytest.

Tests the web application routes, cart functionality, and session management.
"""

import pytest
from app import app
from db import get_product_by_id, get_products


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def client_with_session(client):
    """Create a test client with a session context."""
    with client.session_transaction() as sess:
        sess['cart'] = []
    return client


class TestHomePage:
    """Tests for the home page route."""

    def test_home_page_loads(self, client):
        """Test that the home page loads successfully."""
        response = client.get('/')

        assert response.status_code == 200
        assert b'Chainguard Swag Shop' in response.data
        # Check for the Featured Products section heading
        assert b'Featured Products' in response.data

    def test_home_page_shows_products(self, client):
        """Test that the home page displays featured products."""
        response = client.get('/')

        assert response.status_code == 200
        # Should show at least one featured product name
        first_product = get_products()[0]
        assert first_product.name.encode('utf-8') in response.data


class TestProductPages:
    """Tests for product-related routes."""

    def test_products_page_loads(self, client):
        """Test that the products page loads successfully."""
        response = client.get('/products.html')

        assert response.status_code == 200
        assert b'products' in response.data.lower()

    def test_product_detail_existing(self, client):
        """Test viewing an existing product detail page."""
        response = client.get('/product/1.html')

        assert response.status_code == 200
        prod = get_product_by_id(1)
        assert prod.name.encode('utf-8') in response.data

    def test_product_detail_nonexistent(self, client):
        """Test viewing a non-existent product redirects."""
        response = client.get('/product/999.html')

        assert response.status_code == 302  # Redirect to products page

        # Follow redirect
        response = client.get('/product/999.html', follow_redirects=True)
        assert b'Product not found' in response.data

    @pytest.mark.parametrize("product_id", [1, 8, 18])
    def test_multiple_product_details(self, client, product_id):
        """Test multiple product detail pages load correctly."""
        response = client.get(f'/product/{product_id}.html')

        assert response.status_code == 200

        # Get expected product name
        product = get_product_by_id(product_id)
        expected_name = product.name.encode('utf-8')
        assert expected_name in response.data


class TestCartFunctionality:
    """Tests for shopping cart functionality."""

    def test_cart_page_empty(self, client):
        """Test viewing an empty cart."""
        response = client.get('/cart.html')

        assert response.status_code == 200
        assert b'cart' in response.data.lower()

    def test_add_to_cart_valid_product(self, client_with_session):
        """Test adding a valid product to cart."""
        response = client_with_session.post('/add_to_cart.html', data={
            'product_id': '1',
            'quantity': '2'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Added' in response.data or b'cart' in response.data.lower()

    def test_add_to_cart_invalid_product(self, client_with_session):
        """Test adding an invalid product to cart."""
        response = client_with_session.post('/add_to_cart.html', data={
            'product_id': '999',
            'quantity': '1'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Product not found' in response.data

    def test_cart_quantity_update(self, client_with_session):
        """Test updating cart item quantity."""
        # First add an item
        client_with_session.post('/add_to_cart.html', data={
            'product_id': '1',
            'quantity': '1'
        })

        # Then update quantity
        response = client_with_session.post('/update_cart.html', data={
            'product_id': '1',
            'quantity': '3'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_remove_from_cart(self, client_with_session):
        """Test removing an item from cart."""
        # First add an item
        client_with_session.post('/add_to_cart.html', data={
            'product_id': '1',
            'quantity': '1'
        })

        # Then remove it
        response = client_with_session.get('/remove_from_cart/1', follow_redirects=True)

        assert response.status_code == 200
        assert b'removed' in response.data.lower()


class TestCheckoutProcess:
    """Tests for checkout functionality."""

    def test_checkout_empty_cart_redirects(self, client_with_session):
        """Test that checkout with empty cart redirects."""
        response = client_with_session.get('/checkout.html')

        assert response.status_code == 302  # Should redirect

        response = client_with_session.get('/checkout.html', follow_redirects=True)
        assert b'empty' in response.data.lower()

    def test_checkout_with_items(self, client_with_session):
        """Test checkout page with items in cart."""
        # Add item to cart first
        client_with_session.post('/add_to_cart.html', data={
            'product_id': '1',
            'quantity': '1'
        })

        response = client_with_session.get('/checkout.html')

        assert response.status_code == 200
        assert b'checkout' in response.data.lower()

    def test_place_order(self, client_with_session):
        """Test placing an order."""
        # Add item to cart first
        client_with_session.post('/add_to_cart.html', data={
            'product_id': '1',
            'quantity': '1'
        })

        # Place order
        response = client_with_session.post('/place_order.html', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'address': '123 Test St'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Order placed successfully' in response.data


class TestSessionManagement:
    """Tests for session handling."""

    def test_session_cart_persistence(self, client):
        """Test that cart persists in session across requests."""
        with client.session_transaction() as sess:
            sess['cart'] = [{'product_id': 1, 'quantity': 2}]

        response = client.get('/cart.html')
        assert response.status_code == 200

    def test_session_cart_initialization(self, client):
        """Test that cart is initialized in session."""
        # Make any request to trigger before_request
        client.get('/')

        with client.session_transaction() as sess:
            assert 'cart' in sess
            assert isinstance(sess['cart'], list)


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_invalid_routes_404(self, client):
        """Test that invalid routes return 404."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

    def test_post_to_get_only_routes(self, client):
        """Test POST requests to GET-only routes."""
        response = client.post('/')
        assert response.status_code == 405  # Method not allowed

    @pytest.mark.parametrize("route", ['/cart.html', '/products.html', '/'])
    def test_routes_accept_get(self, client, route):
        """Test that various routes accept GET requests."""
        response = client.get(route)
        assert response.status_code in [200, 302]  # 200 OK or 302 redirect


@pytest.mark.slow
class TestPerformance:
    """Performance-related tests."""

    def test_home_page_response_time(self, client):
        """Test that home page responds quickly."""
        import time

        start_time = time.time()
        response = client.get('/')
        end_time = time.time()

        assert response.status_code == 200
        assert end_time - start_time < 1.0  # Should respond in under 1 second

    def test_product_page_response_time(self, client):
        """Test that product pages respond quickly."""
        import time

        start_time = time.time()
        response = client.get('/products.html')
        end_time = time.time()

        assert response.status_code == 200
        assert end_time - start_time < 1.0
