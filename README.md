# Chainguard Swag Shop

A simple e-commerce demo website built with Flask and Python. Browse products, add items to your cart, and complete purchases in this demo shop.

🚧 **Work in Progress** - Not for production use.
## Quick Start

### Option 1: Using Docker (Recommended)
```bash
docker build -t swag-shop .
docker run -p 8000:8000 swag-shop
```

### Option 2: Local Development
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Then open your browser to <http://127.0.0.1:8000/>

## Using the Makefile

This project includes a Makefile for common tasks. To see all available targets, run:

```bash
make help
```

### Key Targets

- `make install`: Create virtual environment and install dependencies from requirements.txt.
- `make develop`: Run the Flask app locally.
- `make switch-cgr`: Switch to using Chainguard PyPI as primary and reinstall dependencies (requires authentication).
- `make show-provenance`: Fetch and display provenance for packages in requirements.txt (requires authentication).
- `make e2e-up`: Start Docker services for end-to-end testing.
- `make e2e-smoke`: Run smoke tests.

For more details, see the Makefile comments or run `make help`.

## Setting up Authentication

To use Chainguard remediated packages or fetch provenance, you need to set up authentication via `.netrc`.

1. Create or edit `~/.netrc` (on macOS/Linux) or `%HOME%\_netrc`.

2. Add the following entry (replace `<username>` and `<token>` with your Chainguard credentials):

```
machine libraries.cgr.dev
login <username>
password <token>
```

3. Ensure the file has permissions `600` (readable only by owner):

```bash
chmod 600 ~/.netrc
```

This allows commands like `make switch-cgr` and `make show-provenance` to authenticate with the Chainguard repository.

## Features

- Browse products with images and descriptions
- Add items to shopping cart
- View cart contents and totals
- Complete checkout process
- Responsive design for mobile and desktop

## Contributing

Found a bug or want to add a feature? Feel free to open an issue or submit a pull request!
