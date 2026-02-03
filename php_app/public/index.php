<?php
/**
 * GreetA - Faculty Attendance System (PHP)
 * Front controller: ?page=home|login|logout|attendance|attendance_records|admin|admin_add_faculty|admin_view_faculty|admin_delete_faculty
 */
require_once dirname(__DIR__) . '/bootstrap.php';

use GreetA\Auth;
use GreetA\Faculty;
use GreetA\Attendance;

$page = $_GET['page'] ?? 'home';
$baseUrl = 'index.php';

// Logout
if ($page === 'logout') {
    Auth::logout();
    header('Location: ' . $baseUrl . '?page=login');
    exit;
}

// Public: login only
if ($page === 'login') {
    $error = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $user = $_POST['username'] ?? '';
        $pass = $_POST['password'] ?? '';
        if (Auth::login($user, $pass)) {
            header('Location: ' . $baseUrl . '?page=home');
            exit;
        }
        $error = 'Invalid username or password.';
    }
    if (Auth::isLoggedIn()) {
        header('Location: ' . $baseUrl . '?page=home');
        exit;
    }
    $pageTitle = 'Admin Login';
    include dirname(__DIR__) . '/views/header.php';
    include dirname(__DIR__) . '/views/login.php';
    include dirname(__DIR__) . '/views/footer.php';
    exit;
}

// Protected pages
Auth::requireLogin();

// Take attendance (mark by faculty ID)
if ($page === 'attendance_mark' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $facultyId = trim($_POST['faculty_id'] ?? '');
    $faculty = Faculty::getById($facultyId);
    if (!$faculty) {
        $_SESSION['attendance_error'] = 'Faculty ID not found.';
    } elseif (Attendance::alreadyMarkedToday($facultyId)) {
        $_SESSION['attendance_error'] = $faculty->name . ' already marked attendance today.';
    } else {
        Attendance::mark($faculty->id, $faculty->name);
        $_SESSION['attendance_success'] = 'Welcome, ' . $faculty->name . '! Attendance recorded.';
    }
    header('Location: ' . $baseUrl . '?page=attendance');
    exit;
}

// Export CSV
if ($page === 'export_csv') {
    $date = $_GET['date'] ?? date('Y-m-d');
    header('Content-Type: text/csv; charset=UTF-8');
    header('Content-Disposition: attachment; filename="Attendance_' . $date . '.csv"');
    echo Attendance::exportCsv($date);
    exit;
}

// Admin: delete faculty
if ($page === 'admin_delete_faculty') {
    $id = $_GET['id'] ?? '';
    if ($id && Faculty::getById($id)) {
        Faculty::delete($id);
        $_SESSION['message'] = 'Faculty deleted.';
    }
    header('Location: ' . $baseUrl . '?page=admin');
    exit;
}

// Admin: add/update faculty
if ($page === 'admin_save_faculty' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $id = trim($_POST['faculty_id'] ?? '');
    $name = trim($_POST['name'] ?? '');
    $email = trim($_POST['email'] ?? '') ?: null;
    $phone = trim($_POST['phone'] ?? '') ?: null;
    if ($id && $name) {
        $existing = Faculty::getById($id);
        if ($existing) {
            Faculty::update($id, $name, $email, $phone);
            $_SESSION['message'] = 'Faculty updated.';
        } else {
            Faculty::create($id, $name, $email, $phone);
            $_SESSION['message'] = 'Faculty added.';
        }
    }
    header('Location: ' . $baseUrl . '?page=admin');
    exit;
}

// Page routing
$pageTitle = 'GreetA - Faculty Attendance';
switch ($page) {
    case 'home':
        $pageTitle = 'Home';
        $facultyCount = Faculty::count();
        include dirname(__DIR__) . '/views/header.php';
        include dirname(__DIR__) . '/views/home.php';
        include dirname(__DIR__) . '/views/footer.php';
        break;
    case 'attendance':
        $pageTitle = 'Take Attendance';
        $facultyList = Faculty::getAll();
        include dirname(__DIR__) . '/views/header.php';
        include dirname(__DIR__) . '/views/attendance.php';
        include dirname(__DIR__) . '/views/footer.php';
        break;
    case 'attendance_records':
        $pageTitle = 'Attendance Records';
        $date = $_GET['date'] ?? date('Y-m-d');
        $records = Attendance::getForDate($date);
        include dirname(__DIR__) . '/views/header.php';
        include dirname(__DIR__) . '/views/attendance_records.php';
        include dirname(__DIR__) . '/views/footer.php';
        break;
    case 'admin':
        $pageTitle = 'Admin Panel';
        $facultyList = Faculty::getAll();
        include dirname(__DIR__) . '/views/header.php';
        include dirname(__DIR__) . '/views/admin/dashboard.php';
        include dirname(__DIR__) . '/views/footer.php';
        break;
    case 'admin_add_faculty':
        $pageTitle = 'Add Faculty';
        include dirname(__DIR__) . '/views/header.php';
        include dirname(__DIR__) . '/views/admin/add_faculty.php';
        include dirname(__DIR__) . '/views/footer.php';
        break;
    case 'admin_view_faculty':
        $id = $_GET['id'] ?? '';
        $faculty = $id ? Faculty::getById($id) : null;
        $pageTitle = $faculty ? 'Edit Faculty' : 'Faculty';
        include dirname(__DIR__) . '/views/header.php';
        include dirname(__DIR__) . '/views/admin/view_faculty.php';
        include dirname(__DIR__) . '/views/footer.php';
        break;
    default:
        header('Location: ' . $baseUrl . '?page=home');
        exit;
}
