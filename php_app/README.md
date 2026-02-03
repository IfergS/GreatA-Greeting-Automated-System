# GreetA - Faculty Attendance System (PHP)

PHP web version of the GreetA Faculty Attendance System. Uses MySQL and session-based admin login.

## Requirements

- PHP 7.4+ (with PDO MySQL)
- MySQL 5.7+ or MariaDB (e.g. XAMPP)

## Setup

### 1. Database

- Start MySQL (e.g. XAMPP → Start MySQL).
- Create database and tables:

```bash
# In MySQL (phpMyAdmin or mysql CLI):
mysql -u root -p < sql/schema.sql
```

Or in phpMyAdmin: open **SQL** tab, paste contents of `sql/schema.sql`, run.

### 2. Config

Edit `config/database.php` if needed (default: host `localhost`, db `greeta_attendance`, user `root`, no password).

### 3. Create default admin

Open in browser (after placing app under your web root):

```
http://localhost/php_app/public/install.php
```

This creates admin user: **username** `admin`, **password** `admin123`. Run once.

### 4. Run the app

Point document root to `php_app/public` or open:

```
http://localhost/php_app/public/index.php
```

- **Login:** `index.php?page=login`
- **Home:** `index.php?page=home`
- **Take Attendance:** `index.php?page=attendance`
- **Records:** `index.php?page=attendance_records`
- **Admin Panel:** `index.php?page=admin`

## Features

- **Admin login** – Session-based; password hashed with `password_hash()`.
- **Home** – Date/time, faculty count, links to Take Attendance and Admin.
- **Take Attendance** – Select faculty by ID; one record per faculty per day.
- **Attendance Records** – View by date, export CSV (same format as Flutter/Python).
- **Admin Panel** – Add, edit, delete faculty (ID, name, email, phone).

## Directory layout

```
php_app/
├── config/
│   └── database.php      # DB credentials
├── src/
│   ├── Database.php      # PDO connection
│   ├── Auth.php          # Login/logout/session
│   ├── Faculty.php       # Faculty CRUD
│   └── Attendance.php    # Mark/list/export attendance
├── public/
│   ├── index.php         # Front controller
│   ├── install.php       # One-time: create admin
│   └── .htaccess
├── views/
│   ├── header.php, footer.php
│   ├── home.php, login.php, attendance.php, attendance_records.php
│   └── admin/
│       ├── dashboard.php
│       ├── add_faculty.php
│       └── view_faculty.php
├── sql/
│   └── schema.sql        # Full MySQL schema
└── README.md
```

## Face recognition (optional)

The Flutter app uses camera + ML Kit for face recognition. In this PHP version, attendance is marked by **selecting faculty ID** (dropdown). To add face-based check-in later you can:

- Use browser WebRTC + JavaScript face API (e.g. face-api.js) and send a match result to PHP, or
- Call your Python backend (OpenCV/FaceNet) from PHP via `exec()` or a small HTTP API and pass the captured image.

## Security

- Change the default admin password after first login.
- In production use HTTPS and set secure session cookie options in `Auth.php`.
- Do not expose `install.php` in production (delete or protect after first run).
