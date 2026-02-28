# InvenTrack - Inventory Management System

A Django-based web application to manage inventory, stock levels, orders, suppliers, and user activity. Built for small to medium-sized businesses looking for a streamlined inventory solution with role-based access control and real-time analytics.

---

## Features

### Dashboard & Analytics
- Overview statistics: total products, orders, users, and suppliers
- Low stock alerts for items with quantity ≤ 10
- Recent orders feed
- Category distribution pie chart and order status bar chart (Chart.js)
- Recent activity feed
- Role-based dashboard views (admin vs regular users)

### Product Management
- Full CRUD operations for products
- Categories: Stationary, Electronics, Food, Sports
- Search by name/description and filter by category
- Link products to suppliers
- Quantity tracking with automatic stock adjustments
- Export product data to CSV

### Order Management
- Create orders linked to products and users
- Order statuses: Pending, Approved, Delivered, Cancelled
- Admins can update order status inline
- Automatic stock adjustment on approval/cancellation
- Users see only their own orders; admins see all
- Export order data to CSV

### Supplier Management (Admin Only)
- Full CRUD operations for suppliers
- Fields: name, contact person, email, phone, address
- Search by name, contact person, or email

### User Management & Authentication
- User registration and login/logout
- User profiles with profile picture, address, and mobile number
- Password change functionality
- User listing for admins
- Role-based access control (admin/staff vs regular users)

### Activity Logging
- Tracks product, order, supplier, and stock changes
- Records user, action type, description, and timestamp
- Admin-only activity log view

---

## Tech Stack

| Layer       | Technology                                      |
|-------------|------------------------------------------------|
| Backend     | Django 5.0.7 (Python)                          |
| Frontend    | Bootstrap 5.3, Bootstrap Icons, Google Fonts   |
| Charts      | Chart.js 4.4                                   |
| Forms       | Django Crispy Forms + crispy-bootstrap5         |
| Images      | Pillow                                         |
| Database    | SQLite (default), configurable for PostgreSQL/MySQL |

---

## Installation & Setup

**Prerequisites:** Python 3.10+ and pip

```bash
# Clone the repository
git clone https://github.com/yourusername/Django-Based-Inventory-Management.git
cd Django-Based-Inventory-Management

# Create and activate a virtual environment
python -m venv env
# Linux/macOS:
source env/bin/activate
# Windows:
env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## URL Routes

| URL                          | Description                  | Access       |
|------------------------------|------------------------------|-------------|
| `/`                          | Dashboard                    | All users   |
| `/products/`                 | Product listing              | All users   |
| `/products/<id>/`            | Product detail               | All users   |
| `/products/<id>/edit/`       | Edit product                 | Admin       |
| `/products/<id>/delete/`     | Delete product               | Admin       |
| `/products/export/`          | Export products to CSV        | Admin       |
| `/orders/`                   | Order listing                | All users   |
| `/orders/<id>/delete/`       | Delete order                 | Admin       |
| `/orders/<id>/status/`       | Update order status           | Admin       |
| `/orders/export/`            | Export orders to CSV          | Admin       |
| `/suppliers/`                | Supplier listing             | Admin       |
| `/suppliers/<id>/edit/`      | Edit supplier                | Admin       |
| `/suppliers/<id>/delete/`    | Delete supplier              | Admin       |
| `/users/`                    | User listing                 | Admin       |
| `/user/`                     | User profile                 | All users   |
| `/password/`                 | Change password              | All users   |
| `/activity/`                 | Activity log                 | Admin       |
| `/register/`                 | User registration            | Public      |
| `/login/`                    | Login                        | Public      |
| `/logout/`                   | Logout                       | All users   |
| `/admin/`                    | Django admin panel           | Superuser   |

---

## Project Structure

```
Django-Based-Inventory-Management/
├── myproject/                  # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── inventory/                  # Main application
│   ├── models.py               # Product, Order, Supplier, UserProfile, ActivityLog
│   ├── views.py                # All view functions
│   ├── forms.py                # Django forms
│   ├── admin.py                # Admin panel configuration
│   ├── migrations/
│   └── templates/
│       ├── base.html           # Base layout with sidebar navigation
│       ├── index.html          # Dashboard
│       ├── products.html       # Product management
│       ├── orders.html         # Order management
│       ├── suppliers.html      # Supplier management
│       ├── users.html          # User listing
│       ├── user.html           # User profile
│       ├── activity_log.html   # Activity log
│       ├── login.html
│       ├── logout.html
│       └── register.html
├── static/                     # Static files (CSS, JS, images)
├── media/                      # Uploaded files (profile pictures)
├── manage.py
├── requirements.txt
└── README.md
```

---

## Data Models

- **UserProfile** — extends Django User with profile picture, address, and mobile number
- **Product** — name, category, quantity, description, linked supplier
- **Order** — product, created by user, quantity, status (Pending/Approved/Delivered/Cancelled), date
- **Supplier** — name, contact person, email, phone, address
- **ActivityLog** — user, action type, description, timestamp

---

## Dependencies

```
Django==5.0.7
django-crispy-forms==2.3
crispy-bootstrap5==2024.2
pillow==10.4.0
asgiref==3.8.1
sqlparse==0.5.1
tzdata==2024.1
```
