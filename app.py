from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

# ---------------- Database ----------------
db = None
cursor = None

def init_db():
    global db, cursor
    if db is None or not db.is_connected():
        db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306))
)
        cursor = db.cursor(dictionary=True)

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE,
        email VARCHAR(100) UNIQUE,
        password VARCHAR(255),
        fullname VARCHAR(100),
        phone VARCHAR(20),
        default_address TEXT
    )
    """)

    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        description TEXT,
        price FLOAT,
        stock INT,
        category VARCHAR(50),
        image VARCHAR(100)
    )
    """)

    # Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        product_id INT,
        quantity INT,
        total_price FLOAT,
        address TEXT,
        status VARCHAR(50) DEFAULT 'Pending',
        payment_status VARCHAR(50) DEFAULT 'PENDING',
        created_at DATETIME,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    # Payments table
    cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'INITIATED',
    transaction_id VARCHAR(255),
    paid_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
)
""")


    # Preload products if empty
    cursor.execute("SELECT COUNT(*) as count FROM products")
    count = cursor.fetchone()["count"]
    if count == 0:
        cursor.execute("""
INSERT INTO products (name, price, description, image, category, stock) VALUES
('Redmi Note 14 5G Titan Black', 18499.0, 'Xiaomi HyperOS Based on Android 14 (8GB RAM, 256GB Storage)', 'phone1.jpg', 'phone', 5),
('OnePlus Nord Buds 3', 1999.0, 'ANC, Upto 43hrs playback time, IP55 Rated Earbuds, Sound Master Equalizer (Chromatic Blue)', 'earpods1.jpg', 'earpods', 3),
('Fire-Boltt Vintage Smartwatch', 2000.0, '1.32 inch HD Display | Bluetooth Calling | Health Suite | Multiple Sports Modes | Long Battery Life (Silver)', 'smartwatch1.jpg', 'wearable', 4),
('HP Laptop 15FD0623TU', 39499.0, 'Intel Core i3 13th Gen/8GB RAM/512GB SSD/15.6 Inch Full HD IPS Display', 'laptop1.jpg', 'laptop', 3),
('OnePlus 15R 5G Mint Breeze', 52999.0, '12GB RAM, 512GB Storage Snapdragon 8 Gen 5 | 7400 mAh Battery | Lifetime Display Warranty', 'phone2.jpg', 'phone', 4),
('Boat Airdopes 133', 1499.0, 'IPX4 Water Resistant, 17hrs Playback, Bluetooth 5.0', 'earpods2.jpg', 'earpods', 5),
('Noise ColorFit Pro 4', 2999.0, '1.78 inch HD Display, Health Tracking, Sports Modes', 'smartwatch2.jpg', 'wearable', 2),
('Dell Inspiron 14 5000', 45999.0, 'Intel Core i5 12th Gen/8GB RAM/512GB SSD/14-inch Full HD', 'laptop2.jpg', 'laptop', 4),
('Google Pixel 10 Pro 5G', 109999.0, '16GB RAM/256GB Moonstone Android 16 with 7 Years OS & Security Updates', 'phone3.jpg', 'phone', 3),
('Realme Buds Q2', 1299.0, 'Bluetooth 5.0, 28hrs Playback, Low Latency Gaming', 'earpods3.jpg', 'earpods', 4),
('Amazfit Bip U Pro', 3499.0, '1.43 inch HD Display | SpO2 | 60+ Sports Modes', 'smartwatch3.jpg', 'wearable', 3),
('Lenovo IdeaPad 3', 34999.0, 'Intel Core i3 11th Gen/8GB RAM/256GB SSD/15.6-inch Full HD', 'laptop3.jpg', 'laptop', 3),
('vivo X300 5G Elite Black', 75999.0, '6.31-inch AMOLED, 120 Hz Refresh Rate (12GB RAM, 256GB Storage)', 'phone4.jpg', 'phone', 4),
('Sony WF-C500', 2499.0, 'True Wireless Earbuds, 10hrs Playback, IPX4', 'earpods4.jpg', 'earpods', 2),
('Noise Titan Smartwatch', 3999.0, '1.69 inch AMOLED | Fitness Tracking | Sports Modes', 'smartwatch4.jpg', 'wearable', 3),
('Asus VivoBook 15', 42999.0, 'Intel Core i5 12th Gen/16GB RAM/512GB SSD/15.6-inch Full HD', 'laptop4.jpg', 'laptop', 2)
""")
    db.commit()

init_db()

# ---------------- Context Processor ----------------
@app.context_processor
def inject_globals():
    return {'datetime': datetime}

# ---------------- Routes -----------------
@app.route("/")
def home():
    category = request.args.get("category")

    if category:
        cursor.execute("SELECT * FROM products WHERE category=%s", (category,))
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    user_name = None
    if "user_id" in session:
        cursor.execute("SELECT username FROM users WHERE id=%s", (session["user_id"],))
        user_name = cursor.fetchone()["username"]

    return render_template("index.html", products=products, user_name=user_name)

# Registration
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        fullname = request.form["fullname"]
        phone = request.form["phone"]
        try:
            cursor.execute(
                "INSERT INTO users (username,email,password,fullname,phone) VALUES (%s,%s,%s,%s,%s)",
                (username,email,password,fullname,phone)
            )
            db.commit()
            flash("Registration successful! Please login.","success")
            return redirect("/login")
        except:
            flash("Username or email already exists.","danger")
            return redirect("/register")
    return render_template("register.html")

# Login
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['username']}!","success")
            return redirect("/")
        else:
            flash("Invalid credentials.","danger")
            return redirect("/login")
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.","info")
    return redirect("/")

# Profile
@app.route("/profile", methods=["GET","POST"])
def profile():
    if "user_id" not in session:
        flash("Please login first.","warning")
        return redirect("/login")
    cursor.execute("SELECT * FROM users WHERE id=%s",(session["user_id"],))
    user = cursor.fetchone()
    if request.method=="POST":
        fullname = request.form["fullname"]
        phone = request.form["phone"]
        default_address = request.form["default_address"]
        cursor.execute(
            "UPDATE users SET fullname=%s, phone=%s, default_address=%s WHERE id=%s",
            (fullname, phone, default_address, session["user_id"])
        )
        db.commit()
        flash("Profile updated.","success")
        return redirect("/profile")
    return render_template("profile.html", user=user, user_name=user["username"])

# Checkout
@app.route("/checkout/<int:product_id>", methods=["GET","POST"])
def checkout(product_id):
    if "user_id" not in session:
        flash("Please login to buy products.","warning")
        return redirect("/login")

    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()

    if request.method == "POST":
        quantity = int(request.form["quantity"])
        address = request.form["address"]
        total_price = quantity * product["price"]

        if quantity > product["stock"]:
            flash("Not enough stock.", "danger")
            return redirect(url_for("checkout", product_id=product_id))

        cursor.execute("""
            INSERT INTO orders (user_id, product_id, quantity, total_price, address, created_at)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            session["user_id"],
            product_id,
            quantity,
            total_price,
            address,
            datetime.now()
        ))

        order_id = cursor.lastrowid

        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product_id))
        db.commit()

        return redirect(url_for("payment", order_id=order_id))

    return render_template("checkout.html", product=product, user=user)

#cancel Orders
@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor.execute("""
        SELECT * FROM orders 
        WHERE id=%s AND user_id=%s
    """, (order_id, session["user_id"]))
    order = cursor.fetchone()

    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('orders'))

    # 🔒 BLOCK CANCEL IF PAID
    if order['payment_status'] == 'PAID':
        flash("Cannot cancel a paid order.", "danger")
        return redirect(url_for('orders'))

    cursor.execute("DELETE FROM orders WHERE id=%s", (order_id,))
    db.commit()

    flash("Order cancelled successfully.", "success")
    return redirect(url_for('orders'))

# Orders page
@app.route("/orders", methods=["GET", "POST"])
def orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # 🔹 Handle order edits
    if request.method == "POST":
        order_id = request.form["order_id"]
        quantity = request.form["quantity"]
        address = request.form["address"]

        # Check if order is already paid
        cursor.execute("""
            SELECT payment_status 
            FROM orders 
            WHERE id=%s AND user_id=%s
        """, (order_id, session["user_id"]))
        order = cursor.fetchone()

        if order and order["payment_status"] == "PAID":
            flash("Order cannot be edited after payment.", "danger")
            return redirect(url_for("orders"))

        # Update order if not paid
        cursor.execute("""
            UPDATE orders 
            SET quantity=%s, address=%s 
            WHERE id=%s AND user_id=%s
        """, (quantity, address, order_id, session["user_id"]))
        db.commit()

        flash("Order updated successfully.", "success")
        return redirect(url_for("orders"))

    # 🔹 Fetch all orders with product info and payment method
    cursor.execute("""
        SELECT o.*, p.name, p.image, pay.payment_method
        FROM orders o
        JOIN products p ON o.product_id = p.id
        LEFT JOIN payments pay ON o.id = pay.order_id
        WHERE o.user_id=%s
        ORDER BY o.created_at DESC
    """, (session["user_id"],))
    orders = cursor.fetchall()

    return render_template("orders.html", orders=orders)


# Payment
@app.route("/payment/<int:order_id>", methods=["GET", "POST"])
def payment(order_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor.execute("""
        SELECT o.*, p.name 
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.id=%s AND o.user_id=%s
    """, (order_id, session["user_id"]))

    order = cursor.fetchone()

    if not order:
        flash("Order not found.", "danger")
        return redirect("/")

    if request.method == "POST":
        payment_method = request.form["payment_method"]

        # ---- CASH ON DELIVERY ----
        if payment_method == "Cash on Delivery":
            cursor.execute("""
                INSERT INTO payments (order_id, payment_method, payment_status)
                VALUES (%s,%s,'COD')
            """, (order_id, payment_method))

            cursor.execute("""
                UPDATE orders
                SET payment_status='COD', status='Confirmed'
                WHERE id=%s
            """, (order_id,))

            db.commit()
            flash("Order placed successfully! Pay on delivery.", "success")
            return redirect("/orders")

        # ---- ONLINE PAYMENT (SIMULATED) ----
        else:
            fake_transaction_id = f"TXN{int(datetime.now().timestamp())}"

            cursor.execute("""
                INSERT INTO payments (
                    order_id,
                    payment_method,
                    payment_status,
                    transaction_id,
                    paid_at
                )
                VALUES (%s,%s,'SUCCESS',%s,%s)
            """, (
                order_id,
                payment_method,
                fake_transaction_id,
                datetime.now()
            ))

            cursor.execute("""
                UPDATE orders
                SET payment_status='PAID', status='Confirmed'
                WHERE id=%s
            """, (order_id,))

            db.commit()
            flash("Payment successful!", "success")
            return redirect("/orders")

    return render_template("payment.html", order=order)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

