from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "hotel_secret_key_2025"

# ─── DB CONFIG ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",         # ← change to your MySQL username
    "password": "bilal1212",         # ← change to your MySQL password
    "database": "hotel_database"
}

def get_db():
    """Return a fresh MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    result = None
    if fetchone:  result = cur.fetchone()
    if fetchall:  result = cur.fetchall()
    if commit:    conn.commit()
    cur.close()
    conn.close()
    return result

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════════════════════

# ─── HOME ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    stats = {
        "total_rooms":     query("SELECT COUNT(*) AS n FROM rooms",    fetchone=True)["n"],
        "available_rooms": query("SELECT COUNT(*) AS n FROM rooms WHERE availability='Available'", fetchone=True)["n"],
        "total_customers": query("SELECT COUNT(*) AS n FROM customers", fetchone=True)["n"],
        "total_staff":     query("SELECT COUNT(*) AS n FROM staff",     fetchone=True)["n"],
        "total_revenue":   query("SELECT COALESCE(SUM(amount),0) AS n FROM payments", fetchone=True)["n"],
    }
    return render_template("index.html", stats=stats)

# ─── ROOMS ───────────────────────────────────────────────────────────────────
@app.route("/rooms")
def rooms():
    all_rooms = query("SELECT * FROM rooms ORDER BY room_id", fetchall=True)
    return render_template("rooms.html", rooms=all_rooms)

@app.route("/rooms/available")
def available_rooms():
    avail = query("SELECT * FROM rooms WHERE availability='Available' ORDER BY room_id", fetchall=True)
    return render_template("rooms.html", rooms=avail, filter_label="Available Rooms")

# ─── CUSTOMERS ───────────────────────────────────────────────────────────────
@app.route("/customers")
def customers():
    all_customers = query("""
        SELECT c.*, r.type AS room_type
        FROM customers c
        JOIN rooms r ON c.room_id = r.room_id
        ORDER BY c.customer_id
    """, fetchall=True)
    return render_template("customers.html", customers=all_customers)

# ─── BOOK A ROOM ─────────────────────────────────────────────────────────────
@app.route("/book", methods=["GET","POST"])
def book():
    if request.method == "POST":
        name           = request.form["name"].strip()
        cnic           = request.form["cnic"].strip()
        location       = request.form["location"].strip()
        payment_method = request.form["payment_method"].strip()
        check_in       = request.form["check_in"]
        check_out      = request.form["check_out"]

        # Validation
        if not all([name, cnic, location, payment_method, check_in, check_out]):
            flash("All fields are required!", "danger")
            return redirect(url_for("book"))

        # Find first available room
        room = query("SELECT * FROM rooms WHERE availability='Available' ORDER BY room_id LIMIT 1", fetchone=True)
        if not room:
            flash("No rooms available at the moment!", "warning")
            return redirect(url_for("book"))

        try:
            # Insert customer
            query("""
                INSERT INTO customers (name, cnic, location, payment_method, room_id, check_in, check_out)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (name, cnic, location, payment_method, room["room_id"], check_in, check_out), commit=True)

            # Mark room as booked
            query("UPDATE rooms SET availability='Booked' WHERE room_id=%s", (room["room_id"],), commit=True)

            flash(f"Room {room['room_id']} ({room['type']}) successfully booked for {name}!", "success")
            return redirect(url_for("customers"))
        except Error as e:
            flash(f"Booking failed: {e}", "danger")
            return redirect(url_for("book"))

    return render_template("book.html")

# ─── CHECKOUT ────────────────────────────────────────────────────────────────
@app.route("/checkout", methods=["GET","POST"])
def checkout():
    if request.method == "POST":
        name   = request.form["name"].strip()
        amount = request.form.get("amount", "0").strip()

        customer = query("SELECT * FROM customers WHERE name=%s", (name,), fetchone=True)
        if not customer:
            flash(f"Customer '{name}' not found!", "danger")
            return redirect(url_for("checkout"))

        try:
            # Record payment
            if amount and float(amount) > 0:
                query("""
                    INSERT INTO payments (customer_id, amount, payment_date)
                    VALUES (%s, %s, CURDATE())
                """, (customer["customer_id"], float(amount)), commit=True)

            # Free up the room
            query("UPDATE rooms SET availability='Available' WHERE room_id=%s",
                  (customer["room_id"],), commit=True)

            # Remove customer
            query("DELETE FROM customers WHERE customer_id=%s",
                  (customer["customer_id"],), commit=True)

            flash(f"{name} has successfully checked out. Room {customer['room_id']} is now available.", "success")
            return redirect(url_for("index"))
        except Error as e:
            flash(f"Checkout failed: {e}", "danger")
            return redirect(url_for("checkout"))

    all_customers = query("SELECT name, room_id FROM customers ORDER BY name", fetchall=True)
    return render_template("checkout.html", customers=all_customers)

# ─── STAFF ───────────────────────────────────────────────────────────────────
@app.route("/staff")
def staff():
    all_staff = query("SELECT * FROM staff ORDER BY staff_id", fetchall=True)
    return render_template("staff.html", staff=all_staff)

@app.route("/staff/add", methods=["GET","POST"])
def add_staff():
    if request.method == "POST":
        name     = request.form["name"].strip()
        position = request.form["position"].strip()
        email    = request.form["email"].strip()
        if not all([name, position]):
            flash("Name and position are required!", "danger")
            return redirect(url_for("add_staff"))
        query("INSERT INTO staff (name, position, email) VALUES (%s,%s,%s)",
              (name, position, email), commit=True)
        flash(f"Staff member '{name}' added successfully!", "success")
        return redirect(url_for("staff"))
    return render_template("add_staff.html")

# ─── PAYMENTS ────────────────────────────────────────────────────────────────
@app.route("/payments")
def payments():
    all_payments = query("""
        SELECT p.*, c.name AS customer_name, c.room_id
        FROM payments p
        LEFT JOIN customers c ON p.customer_id = c.customer_id
        ORDER BY p.payment_date DESC
    """, fetchall=True)
    total = query("SELECT COALESCE(SUM(amount),0) AS total FROM payments", fetchone=True)["total"]
    return render_template("payments.html", payments=all_payments, total=total)

# ─── DAILY REPORT ─────────────────────────────────────────────────────────────
@app.route("/report")
def report():
    data = {
        "total_rooms":     query("SELECT COUNT(*) AS n FROM rooms", fetchone=True)["n"],
        "available_rooms": query("SELECT COUNT(*) AS n FROM rooms WHERE availability='Available'", fetchone=True)["n"],
        "booked_rooms":    query("SELECT COUNT(*) AS n FROM rooms WHERE availability='Booked'", fetchone=True)["n"],
        "total_customers": query("SELECT COUNT(*) AS n FROM customers", fetchone=True)["n"],
        "total_staff":     query("SELECT COUNT(*) AS n FROM staff", fetchone=True)["n"],
        "total_revenue":   query("SELECT COALESCE(SUM(amount),0) AS n FROM payments", fetchone=True)["n"],
        "today_revenue":   query("SELECT COALESCE(SUM(amount),0) AS n FROM payments WHERE payment_date=CURDATE()", fetchone=True)["n"],
        "room_types":      query("SELECT type, COUNT(*) AS total, SUM(availability='Booked') AS booked FROM rooms GROUP BY type", fetchall=True),
        "recent_bookings": query("""
            SELECT c.name, c.room_id, r.type, c.check_in, c.check_out, c.payment_method
            FROM customers c JOIN rooms r ON c.room_id=r.room_id
            ORDER BY c.customer_id DESC LIMIT 5
        """, fetchall=True),
    }
    return render_template("report.html", data=data)

# ─── ROOM SERVICES ───────────────────────────────────────────────────────────
@app.route("/services")
def services():
    all_services = query("""
        SELECT rs.*, r.type AS room_type
        FROM room_services rs
        JOIN rooms r ON rs.room_id = r.room_id
        ORDER BY rs.service_id
    """, fetchall=True)
    return render_template("services.html", services=all_services)

@app.route("/services/add", methods=["GET","POST"])
def add_service():
    if request.method == "POST":
        room_id      = request.form["room_id"]
        service_type = request.form["service_type"].strip()
        cost         = request.form["cost"]
        query("INSERT INTO room_services (room_id, service_type, service_cost) VALUES (%s,%s,%s)",
              (room_id, service_type, cost), commit=True)
        flash("Service added successfully!", "success")
        return redirect(url_for("services"))
    all_rooms = query("SELECT room_id, type FROM rooms ORDER BY room_id", fetchall=True)
    return render_template("add_service.html", rooms=all_rooms)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
