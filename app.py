"""
Inventory Management System
A Flask-based web application for managing inventory data with user authentication.

Authors:
- Parminder Singh (Student ID: 25351400)
- Navdeep Kaur (Student ID: 25343800)

This application provides CRUD (Create, Read, Update, Delete) operations
for inventory items with SQLite database persistence and user authentication.
"""

import os
import sqlite3
import uuid
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Initialize Flask application
app = Flask(__name__)

# Secret key for session management and flash messages
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')

# Database configuration
DATABASE = 'inventory.db'

# Image upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# ============================================================================
# USER MODEL FOR FLASK-LOGIN
# ============================================================================

class User(UserMixin):
    """
    User model for Flask-Login integration.
    Implements required methods for user session management.
    """
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    """
    Callback to reload user object from user ID stored in session.
    Required by Flask-Login for session management.
    """
    conn = get_db_connection()
    user_data = conn.execute(
        'SELECT id, username, email FROM users WHERE id = ?', 
        (user_id,)
    ).fetchone()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Database connection object with row factory
        set to return dictionary-like rows for easier data access.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the database by creating required tables.
    
    Creates two tables:
    1. users - For storing user authentication data
    2. inventory - For storing inventory items with user ownership
    """
    conn = get_db_connection()
    
    # Create users table for authentication
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create inventory table with user relationship and image support
    conn.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()


def allowed_file(filename):
    """
    Checks if uploaded file has an allowed extension.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
    """
    Saves uploaded image file with a unique filename.
    
    Args:
        file: FileStorage object from form upload
        
    Returns:
        str: Saved filename or None if save failed
    """
    if file and file.filename and allowed_file(file.filename):
        # Generate unique filename to prevent overwrites
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return unique_filename
    return None


def delete_image(filename):
    """
    Deletes an image file from the uploads folder.
    Includes error handling for filesystem operations.
    
    Args:
        filename: Name of the file to delete
    """
    if filename:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except OSError:
            pass


def format_datetime(value):
    """
    Formats a datetime string for display in templates.
    """
    if value:
        try:
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%d/%m/%Y %H:%M')
        except (ValueError, TypeError):
            return value
    return ''


# Register template filter
app.jinja_env.filters['datetime'] = format_datetime


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    Creates new user account with hashed password.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Check if user already exists
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing_user:
            conn.close()
            flash('Username or email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user with hashed password
        password_hash = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    Authenticates user and creates session.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please enter username and password.', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        user_data = conn.execute(
            'SELECT id, username, email, password_hash FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['email'])
            login_user(user, remember=bool(remember))
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to requested page or home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Invalid username or password.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """
    User logout route.
    Ends user session and redirects to login.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================================
# INVENTORY CRUD ROUTES
# ============================================================================

@app.route('/')
@login_required
def index():
    """
    Home page route - Displays user's inventory items.
    """
    conn = get_db_connection()
    items = conn.execute(
        'SELECT * FROM inventory WHERE user_id = ? ORDER BY updated_at DESC',
        (current_user.id,)
    ).fetchall()
    conn.close()
    
    # Calculate summary statistics
    total_items = len(items)
    total_quantity = sum(item['quantity'] for item in items)
    total_value = sum(item['quantity'] * item['price'] for item in items)
    
    return render_template(
        'index.html',
        items=items,
        total_items=total_items,
        total_quantity=total_quantity,
        total_value=total_value
    )


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    """
    Add new inventory item route - CREATE operation.
    Supports image upload for item.
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        quantity = request.form.get('quantity', '')
        price = request.form.get('price', '')
        category = request.form.get('category', '').strip()
        
        # Validate required fields
        if not name or not quantity or not price or not category:
            flash('All fields are required!', 'error')
            return redirect(url_for('add_item'))
        
        # Validate numeric values
        try:
            quantity = int(quantity)
            price = float(price)
            
            if quantity < 0:
                flash('Quantity cannot be negative!', 'error')
                return redirect(url_for('add_item'))
            if price < 0:
                flash('Price cannot be negative!', 'error')
                return redirect(url_for('add_item'))
                
        except ValueError:
            flash('Invalid quantity or price value!', 'error')
            return redirect(url_for('add_item'))
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                image_filename = save_image(file)
                if file.filename and not image_filename:
                    flash('Invalid image format. Allowed: PNG, JPG, JPEG, GIF, WEBP', 'error')
                    return redirect(url_for('add_item'))
        
        # Insert new item
        conn = get_db_connection()
        conn.execute(
            '''INSERT INTO inventory (user_id, name, quantity, price, category, image_filename) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (current_user.id, name, quantity, price, category, image_filename)
        )
        conn.commit()
        conn.close()
        
        flash(f'Item "{name}" added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    """
    Edit inventory item route - UPDATE operation.
    Supports updating or removing item image.
    """
    conn = get_db_connection()
    item = conn.execute(
        'SELECT * FROM inventory WHERE id = ? AND user_id = ?', 
        (id, current_user.id)
    ).fetchone()
    
    if item is None:
        conn.close()
        flash('Item not found!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        quantity = request.form.get('quantity', '')
        price = request.form.get('price', '')
        category = request.form.get('category', '').strip()
        remove_image = request.form.get('remove_image', False)
        
        # Validate required fields
        if not name or not quantity or not price or not category:
            flash('All fields are required!', 'error')
            return redirect(url_for('edit_item', id=id))
        
        # Validate numeric values
        try:
            quantity = int(quantity)
            price = float(price)
            
            if quantity < 0:
                flash('Quantity cannot be negative!', 'error')
                return redirect(url_for('edit_item', id=id))
            if price < 0:
                flash('Price cannot be negative!', 'error')
                return redirect(url_for('edit_item', id=id))
                
        except ValueError:
            flash('Invalid quantity or price value!', 'error')
            return redirect(url_for('edit_item', id=id))
        
        # Handle image
        image_filename = item['image_filename']
        
        # Remove image if requested
        if remove_image:
            delete_image(image_filename)
            image_filename = None
        
        # Handle new image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                new_image = save_image(file)
                if new_image:
                    # Delete old image
                    delete_image(item['image_filename'])
                    image_filename = new_image
                else:
                    flash('Invalid image format.', 'error')
                    return redirect(url_for('edit_item', id=id))
        
        # Update item
        conn.execute('''
            UPDATE inventory 
            SET name = ?, quantity = ?, price = ?, category = ?, 
                image_filename = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', (name, quantity, price, category, image_filename, id, current_user.id))
        conn.commit()
        conn.close()
        
        flash(f'Item "{name}" updated successfully!', 'success')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('edit.html', item=item)


@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_item(id):
    """
    Delete inventory item route - DELETE operation.
    Also removes associated image file.
    """
    conn = get_db_connection()
    item = conn.execute(
        'SELECT name, image_filename FROM inventory WHERE id = ? AND user_id = ?',
        (id, current_user.id)
    ).fetchone()
    
    if item is None:
        conn.close()
        flash('Item not found!', 'error')
        return redirect(url_for('index'))
    
    item_name = item['name']
    
    # Delete associated image
    delete_image(item['image_filename'])
    
    # Delete item from database
    conn.execute('DELETE FROM inventory WHERE id = ? AND user_id = ?', (id, current_user.id))
    conn.commit()
    conn.close()
    
    flash(f'Item "{item_name}" deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/view/<int:id>')
@login_required
def view_item(id):
    """
    View single inventory item details.
    """
    conn = get_db_connection()
    item = conn.execute(
        'SELECT * FROM inventory WHERE id = ? AND user_id = ?',
        (id, current_user.id)
    ).fetchone()
    conn.close()
    
    if item is None:
        flash('Item not found!', 'error')
        return redirect(url_for('index'))
    
    return render_template('view.html', item=item)


@app.route('/search')
@login_required
def search():
    """
    Search inventory items by name or category.
    Only searches current user's items.
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    items = conn.execute('''
        SELECT * FROM inventory 
        WHERE user_id = ? AND (name LIKE ? OR category LIKE ?)
        ORDER BY updated_at DESC
    ''', (current_user.id, f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    
    return render_template('search.html', items=items, query=query)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

# Initialize database
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
