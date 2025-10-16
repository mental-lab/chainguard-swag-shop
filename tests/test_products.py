"""
Product-related tests using pytest.

Tests the product retrieval functionality and Product model behavior.
"""

import pytest
from db import get_product_by_id, get_products, Product
from config import BRAND_NAME


class TestProductRetrieval:
    """Tests for product retrieval functions."""

    def test_get_existing_product_first(self):
        """Test retrieving the first product in the catalog."""
        product = get_product_by_id(1)

        assert product is not None
        assert product.id == 1
        assert product.name == f"{BRAND_NAME} Softstyle V-Neck Tee"
        assert product.price == 20.00
        assert product.category == "Clothing"

    def test_get_existing_product_middle(self):
        """Test retrieving a middle product in the catalog."""
        product = get_product_by_id(8)

        assert product is not None
        assert product.id == 8
        assert product.name == f"{BRAND_NAME} Adult Cotton Hat"
        assert product.price == 20.00
        assert product.category == "Accessories"

    def test_get_existing_product_last(self):
        """Test retrieving the last product in the catalog."""
        product = get_product_by_id(18)

        assert product is not None
        assert product.id == 18
        assert product.name == f"{BRAND_NAME} Lapel Pin 2 pack"
        assert product.price == 10.00
        assert product.category == "Accessories"

    @pytest.mark.parametrize("product_id", [0, 100, 999, -1, -5])
    def test_get_nonexistent_product_ids(self, product_id):
        """Test retrieving products with IDs that don't exist."""
        product = get_product_by_id(product_id)
        assert product is None

    @pytest.mark.parametrize("invalid_id", ["1", "abc", 1.5, None, [], {}])
    def test_get_product_with_invalid_id_types(self, invalid_id):
        """Test retrieving products with invalid ID types."""
        product = get_product_by_id(invalid_id)
        assert product is None


class TestProductCatalog:
    """Tests for the complete product catalog."""

    def test_get_all_products(self):
        """Test retrieving all products returns expected count."""
        products = get_products()

        assert len(products) == 18
        assert all(isinstance(product, Product) for product in products)

    def test_product_ids_are_unique(self):
        """Test that all product IDs in catalog are unique."""
        products = get_products()
        product_ids = [product.id for product in products]

        assert len(product_ids) == len(set(product_ids))

    def test_all_products_have_required_fields(self):
        """Test that all products have required fields populated."""
        products = get_products()

        for product in products:
            assert product.id is not None
            assert product.name is not None and len(product.name.strip()) > 0
            assert product.description is not None
            assert product.price is not None and product.price >= 0
            assert product.image_url is not None and len(product.image_url.strip()) > 0
            assert product.category is not None and len(product.category.strip()) > 0

    def test_product_categories(self):
        """Test that products have expected categories."""
        products = get_products()
        categories = {product.category for product in products}

        expected_categories = {"Clothing", "Accessories"}
        assert categories == expected_categories

    def test_price_ranges(self):
        """Test that product prices are within reasonable ranges."""
        products = get_products()
        prices = [product.price for product in products]

        assert min(prices) >= 0
        assert max(prices) <= 100  # Reasonable upper bound for swag items
        assert all(isinstance(price, (int, float)) for price in prices)


class TestProductModel:
    """Tests for the Product model class."""

    def test_product_creation(self):
        """Test creating a Product instance."""
        product = Product(
            id=999,
            name="Test Product",
            description="Test Description",
            price=15.99,
            image_url="https://example.com/test.jpg",
            category="Test"
        )

        assert product.id == 999
        assert product.name == "Test Product"
        assert product.description == "Test Description"
        assert product.price == 15.99
        assert product.image_url == "https://example.com/test.jpg"
        assert product.category == "Test"

    def test_product_string_representation(self):
        """Test that Product has some string representation."""
        product = Product(1, "Test", "Desc", 10.0, "url", "Cat")

        # Product class might not have __str__ method, but should at least not crash
        str_repr = str(product)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0


# Test fixtures for more complex testing scenarios
@pytest.fixture
def sample_product():
    """Fixture providing a sample product for testing."""
    return Product(
        id=100,
        name=f"Sample {BRAND_NAME} Product",
        description="A sample product for testing",
        price=25.00,
        image_url="https://example.com/sample.jpg",
        category="Test"
    )


@pytest.fixture
def product_catalog():
    """Fixture providing the current product catalog."""
    return get_products()


class TestProductFixtures:
    """Tests using pytest fixtures."""

    def test_sample_product_fixture(self, sample_product):
        """Test using the sample product fixture."""
        assert sample_product.name == f"Sample {BRAND_NAME} Product"
        assert sample_product.price == 25.00

    def test_catalog_fixture(self, product_catalog):
        """Test using the product catalog fixture."""
        assert len(product_catalog) > 0
        assert all(hasattr(product, 'id') for product in product_catalog)
