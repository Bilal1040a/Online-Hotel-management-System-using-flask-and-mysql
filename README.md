# 🏨 Hotel Booking System — Python + MySQL + Flask

A web-based Hotel Booking System running on localhost.
Converted from your Java Swing project into a full web app.

---

## 📦 SETUP INSTRUCTIONS

### Step 1 — Install Python packages
```
pip install flask mysql-connector-python
```

### Step 2 — Setup MySQL Database
Open MySQL Workbench or terminal and run:
```
mysql -u root -p < hotel_db.sql
```
OR copy-paste the contents of `hotel_db.sql` into MySQL Workbench and execute.

### Step 3 — Configure DB credentials in app.py
Edit lines 11-14 in app.py:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",       ← your MySQL username
    "password": "",       ← your MySQL password
    "database": "hotel_db"
}
```

### Step 4 — Run the app
```
python app.py
```

### Step 5 — Open in browser
```
http://localhost:5000
```

---

## 🗂 PROJECT STRUCTURE

```
hotel_booking/
├── app.py                  ← Main Flask application
├── hotel_db.sql            ← MySQL database schema + queries
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
└── templates/
    ├── base.html           ← Shared layout with navbar
    ├── index.html          ← Dashboard / home
    ├── rooms.html          ← All rooms / available rooms
    ├── customers.html      ← Current guests
    ├── book.html           ← Book a room form
    ├── checkout.html       ← Checkout form
    ├── staff.html          ← Staff list
    ├── add_staff.html      ← Add staff form
    ├── services.html       ← Room services list
    ├── add_service.html    ← Add service form
    ├── payments.html       ← Payment records
    └── report.html         ← Daily report dashboard
```

---

## 🌐 PAGES / ROUTES

| URL                | Description             |
|--------------------|-------------------------|
| /                  | Dashboard with stats    |
| /rooms             | All rooms               |
| /rooms/available   | Available rooms only    |
| /customers         | Current checked-in guests |
| /book              | Book a new room         |
| /checkout          | Checkout a guest        |
| /staff             | Hotel staff list        |
| /staff/add         | Add new staff member    |
| /services          | Room services           |
| /services/add      | Add room service        |
| /payments          | Payment records         |
| /report            | Daily summary report    |

---

## 📋 DATABASE TABLES

| Table         | Description                     |
|---------------|---------------------------------|
| rooms         | 10 hotel rooms (Standard/Deluxe/Suite) |
| customers     | Currently checked-in guests      |
| payments      | Payment transaction records      |
| staff         | Hotel staff members              |
| room_services | Services linked to rooms         |

---

## 🔑 OOP CONCEPTS PRESERVED FROM JAVA PROJECT

| Java Concept     | Python/Flask Equivalent           |
|------------------|-----------------------------------|
| Person (base class) | DB table design + shared query logic |
| Customer extends Person | customers table with all fields  |
| Staff extends Person | staff table                    |
| Room class       | rooms table                       |
| Hotel class      | app.py route handlers             |
| Encapsulation    | DB columns + access via routes    |
| Inheritance      | Table structure + shared templates |
| ArrayList        | SQL queries returning lists       |
| GUI (Swing)      | HTML templates + Flask routes     |
