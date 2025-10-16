from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
from db import Product, get_products, get_product_by_id
from config import BRAND_NAME

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production
# for the freezer.py
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_IGNORE_404_NOT_FOUND'] = True

# CWE-798: Hardcoded AWS Credentials (DEMO VULNERABILITY - DO NOT USE IN PRODUCTION)
# These credentials are intentionally hardcoded for security scanning demonstration
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION = "us-west-2"

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


# Demo Vulnerability Routes (CWE Demonstrations)
# These routes contain intentional security vulnerabilities for demonstration purposes
# WARNING: DO NOT USE IN PRODUCTION

@app.route('/demo/search.html', methods=['GET', 'POST'])
def demo_search():
    """
    CWE-89: SQL Injection Vulnerability Demo Route
    
    This route intentionally contains SQL injection vulnerabilities for demonstration purposes.
    It shows how user input can be directly concatenated into SQL queries without proper sanitization.
    """
    import sqlite3
    
    search_results = []
    search_term = ""
    error_message = ""
    
    if request.method == 'POST':
        search_term = request.form.get('search_term', '')
        
        if search_term:
            try:
                # CWE-89: VULNERABLE SQL INJECTION - Direct string concatenation
                # This is intentionally vulnerable for demonstration purposes
                conn = sqlite3.connect(':memory:')
                cursor = conn.cursor()
                
                # Create a demo table with sample data
                cursor.execute('''
                    CREATE TABLE demo_products (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        description TEXT,
                        price REAL
                    )
                ''')
                
                # Insert sample data
                sample_products = [
                    (1, f'{BRAND_NAME} T-Shirt', 'Comfortable cotton t-shirt', 25.00),
                    (2, f'{BRAND_NAME} Mug', 'Ceramic coffee mug', 15.00),
                    (3, f'{BRAND_NAME} Stickers', 'Pack of logo stickers', 5.00),
                    (4, f'{BRAND_NAME} Hoodie', 'Warm hoodie with logo', 45.00)
                ]
                
                cursor.executemany(
                    'INSERT INTO demo_products (id, name, description, price) VALUES (?, ?, ?, ?)',
                    sample_products
                )
                
                # VULNERABLE QUERY - Direct string concatenation allows SQL injection
                vulnerable_query = f"SELECT * FROM demo_products WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"
                
                cursor.execute(vulnerable_query)
                results = cursor.fetchall()
                
                for row in results:
                    search_results.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'price': row[3]
                    })
                
                conn.close()
                
            except Exception as e:
                error_message = f"Database error: {str(e)}"
    
    return render_template('demo_search.html', 
                         search_results=search_results, 
                         search_term=search_term,
                         error_message=error_message)


@app.route('/demo/generate_invoice.html', methods=['GET', 'POST'])
def demo_generate_invoice():
    """
    CWE-78: Command Injection Vulnerability Demo Route
    
    This route intentionally contains command injection vulnerabilities for demonstration purposes.
    It shows how user input can be directly passed to system commands without proper sanitization.
    """
    import subprocess
    import os
    import tempfile
    
    invoice_content = ""
    error_message = ""
    command_output = ""
    
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '')
        invoice_format = request.form.get('invoice_format', 'txt')
        
        if customer_name:
            try:
                # CWE-78: VULNERABLE COMMAND INJECTION - Direct user input in system command
                # This is intentionally vulnerable for demonstration purposes
                
                # Create a temporary directory for invoice generation
                temp_dir = tempfile.mkdtemp()
                invoice_filename = f"invoice_{customer_name}.{invoice_format}"
                invoice_path = os.path.join(temp_dir, invoice_filename)
                
                # Generate basic invoice content
                invoice_content = f"""
INVOICE
=======
Customer: {customer_name}
Date: $(date)
Items:
- {BRAND_NAME} T-Shirt: $25.00
- {BRAND_NAME} Mug: $15.00
Total: $40.00

Thank you for your business!
"""
                
                # VULNERABLE COMMAND - Direct user input concatenation allows command injection
                # The customer_name parameter is directly inserted into the command
                vulnerable_command = f"echo '{invoice_content}' > {invoice_path} && echo 'Invoice generated for {customer_name}'"
                
                # Execute the vulnerable command
                result = subprocess.run(vulnerable_command, 
                                      shell=True, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=10)
                
                command_output = result.stdout
                
                if result.returncode == 0:
                    # Read the generated invoice
                    if os.path.exists(invoice_path):
                        with open(invoice_path, 'r') as f:
                            invoice_content = f.read()
                else:
                    error_message = f"Command execution failed: {result.stderr}"
                
                # Cleanup
                try:
                    if os.path.exists(invoice_path):
                        os.remove(invoice_path)
                    os.rmdir(temp_dir)
                except:
                    pass  # Ignore cleanup errors
                    
            except subprocess.TimeoutExpired:
                error_message = "Command execution timed out"
            except Exception as e:
                error_message = f"Error generating invoice: {str(e)}"
    
    return render_template('demo_invoice.html', 
                         invoice_content=invoice_content,
                         command_output=command_output,
                         error_message=error_message)


@app.route('/demo/download_receipt.html', methods=['GET', 'POST'])
def demo_download_receipt():
    """
    CWE-22: Path Traversal Vulnerability Demo Route
    
    This route intentionally contains path traversal vulnerabilities for demonstration purposes.
    It shows how user input can be used to access files outside the intended directory.
    """
    import os
    
    receipt_content = ""
    error_message = ""
    available_receipts = []
    
    # Get list of available receipts (legitimate files)
    receipts_dir = "receipts"
    if os.path.exists(receipts_dir):
        try:
            for filename in os.listdir(receipts_dir):
                if filename.endswith('.txt') and filename.startswith('receipt_'):
                    available_receipts.append(filename)
        except:
            pass
    
    if request.method == 'POST':
        receipt_filename = request.form.get('receipt_filename', '')
        
        if receipt_filename:
            try:
                # CWE-22: VULNERABLE PATH TRAVERSAL - Direct file path concatenation
                # This is intentionally vulnerable for demonstration purposes
                
                # VULNERABLE CODE - No path validation allows directory traversal
                file_path = os.path.join(receipts_dir, receipt_filename)
                
                # This allows paths like "../../../etc/passwd" or "../app.py"
                # The os.path.join doesn't prevent traversal when the second argument starts with ../
                
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        receipt_content = f.read()
                else:
                    error_message = f"Receipt file '{receipt_filename}' not found"
                    
            except Exception as e:
                error_message = f"Error reading receipt: {str(e)}"
    
    return render_template('demo_receipt.html', 
                         receipt_content=receipt_content,
                         error_message=error_message,
                         available_receipts=available_receipts)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
