# 📦 Inventory Management System

A Django-based web application to manage inventory, stock levels, product details, and supplier information efficiently. Ideal for small to medium-sized businesses looking for a streamlined inventory solution.

---

## 🚀 Features

- User authentication (admin/staff roles)
- Product & Category management
- Real-time stock tracking
- Supplier & purchase order management
- Inventory reports & analytics
- Search & filtering functionality
- Responsive web design

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite (default), can be configured for PostgreSQL/MySQL
- **Tools:** Django Admin, Django REST Framework (optional), VS Code

---

## 📦 Installation & Setup

Make sure Python and pip are installed.

```bash
# Clone the repository
git clone https://github.com/yourusername/inventory-management-system.git
cd inventory-management-system

# Create a virtual environment
python -m venv env 
source env/bin/activate  # for Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py creates
