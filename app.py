# app.py - Flask backend for login, dashboard, and product detail pages
from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.executescript('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                posted_by TEXT,
                type TEXT,
                size TEXT,
                description TEXT,
                availability TEXT,
                mode TEXT,
                main_image TEXT
            );
            CREATE TABLE product_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                image_path TEXT
            );
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('dashboard.html', username=session['username'], products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        conn.close()
        return 'Product not found', 404
    images = conn.execute('SELECT image_path FROM product_images WHERE product_id = ?', (product_id,)).fetchall()
    conn.close()
    product_data = {
        'name': product['name'],
        'posted_by': product['posted_by'],
        'type': product['type'],
        'size': product['size'],
        'description': product['description'],
        'availability': product['availability'],
        'mode': product['mode'],
        'main_image': product['main_image'],
        'images': [img['image_path'] for img in images]
    }
    return render_template('product_detail.html', product=product_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)