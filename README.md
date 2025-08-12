Inventory Plus - Professional Corporate Inventory Management System
Inventory Plus is a comprehensive, professional-grade inventory management system built with Django, designed for corporate environments. It features a modern UI/UX, role-based access control, and real-time stock tracking.


Models
https://docs.google.com/document/d/1uJZedke8GIPMrp_K3vydkQENxrkBg8HsyCrszzJkUXU/edit?usp=sharing


Canva
https://www.canva.com/design/DAGvqWZio5A/9P3RdXMMlNn5rzolI670jw/edit?utm_content=DAGvqWZio5A&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton



It have 6 apps: 
1-Account 
2-dashboard 
3-inventory
4-suppliers
5-notifications
6-product


Features
Core Functionality
Product Management: Complete CRUD operations for products with detailed information

Category Management: Organize products with hierarchical categories

Supplier Management: Comprehensive supplier database with contact information

Stock Management: Real-time stock tracking with movement history

User Management: Role-based access control (Admin, Manager, Employee)

Search & Filtering: Advanced search with multiple filter options

Advanced Features
Dashboard Analytics: Real-time statistics and KPI monitoring

Low Stock Alerts: Automated notifications for inventory management

Stock Movement Tracking: Complete audit trail for all stock changes

Responsive Design: Mobile-friendly interface with modern animations

Email Notifications: Automated alerts for low stock and expiry dates 



Technical Features
Modern UI: Bootstrap 5 with custom animations and gradients

Responsive: Mobile-first design approach

Performance: Optimized queries and caching

Analytics: Built-in dashboard with charts and statistics



Technology Stack
Backend: Django 4.2.7, Python 3.10+

Database: SQLite

Frontend: Bootstrap 5, HTML5, CSS3, JavaScript

UI Components: Bootstrap Icons, Animate.css

Forms: Django Crispy Forms with Bootstrap 5

Authentication: Django built-in authentication system

File Handling: Pillow for image processing


Requirements
System Requirements
Python 3.10 or higher

Django 4.2.7



Python Dependencies
txt
Django==4.2.7
python-dotenv==1.0.0
Pillow==10.1.0
django-crispy-forms==2.1
crispy-bootstrap5==0.7
django-extensions==3.2.3
Quick Start
Clone the Repository


Create a .env file in the project root:

env
نسخ
تحرير
SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
MANAGER_EMAIL=manager@company.com
Database Setup



User Accounts
Default Login Credentials
Administrator Account

Username: admin

Password: admin123

Permissions: Full access to all features

Employee Account

Username: employee

Password: emp123

Permissions: Limited access (view/update products, manage stock)

System Architecture
Models Overview
User Management

UserProfile: Extended user model with role-based permissions

Roles: Admin, Manager, Employee with different access levels

Inventory Core

Product: Complete product information with pricing and stock data

Category: Product categorization system

Supplier: Supplier management with contact details

StockMovement: Audit trail for all stock changes