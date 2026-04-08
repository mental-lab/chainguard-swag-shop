# E2E Testing with Playwright

## 📋 Overview

This directory contains end-to-end (E2E) tests for the Chainguard Swag Shop using [Playwright](https://playwright.dev/) for Python. These tests validate the application's functionality by running automated browser tests against a containerized version of the Flask application.

## 🏗️ Architecture

```
┌─────────────────────┐
│  Playwright Tests   │
│   (Python + pytest) │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│   Flask App         │
│ (Docker Container)  │
│   Port 8000         │
└─────────────────────┘
```

## 📁 Test Structure

```
tests/e2e/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── test_smoke.py            # Critical path smoke tests
├── test_shopping_flow.py    # Comprehensive shopping tests
└── test_cross_browser.py    # Cross-browser compatibility
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+
- Make (optional, for convenience)

### Installation

```bash
# Install E2E testing dependencies
make install-e2e

# Or manually:
pip install -r requirements-e2e.txt
playwright install
```

### Running Tests Locally


**Using Make (Recommended):**

```bash
# Run smoke tests (fastest, critical paths only)
make e2e-smoke

# Run all E2E tests
make e2e-all

# Run tests on all browsers
make e2e-cross-browser

# Run tests in debug mode (headed, slow motion)
make e2e-debug
```

**Using Docker Compose directly:**

```bash
# Start containers
docker-compose up -d

# Run tests
pytest tests/e2e/ -v --base-url=http://localhost:8000

# Stop containers
docker-compose down
```

**Manual approach:**

```bash
# Terminal 1: Start Flask app
python app.py

# Terminal 2: Run tests
pytest tests/e2e/ -v --base-url=http://localhost:8000 --browser chromium
```

## 🎯 Test Categories

### Smoke Tests (`test_smoke.py`)
Critical paths that must always work:
- ✅ Homepage loads
- ✅ Products page displays items
- ✅ Add product to cart
- ✅ Complete checkout flow
- ✅ Cart empty state

**Run smoke tests:**
```bash
pytest tests/e2e/test_smoke.py -v -m smoke
```


### Shopping Flow Tests (`test_shopping_flow.py`)
Comprehensive tests for e-commerce functionality:
- 📦 Product browsing and details
- 🛒 Cart management (add, update, remove)
- 💳 Checkout process and validation
- ✨ Multiple products handling

**Run shopping tests:**
```bash
pytest tests/e2e/test_shopping_flow.py -v
```

### Cross-Browser Tests (`test_cross_browser.py`)
Validate compatibility across browsers:
- 🌐 Chromium (Chrome/Edge)
- 🦊 Firefox
- 🧭 WebKit (Safari)

**Run cross-browser tests:**
```bash
pytest tests/e2e/ -v --browser chromium --browser firefox --browser webkit
```

## 🔧 Configuration

### Environment Variables

```bash
# Base URL for the application under test
export BASE_URL="http://localhost:8000"

# Playwright browser path (optional)
export PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Slow down operations for debugging (milliseconds)
export PLAYWRIGHT_SLOWMO=1000
```

### pytest.ini Configuration

Key Playwright settings in `pytest.ini`:
- `browser = chromium` - Default browser
- `headed = false` - Headless by default
- `screenshot = only-on-failure` - Capture on failures
- `video = retain-on-failure` - Record videos on failures
- `trace = retain-on-failure` - Generate traces for debugging


## 🐛 Debugging

### Run Tests in Headed Mode

See the browser in action:

```bash
pytest tests/e2e/test_smoke.py --headed --slowmo=1000
```

### Enable Playwright Inspector

Step through tests interactively:

```bash
PWDEBUG=1 pytest tests/e2e/test_smoke.py --headed
```

### View Trace Files

Playwright generates trace files on failure:

```bash
# After a test failure
playwright show-trace test-results/trace.zip
```

### Common Issues

**Issue: Tests fail with "Connection refused"**
```bash
# Solution: Ensure Flask app is running
docker-compose ps  # Check container status
docker-compose logs swag-shop  # Check app logs
curl http://localhost:8000/  # Test manually
```

**Issue: "Browser not installed"**
```bash
# Solution: Install Playwright browsers
playwright install
```

**Issue: Slow test execution**
```bash
# Solution: Run in headless mode without slow motion
pytest tests/e2e/ --headed=false
```

## 📊 Test Reports

### HTML Report

```bash
pytest tests/e2e/ --html=test-results/report.html --self-contained-html
open test-results/report.html
```

### JUnit XML (for CI)

```bash
pytest tests/e2e/ --junitxml=test-results/junit.xml
```


## 📝 Writing New Tests

### Test Template

```python
import pytest
from playwright.sync_api import Page, expect

def test_my_feature(page: Page, base_url: str):
    """Test description."""
    # Navigate
    page.goto(f"{base_url}/products.html")
    
    # Interact
    page.click("button")
    
    # Assert
    expect(page.locator("h1")).to_contain_text("Success")
```

### Best Practices

1. **Use semantic locators:**
   ```python
   # ✅ Good - semantic and stable
   page.click("button:has-text('Add to Cart')")
   page.locator("input[name='email']")
   
   # ❌ Bad - brittle selectors
   page.click(".btn-primary")
   page.locator("#submit-btn-123")
   ```

2. **Wait for state, not time:**
   ```python
   # ✅ Good
   page.wait_for_load_state("networkidle")
   expect(element).to_be_visible()
   
   # ❌ Bad
   time.sleep(3)
   ```

3. **Use fixtures for setup:**
   ```python
   @pytest.fixture
   def page_with_cart(page, base_url):
       page.goto(f"{base_url}/products.html")
       page.click("button:text('Add to Cart')")
       return page
   ```

4. **Mark tests appropriately:**
   ```python
   @pytest.mark.smoke  # Critical path
   @pytest.mark.e2e    # End-to-end test
   def test_checkout():
       pass
   ```


## 🎓 Useful Commands

```bash
# Run specific test
pytest tests/e2e/test_smoke.py::test_homepage_loads -v

# Run tests matching pattern
pytest tests/e2e/ -k "cart" -v

# Run tests by marker
pytest tests/e2e/ -m smoke -v

# Parallel execution (faster)
pytest tests/e2e/ -n auto

# Generate code from browser interactions
playwright codegen http://localhost:8000

# Update snapshots (for visual regression)
pytest tests/e2e/ --update-snapshots

# List all installed browsers
playwright list

# Check Playwright installation
playwright --version
```

## 📚 Resources

- [Playwright Python Docs](https://playwright.dev/python/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [GitLab CI Services](https://docs.gitlab.com/ee/ci/services/)
- [Best Practices for E2E Testing](https://playwright.dev/docs/best-practices)

## 🤝 Contributing

When adding new E2E tests:

1. Add tests to appropriate file (smoke, shopping_flow, etc.)
2. Use descriptive test names and docstrings
3. Mark tests appropriately (`@pytest.mark.smoke`, etc.)
4. Update this README if adding new test categories
5. Ensure tests pass locally before committing
6. Add to GitHub Actions workflow if new critical paths

## 📧 Support

For issues or questions about E2E testing:
- Check existing test failures in GitLab CI artifacts
- Review Playwright traces for detailed debugging
- Consult the Playwright documentation
- Ask in the team's technical channel

---

**Happy Testing! 🎭**
