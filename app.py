from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
from db import Product, get_products, get_product_by_id
from config import BRAND_NAME

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production
# for the freezer.py
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_IGNORE_404_NOT_FOUND'] = True

# Initialize session cart if it doesn't exist
@app.before_request
def before_request():
    if 'cart' not in session:
        session['cart'] = []

@app.route('/')
def index():
    featured_products = get_products()[:6]  # Get first 4 products as featured
    return render_template('index.html', featured_products=featured_products)

@app.route('/products.html')
def products():
    all_products = get_products()
    return render_template('products.html', products=all_products)

@app.route('/product/<int:product_id>.html')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found')
        return redirect(url_for('products'))
    return render_template('product_detail.html', product=product, product_detail=True)

@app.route('/cart.html')
def cart():
    cart_items = []
    total = 0
    for item in session['cart']:
        product = get_product_by_id(item['product_id'])
        if product:
            quantity = item['quantity']
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart.html', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))
    
    # Check if product exists
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found')
        return redirect(url_for('products'))
    
    # Check if product is already in cart
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            session.modified = True
            flash(f'Added {quantity} more to your cart')
            return redirect(url_for('cart'))
    
    # If not in cart, add it
    cart.append({'product_id': product_id, 'quantity': quantity})
    session.modified = True
    flash(f'Added {product.name} to your cart')
    return redirect(url_for('cart'))

@app.route('/update_cart.html', methods=['POST'])
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    
    # Update cart item quantity
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id:
            if quantity <= 0:
                cart.remove(item)
                flash('Item removed from cart')
            else:
                item['quantity'] = quantity
                flash('Cart updated')
            session.modified = True
            break
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id:
            cart.remove(item)
            session.modified = True
            flash('Item removed from cart')
            break
    return redirect(url_for('cart'))

@app.route('/checkout.html')
def checkout():
    if not session['cart']:
        flash('Your cart is empty')
        return redirect(url_for('products'))
    
    cart_items = []
    total = 0
    for item in session['cart']:
        product = get_product_by_id(item['product_id'])
        if product:
            quantity = item['quantity']
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/place_order.html', methods=['POST'])
def place_order():
    # In a real application, you would process payment and store order in database
    # For this example, we'll just clear the cart and show a confirmation
    name = request.form.get('name')
    email = request.form.get('email')
    address = request.form.get('address')
    
    # Clear the cart
    session['cart'] = []
    session.modified = True
    
    flash(f'Order placed successfully! Thank you, {name}.')
    return redirect(url_for('index'))


@app.route('/demo/')
def demo_hub():
    """Pre-sales Demo Hub landing page."""
    return render_template('demo_hub.html')


@app.route('/demo/container-security.html')
def demo_container_security():
    """Container CVE comparison: standard python:3.12-slim vs cgr.dev/chainguard/python."""
    standard_image = {
        'name': 'python:3.12-slim',
        'total_cves': 57,
        'critical': 3,
        'high': 14,
        'medium': 28,
        'low': 12,
        'cves': [
            {'id': 'CVE-2024-6119', 'severity': 'CRITICAL', 'package': 'openssl', 'version': '3.0.13-1', 'description': 'OpenSSL possible denial of service in X.509 name checks'},
            {'id': 'CVE-2024-5535', 'severity': 'CRITICAL', 'package': 'openssl', 'version': '3.0.13-1', 'description': 'OpenSSL SSL_select_next_proto buffer overread'},
            {'id': 'CVE-2023-6129', 'severity': 'CRITICAL', 'package': 'openssl', 'version': '3.0.13-1', 'description': 'OpenSSL POLY1305 MAC implementation corrupts vector registers'},
            {'id': 'CVE-2024-2004', 'severity': 'HIGH', 'package': 'curl', 'version': '7.88.1-10+deb12u6', 'description': 'curl unused SSH_FILETYPE_UNKNOWN protocol option ignored'},
            {'id': 'CVE-2024-2398', 'severity': 'HIGH', 'package': 'curl', 'version': '7.88.1-10+deb12u6', 'description': 'curl HTTP/2 push headers memory-leak'},
            {'id': 'CVE-2023-38545', 'severity': 'HIGH', 'package': 'curl', 'version': '7.88.1-10+deb12u6', 'description': 'curl SOCKS5 heap buffer overflow'},
            {'id': 'CVE-2024-0567', 'severity': 'HIGH', 'package': 'gnutls28', 'version': '3.7.9-2+deb12u3', 'description': 'GnuTLS rejects certificate chains with distributed trust anchors'},
            {'id': 'CVE-2024-28182', 'severity': 'HIGH', 'package': 'nghttp2', 'version': '1.52.0-1', 'description': 'nghttp2 HTTP/2 CONTINUATION frame flood attack'},
            {'id': 'CVE-2023-45853', 'severity': 'HIGH', 'package': 'zlib1g', 'version': '1:1.2.13.dfsg-1', 'description': 'zlib integer overflow in zipOpenNewFileInZip4_64'},
            {'id': 'CVE-2024-26462', 'severity': 'HIGH', 'package': 'krb5', 'version': '1.20.1-2+deb12u2', 'description': 'Kerberos memory leak in SPNEGO token exchange'},
            {'id': 'CVE-2024-33600', 'severity': 'HIGH', 'package': 'glibc', 'version': '2.36-9+deb12u8', 'description': 'glibc nscd: null pointer dereferences after notfound response'},
            {'id': 'CVE-2024-33601', 'severity': 'HIGH', 'package': 'glibc', 'version': '2.36-9+deb12u8', 'description': 'glibc nscd: netgroup cache may terminate daemon on memory allocation failure'},
            {'id': 'CVE-2023-4016', 'severity': 'HIGH', 'package': 'procps', 'version': '2:4.0.2-3', 'description': 'procps-ng buffer overflow in ps command'},
            {'id': 'CVE-2024-2961', 'severity': 'HIGH', 'package': 'glibc', 'version': '2.36-9+deb12u8', 'description': 'glibc iconv out-of-bounds write in ISO-2022-CN-EXT'},
            {'id': 'CVE-2023-29491', 'severity': 'MEDIUM', 'package': 'ncurses', 'version': '6.4-4', 'description': 'ncurses: Local users can trigger security-relevant memory corruption'},
            {'id': 'CVE-2024-35325', 'severity': 'MEDIUM', 'package': 'libaom3', 'version': '3.6.0-1', 'description': 'aom: NULL pointer dereference in av1_build_inter_predictors'},
        ],
    }

    chainguard_image = {
        'name': 'cgr.dev/chainguard/python:latest',
        'total_cves': 0,
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'cves': [],
    }

    return render_template('demo_container_security.html',
                           standard_image=standard_image,
                           chainguard_image=chainguard_image,
                           brand_name=BRAND_NAME)


@app.route('/demo/libraries.html')
def demo_libraries():
    """Chainguard Libraries demo: patched packages, CVE remediation, SLSA provenance."""
    pypi_packages = [
        {'name': 'Werkzeug', 'pypi_version': '2.3.7', 'cve_count': 3,
         'cves': ['CVE-2024-34069', 'CVE-2023-46136', 'CVE-2023-25577']},
        {'name': 'requests', 'pypi_version': '2.28.2', 'cve_count': 2,
         'cves': ['CVE-2023-32681', 'CVE-2024-35195']},
        {'name': 'cryptography', 'pypi_version': '41.0.0', 'cve_count': 4,
         'cves': ['CVE-2024-26130', 'CVE-2023-49083', 'CVE-2023-38325', 'CVE-2023-23931']},
        {'name': 'Pillow', 'pypi_version': '9.5.0', 'cve_count': 5,
         'cves': ['CVE-2024-28219', 'CVE-2023-50447', 'CVE-2023-44271', 'CVE-2023-4863', 'CVE-2023-44272']},
        {'name': 'urllib3', 'pypi_version': '1.26.16', 'cve_count': 2,
         'cves': ['CVE-2023-43804', 'CVE-2023-45803']},
        {'name': 'setuptools', 'pypi_version': '67.8.0', 'cve_count': 1,
         'cves': ['CVE-2024-6345']},
    ]

    cgr_packages = [
        {'name': 'Werkzeug', 'cgr_version': '3.0.3-cgr1', 'cve_count': 0, 'cves': []},
        {'name': 'requests', 'cgr_version': '2.32.3-cgr1', 'cve_count': 0, 'cves': []},
        {'name': 'cryptography', 'cgr_version': '42.0.8-cgr1', 'cve_count': 0, 'cves': []},
        {'name': 'Pillow', 'cgr_version': '10.4.0-cgr1', 'cve_count': 0, 'cves': []},
        {'name': 'urllib3', 'cgr_version': '2.2.2-cgr1', 'cve_count': 0, 'cves': []},
        {'name': 'setuptools', 'cgr_version': '72.1.0-cgr1', 'cve_count': 0, 'cves': []},
    ]

    notable_cves = [
        {
            'id': 'CVE-2024-34069',
            'package': 'Werkzeug',
            'severity': 'HIGH',
            'cvss': '7.5',
            'description': 'Werkzeug debugger allows code execution on systems with debugging enabled and an attacker can access the debugger remotely.',
            'pypi_version': '< 3.0.3',
            'cgr_version': '3.0.3-cgr1',
            'fix': 'Upgraded to 3.0.3 with additional hardening; debugger PIN validation strengthened.',
        },
        {
            'id': 'CVE-2023-32681',
            'package': 'requests',
            'severity': 'MEDIUM',
            'cvss': '6.1',
            'description': 'Requests forwards Proxy-Authorization headers to destination servers when redirecting cross-origin, potentially leaking credentials.',
            'pypi_version': '< 2.31.0',
            'cgr_version': '2.32.3-cgr1',
            'fix': 'Patched redirect handling to strip sensitive headers on cross-origin redirects.',
        },
        {
            'id': 'CVE-2024-26130',
            'package': 'cryptography',
            'severity': 'HIGH',
            'cvss': '7.5',
            'description': 'NULL pointer dereference in PKCS#12 parsing causes process crash when processing specially crafted certificates.',
            'pypi_version': '< 42.0.4',
            'cgr_version': '42.0.8-cgr1',
            'fix': 'Fixed PKCS#12 parsing; updated to latest OpenSSL bindings.',
        },
        {
            'id': 'CVE-2024-28219',
            'package': 'Pillow',
            'severity': 'HIGH',
            'cvss': '7.3',
            'description': 'Buffer overflow in _imagingcms.c when processing ICC profiles in crafted images.',
            'pypi_version': '< 10.3.0',
            'cgr_version': '10.4.0-cgr1',
            'fix': 'Fixed bounds checking in ICC profile parsing; updated libimagequant and zlib.',
        },
    ]

    sample_attestation = '''{
  "_type": "https://in-toto.io/Statement/v0.1",
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "subject": [
    {
      "name": "cgr.dev/chainguard/python",
      "digest": {
        "sha256": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
      }
    }
  ],
  "predicate": {
    "builder": {
      "id": "https://github.com/chainguard-dev/apko/.github/workflows/release.yml"
    },
    "buildType": "https://github.com/chainguard-dev/melange",
    "invocation": {
      "configSource": {
        "uri": "https://github.com/chainguard-images/images",
        "digest": { "sha1": "abc123def456" },
        "entryPoint": "images/python/configs/latest.apko.yaml"
      }
    },
    "metadata": {
      "buildStartedOn": "2024-10-01T12:00:00Z",
      "buildFinishedOn": "2024-10-01T12:04:33Z",
      "completeness": {
        "parameters": true,
        "environment": true,
        "materials": true
      },
      "reproducible": true
    },
    "materials": [
      {
        "uri": "https://packages.cgr.dev/os/x86_64/python-3.12.6-r0.apk",
        "digest": { "sha256": "deadbeef..." }
      }
    ]
  }
}'''

    return render_template('demo_libraries.html',
                           pypi_packages=pypi_packages,
                           cgr_packages=cgr_packages,
                           notable_cves=notable_cves,
                           sample_attestation=sample_attestation,
                           brand_name=BRAND_NAME)


@app.route('/demo/platform.html')
def demo_platform():
    """Platform demo: Custom Assembly, versioned build.yaml, evidence bundle."""
    return render_template('demo_platform.html', brand_name=BRAND_NAME)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
