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
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

Then open your browser to <http://127.0.0.1:8000/>

## Features

- Browse products with images and descriptions
- Add items to shopping cart
- View cart contents and totals
- Complete checkout process
- Responsive design for mobile and desktop

## Contributing

Found a bug or want to add a feature? Feel free to open an issue or submit a pull request!
