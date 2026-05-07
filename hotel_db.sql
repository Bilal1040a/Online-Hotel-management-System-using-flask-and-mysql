-- ============================================================
--  HOTEL BOOKING SYSTEM — SQL Script
--  Run this in MySQL Workbench or terminal before starting app
-- ============================================================

-- 1. Create and select database
CREATE DATABASE IF NOT EXISTS hotel_db;
USE hotel_db;

-- ============================================================
--  TABLE CREATION (DDL)
-- ============================================================

-- Drop tables in safe order (child → parent)
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS room_services;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS staff;

-- ROOMS
CREATE TABLE rooms (
    room_id      VARCHAR(10)   PRIMARY KEY,
    type         VARCHAR(50)   NOT NULL,
    price        DECIMAL(10,2) NOT NULL,
    availability VARCHAR(20)   NOT NULL DEFAULT 'Available',
    CONSTRAINT chk_availability CHECK (availability IN ('Available','Booked'))
);

-- STAFF
CREATE TABLE staff (
    staff_id   INT           PRIMARY KEY AUTO_INCREMENT,
    name       VARCHAR(100)  NOT NULL,
    position   VARCHAR(50)   NOT NULL,
    email      VARCHAR(150)  UNIQUE
);

-- CUSTOMERS (checked-in guests)
CREATE TABLE customers (
    customer_id    INT           PRIMARY KEY AUTO_INCREMENT,
    name           VARCHAR(100)  NOT NULL,
    cnic           VARCHAR(20)   NOT NULL,
    location       VARCHAR(100)  NOT NULL,
    payment_method VARCHAR(50)   NOT NULL,
    room_id        VARCHAR(10)   NOT NULL,
    check_in       DATE          NOT NULL,
    check_out      DATE          NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

-- PAYMENTS
CREATE TABLE payments (
    payment_id   INT           PRIMARY KEY AUTO_INCREMENT,
    customer_id  INT,
    amount       DECIMAL(10,2) NOT NULL,
    payment_date DATE          NOT NULL DEFAULT (CURDATE()),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
);

-- ROOM SERVICES
CREATE TABLE room_services (
    service_id   INT           PRIMARY KEY AUTO_INCREMENT,
    room_id      VARCHAR(10)   NOT NULL,
    service_type VARCHAR(100)  NOT NULL,
    service_cost DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

-- ============================================================
--  SAMPLE DATA (DML — INSERT)
-- ============================================================

-- Rooms (10 rooms like original Java project)
INSERT INTO rooms (room_id, type, price, availability) VALUES
('R01', 'Standard',  8000.00, 'Available'),
('R02', 'Standard',  8000.00, 'Available'),
('R03', 'Standard',  8000.00, 'Available'),
('R04', 'Deluxe',   15000.00, 'Available'),
('R05', 'Deluxe',   15000.00, 'Available'),
('R06', 'Deluxe',   15000.00, 'Available'),
('R07', 'Suite',    30000.00, 'Available'),
('R08', 'Suite',    30000.00, 'Available'),
('R09', 'Suite',    30000.00, 'Available'),
('R10', 'Suite',    30000.00, 'Available');

-- Staff (same as Java project + extras)
INSERT INTO staff (name, position, email) VALUES
('Ali',    'Manager',       'ali@hotel.com'),
('Sara',   'Receptionist',  'sara@hotel.com'),
('John',   'Cleaner',       'john@hotel.com'),
('Ahmed',  'Security',      'ahmed@hotel.com'),
('Fatima', 'Chef',          'fatima@hotel.com');

-- Sample Customers
INSERT INTO customers (name, cnic, location, payment_method, room_id, check_in, check_out) VALUES
('Bilal Ahmed',  '35202-1234567-1', 'Rawalpindi', 'Cash',        'R01', '2025-05-01', '2025-05-05'),
('Sara Khan',    '35202-9876543-2', 'Lahore',     'Credit Card', 'R04', '2025-05-02', '2025-05-07'),
('Umar Farooq',  '35202-5555555-3', 'Islamabad',  'Online',      'R07', '2025-05-03', '2025-05-10');

-- Mark booked rooms
UPDATE rooms SET availability='Booked' WHERE room_id IN ('R01','R04','R07');

-- Sample Payments
INSERT INTO payments (customer_id, amount, payment_date) VALUES
(1, 32000.00, '2025-05-01'),
(2, 75000.00, '2025-05-02'),
(3, 210000.00,'2025-05-03');

-- Sample Room Services
INSERT INTO room_services (room_id, service_type, service_cost) VALUES
('R01', 'Room Cleaning', 500.00),
('R01', 'Laundry',       800.00),
('R04', 'Room Service', 1500.00),
('R04', 'WiFi',          200.00),
('R07', 'Mini Bar',     2000.00),
('R07', 'Room Cleaning',  500.00);

-- ============================================================
--  SQL QUERIES (DQL)
-- ============================================================

-- Q1: All rooms with status
SELECT room_id, type, price, availability
FROM rooms
ORDER BY room_id;

-- Q2: Available rooms only
SELECT room_id, type, price
FROM rooms
WHERE availability = 'Available'
ORDER BY price ASC;

-- Q3: All current customers with room info
SELECT c.customer_id, c.name, c.cnic, c.location,
       c.payment_method, c.room_id, r.type AS room_type,
       c.check_in, c.check_out
FROM customers c
JOIN rooms r ON c.room_id = r.room_id
ORDER BY c.customer_id;

-- Q4: All staff
SELECT staff_id, name, position, email
FROM staff
ORDER BY staff_id;

-- Q5: All payments with customer names
SELECT p.payment_id, c.name AS customer_name, c.room_id,
       p.amount, p.payment_date
FROM payments p
LEFT JOIN customers c ON p.customer_id = c.customer_id
ORDER BY p.payment_date DESC;

-- Q6: Total revenue
SELECT SUM(amount) AS total_revenue
FROM payments;

-- Q7: Today's revenue
SELECT SUM(amount) AS today_revenue
FROM payments
WHERE payment_date = CURDATE();

-- Q8: Daily report summary
SELECT
    (SELECT COUNT(*) FROM rooms)                        AS total_rooms,
    (SELECT COUNT(*) FROM rooms WHERE availability='Available') AS available_rooms,
    (SELECT COUNT(*) FROM rooms WHERE availability='Booked')    AS booked_rooms,
    (SELECT COUNT(*) FROM customers)                    AS total_customers,
    (SELECT COUNT(*) FROM staff)                        AS total_staff,
    (SELECT COALESCE(SUM(amount),0) FROM payments)      AS total_revenue;

-- Q9: Rooms by type with occupancy
SELECT type,
       COUNT(*) AS total_rooms,
       SUM(availability = 'Booked') AS booked,
       SUM(availability = 'Available') AS available
FROM rooms
GROUP BY type;

-- Q10: Services per room with cost
SELECT rs.service_id, rs.room_id, r.type AS room_type,
       rs.service_type, rs.service_cost
FROM room_services rs
JOIN rooms r ON rs.room_id = r.room_id
ORDER BY rs.room_id;

-- Q11: Total service cost per room
SELECT rs.room_id, r.type,
       SUM(rs.service_cost) AS total_service_cost
FROM room_services rs
JOIN rooms r ON rs.room_id = r.room_id
GROUP BY rs.room_id, r.type
ORDER BY total_service_cost DESC;

-- Q12: Most expensive room type
SELECT type, MAX(price) AS price_per_night
FROM rooms
GROUP BY type
ORDER BY price_per_night DESC;

-- Q13: Revenue by payment method
SELECT c.payment_method,
       COUNT(*) AS transactions,
       SUM(p.amount) AS total_amount
FROM payments p
JOIN customers c ON p.customer_id = c.customer_id
GROUP BY c.payment_method;

-- Q14: Checkout customer (example: customer_id = 1)
-- Step 1: Record final payment if needed
-- INSERT INTO payments (customer_id, amount) VALUES (1, 32000.00);
-- Step 2: Free the room
-- UPDATE rooms SET availability='Available' WHERE room_id = 'R01';
-- Step 3: Remove customer
-- DELETE FROM customers WHERE customer_id = 1;

-- Q15: Search customer by name
SELECT c.*, r.type AS room_type
FROM customers c
JOIN rooms r ON c.room_id = r.room_id
WHERE c.name LIKE '%Bilal%';
