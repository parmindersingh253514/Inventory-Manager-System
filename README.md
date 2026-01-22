# Inventory Management System

A web-based Inventory Management System built with Flask and SQLite for managing inventory data effectively. This project features user authentication, image uploads, and full CRUD operations. Developed as part of a Computing Technology university module.

## Project Information

**Module**: Computing Technology  
**Academic Year**: 2025/2026

video link: http://youtube.com/watch?v=k1kGXHkBAEo&feature=youtu.be
### Team Members

| Name | Student ID | Contributions |
|------|------------|---------------|
| Parminder Singh | 25351400 | Backend development, database design, Flask routes, authentication system |
| Navdeep Kaur | 25343800 | Frontend development, HTML/CSS templates, image upload feature, documentation |

## Project Purpose

This Inventory Management System solves the real-world problem of tracking and managing inventory items in a business or warehouse setting. It provides:

- Secure user authentication with registration and login
- Personal inventory management for each user
- Image uploads for visual item identification
- Comprehensive item tracking with categories and pricing

## Features

### Authentication
- **User Registration**: Create new accounts with username, email, and password
- **Secure Login**: Password hashing with Werkzeug for security
- **Session Management**: Flask-Login for persistent sessions
- **Remember Me**: Optional persistent login

### Inventory Management
- **Add Items**: Create inventory entries with name, category, quantity, price, and image
- **View Items**: Dashboard with card-based display and summary statistics
- **Update Items**: Modify item details and replace/remove images
- **Delete Items**: Remove items with confirmation prompts
- **Search**: Find items by name or category

### Image Upload
- **Supported Formats**: PNG, JPG, JPEG, GIF, WEBP
- **File Size Limit**: 5MB maximum
- **Preview**: Real-time image preview before upload
- **Management**: Replace or remove images when editing items

### Dashboard Features
- Total items count
- Total quantity across all items
- Total inventory value calculation
- Visual stock alerts (low stock, out of stock)

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11 |
| Framework | Flask 3.x |
| Authentication | Flask-Login |
| Password Hashing | Werkzeug Security |
| Database | SQLite |
| Frontend | HTML5, CSS3, JavaScript |
| Template Engine | Jinja2 |
| Production Server | Gunicorn |

## System Architecture

![System Architecture](/diagrams/Diagrams-System%20Architecture.drawio.png)

## Application Workflow

![Application Workflow](/diagrams/Diagrams-Application%20Workflow.drawio.png)
## Database Schema

![Database Schema](/diagrams/Diagrams-Database%20Schema.drawio.png)
## ER Diagram with Operations

![ER Diagram](/diagrams/Diagrams-ER%20Diagram%20with%20Operations.drawio.png)
## Authentication Flow

![Authentication Flow](/diagrams/Diagrams-Authentication%20Flow.drawio.png)
## CRUD Operations with Image Upload

![CRUD Operations](/diagrams/Diagrams-CRUD%20Operations%20with%20Image%20Upload.drawio.png)
## Project Structure

```
inventory-management-system/
├── app.py                 # Main Flask application
├── inventory.db           # SQLite database (auto-generated)
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html         # Base layout template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── index.html        # Dashboard with item cards
│   ├── add.html          # Add item form with image upload
│   ├── edit.html         # Edit item form
│   ├── view.html         # Single item view
│   └── search.html       # Search results
└── diagrams/             # Project diagrams
    ├── Diagrams-System Architecture.drawio.png
    ├── Diagrams-Application Workflow.drawio.png
    ├── Diagrams-Database Schema.drawio.png
    ├── Diagrams-ER Diagram with Operations.drawio.png
    ├── Diagrams-Authentication Flow.drawio.png
    └── Diagrams-CRUD Operations with Image Upload.drawio.png
└── static/
    ├── style.css         # CSS stylesheet
    └── uploads/          # Uploaded images directory
```

## How to Run the Project

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/parmindersingh253514/Inventory-Manager-System
   cd inventory-management-system
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your web browser and navigate to: `http://localhost:5000`

6. **Create an account**
   - Click "Register" to create a new account
   - Log in with your credentials
   - Start managing your inventory!

### Running in Production

For production deployment, use Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## API Routes

### Authentication Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |

### Inventory Routes (Protected)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Dashboard with all items |
| GET/POST | `/add` | Add new item with image |
| GET/POST | `/edit/<id>` | Edit item |
| POST | `/delete/<id>` | Delete item |
| GET | `/view/<id>` | View item details |
| GET | `/search?q=<query>` | Search items |

## Database Tables

### Users Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| username | TEXT | UNIQUE, NOT NULL | User's username |
| email | TEXT | UNIQUE, NOT NULL | User's email |
| password_hash | TEXT | NOT NULL | Hashed password |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration time |

### Inventory Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | Owner user ID |
| name | TEXT | NOT NULL | Item name |
| quantity | INTEGER | NOT NULL | Stock quantity |
| price | REAL | NOT NULL | Unit price |
| category | TEXT | NOT NULL | Item category |
| image_filename | TEXT | | Uploaded image file |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update |

## Security Features

- **Password Hashing**: Passwords are hashed using Werkzeug's security functions
- **Session Management**: Flask-Login handles secure session management
- **User Isolation**: Each user can only see and manage their own inventory
- **CSRF Protection**: Form submissions use Flask's built-in security
- **File Validation**: Image uploads are validated for allowed extensions

## Code Structure

### app.py

The main application file is organized into sections:

1. **Configuration**: App setup, secret keys, upload settings
2. **User Model**: Flask-Login integration for session management
3. **Database Functions**: Connection and initialization helpers
4. **Authentication Routes**: Register, login, logout
5. **Inventory Routes**: CRUD operations with image handling
6. **Utility Functions**: Date formatting, file handling

### Templates

Using Jinja2 template inheritance:

- **base.html**: Common layout with navigation and footer
- **Authentication pages**: Login and registration forms
- **Inventory pages**: Dashboard, forms, and item views

### Styling

Modern CSS with:

- CSS custom properties for theming
- Responsive grid layouts
- Card-based item display
- Image upload preview
- Visual stock status indicators

## Validation Rules

### User Registration
- Username: At least 3 characters, unique
- Email: Valid email format, unique
- Password: At least 6 characters

### Inventory Items
- All fields (name, quantity, price, category) are required
- Quantity must be a non-negative integer
- Price must be a non-negative decimal
- Images must be PNG, JPG, JPEG, GIF, or WEBP (max 5MB)

## Future Enhancements

Potential improvements for future versions:
- Password reset via email
- User profile management
- Bulk import/export (CSV)
- Category dropdown with preset options
- Inventory reports and analytics
- Low stock email notifications
- Multiple image support per item
- Barcode/QR code scanning

## License

This project is developed for educational purposes as part of a university module.

## Acknowledgements

- Flask Documentation: https://flask.palletsprojects.com/
- Flask-Login Documentation: https://flask-login.readthedocs.io/
- SQLite Documentation: https://sqlite.org/docs.html
- Werkzeug Security: https://werkzeug.palletsprojects.com/
- Draw.io Documentation: https://www.draw.io/
