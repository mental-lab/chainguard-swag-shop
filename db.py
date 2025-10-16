import sqlite3
import os
from config import BRAND_NAME

DATABASE_PATH = 'db/store.db'

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables if they don't exist"""
    if not os.path.exists(DATABASE_PATH):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image TEXT,
            category TEXT
        )
        ''')
        
        # Create orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create order_items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        conn.commit()
        conn.close()

class Product:
    def __init__(self, id, name, description, price, image_url, category):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.image_url = image_url
        self.category = category

# Sample product data (in a real app, this would come from a database)
_products = [
    Product(1, 
            f"{BRAND_NAME} Softstyle V-Neck Tee", 
            "This v-neck t-shirt features double-needle stitched sleeves and bottom hem add durability.", 
            20.00, 
            "https://source.unsplash.com/800x800/?tshirt,blue,apparel&sig=1", 
            "Clothing"),
    Product(2, 
            f"{BRAND_NAME} Knit Beanie", 
            "Knit Beanie with Cuff.", 
            15.00, 
            "https://source.unsplash.com/800x800/?beanie,hat,knit&sig=2", 
            "Accessories"),
    Product(3, 
            f"{BRAND_NAME} Jacquard Ankle Socks", 
            "100% athletic jacquard/woven socks.", 
            10.00, 
            "https://source.unsplash.com/800x800/?socks,knit,pattern&sig=3", 
            "Clothing"),
    Product(4, 
            f"{BRAND_NAME} YETI Rambler Mug", 
            "Food-grade 18/8 stainless steel, double-wall vacuum insulation, this 10oz mug keeps contents cold or hot.", 
            34.00, 
            "https://source.unsplash.com/800x800/?mug,coffee,white&sig=4", 
            "Accessories"),
    Product(5, 
            f"{BRAND_NAME} Loose Eco Knit Vest", 
            "Features: Super Soft sweaterfleece, zippered chest pocket, and on-seam zippered pockets.", 
            55.00, 
            "https://source.unsplash.com/800x800/?vest,fleece,apparel&sig=5", 
            "Clothing"),
    Product(6, 
            f"{BRAND_NAME} Comfort Colors Tee", 
            "Pigment Dyed Short Sleeve T-Shirt made with 100% pre-shrunk cotton.", 
            22.00, 
            "https://source.unsplash.com/800x800/?tshirt,cotton,comfort&sig=6", 
            "Clothing"),
    Product(7, 
            f"{BRAND_NAME} North Face Beanie", 
            "A cold-weather must-have that features an adjustable cuff height and a fleece liner. Made by The North Face", 
            35.00, 
            "https://source.unsplash.com/800x800/?beanie,warm,hat&sig=7", 
            "Accessories"),
    Product(8, 
            f"{BRAND_NAME} Adult Cotton Hat", 
            "6-panel cap is made of a garment washed superior 100% cotton.", 
            20.00, 
            "https://source.unsplash.com/800x800/?cap,hat,cotton&sig=8", 
            "Accessories"),

    Product(9, 
            f"{BRAND_NAME} Fitted Eco Knit Vest", 
            "The Overachiever sweater fleece vest serves up the warmth of wool with the comfort of your favorite fireside snack. Features: Super Soft sweaterfleece, zippered chest pocket, and on-seam zippered pockets.", 
            55.00, 
            "https://source.unsplash.com/800x800/?vest,women,apparel&sig=9", 
            "Clothing"),
    Product(10, 
            f"{BRAND_NAME} Next Level Hoodie", 
            "7.4-ounce, 60/40 cotton/poly pullover hoodie.", 
            50.00, 
            "https://source.unsplash.com/800x800/?hoodie,blue,apparel&sig=10", 
            "Clothing"),
    Product(11, 
            f"{BRAND_NAME} Camelbak Tumbler", 
            "Tumbler is 20 oz. It features a durable full powder-coat, copper vacuum-insulated stainless steel.", 
            35.00, 
            "https://source.unsplash.com/800x800/?tumbler,travel,stainless&sig=11", 
            "Clothing"),
    Product(12, 
            f"{BRAND_NAME} Sticky Notes", 
            f"5x5 {BRAND_NAME} sticky notes. 50 sheets.", 
            5.00, 
            "https://source.unsplash.com/800x800/?sticky,notes,stationery&sig=12", 
            "Clothing"),
    Product(13, 
            f"{BRAND_NAME} Jacquard Dress Socks", 
            "This soft cotton crew dress sock is made to fit various foot sizes while keeping your feet comfortable for the duration of the work day. Made of 60% cotton / 27% spandex / 10% nylon / 3% elastic. #1 Seller. One size fits most.", 
            10.00, 
            "https://source.unsplash.com/800x800/?socks,dress,pattern&sig=13", 
            "Clothing"),
    Product(14, 
            "Softstyle Crewneck Tee", 
            "Latest flagship smartphone with advanced features", 
            20.00, 
            "https://source.unsplash.com/800x800/?tshirt,crewneck,apparel&sig=14", 
            "Clothing"),
    Product(15, 
            f"{BRAND_NAME} Paperzen Slim Wallet", 
            "Durable, lightweight, washable and sustainable jeans tags material wallet , Left pocket with 4 card slots . Right pocket can accommodate a passport.", 
            7.00, 
            "https://source.unsplash.com/800x800/?wallet,slim,leather&sig=15", 
            "Clothing"),
    Product(16, 
            "Jotter Click Pens", 
            f"Custom {BRAND_NAME} pens, 3 per pack", 
            7.00, 
            "https://source.unsplash.com/800x800/?pens,gel,stationery&sig=16", 
            "Clothing"),
    Product(17, 
            f"{BRAND_NAME} Smartpad Mousepad", 
            "This standard mouse pad features a natural rubber mat that measures 9 x 7 1/4. 1/8 thick natural rubber.", 
            10.00, 
            "https://source.unsplash.com/800x800/?mousepad,desk,accessory&sig=17", 
            "Clothing"),
    Product(18, 
            f"{BRAND_NAME} Lapel Pin 2 pack", 
            f"Set of 2 lapel pins with plating and custom {BRAND_NAME} cut shape.", 
            10.00, 
            "https://source.unsplash.com/800x800/?enamel,pin,badge&sig=18", 
            "Accessories"),
]

def get_products():
    return _products

def get_product_by_id(product_id):
    for product in _products:
        if product.id == product_id:
            return product
    return None
