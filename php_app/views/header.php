<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle ?? 'GreetA') ?> - Faculty Attendance System</title>
    <style>
        :root {
            --primary: #1a1a2e;
            --secondary: #16213e;
            --accent: #2196F3;
            --text: #fff;
            --text-muted: #bdc3c7;
        }
        * { box-sizing: border-box; }
        body { margin: 0; font-family: Segoe UI, system-ui, sans-serif; background: var(--primary); color: var(--text); min-height: 100vh; }
        .header { background: var(--secondary); border-bottom: 2px solid var(--accent); padding: 1rem 1.5rem; }
        .header h1 { margin: 0; font-size: 1.5rem; }
        .header .sub { color: var(--accent); font-size: 0.9rem; }
        .nav { margin-top: 0.75rem; }
        .nav a { color: var(--accent); text-decoration: none; margin-right: 1rem; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 900px; margin: 0 auto; padding: 1.5rem; }
        .card { background: var(--secondary); border: 2px solid var(--accent); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; }
        .btn { display: inline-block; padding: 0.6rem 1.2rem; background: var(--accent); color: #fff; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; font-size: 1rem; }
        .btn:hover { opacity: 0.9; }
        .btn-secondary { background: #444; }
        input, select { padding: 0.5rem; border-radius: 6px; border: 1px solid #444; background: #333; color: #fff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.6rem; text-align: left; border-bottom: 1px solid #333; }
        .alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
        .alert-success { background: #1b5e20; color: #c8e6c9; }
        .alert-error { background: #b71c1c; color: #ffcdd2; }
        .muted { color: var(--text-muted); }
    </style>
</head>
<body>
    <?php if (isset($pageTitle) && $pageTitle !== 'Admin Login'): ?>
    <header class="header">
        <h1>🔐 GreetA - Faculty Attendance System</h1>
        <p class="sub">✨ AI-Powered Recognition & Management System ✨</p>
        <nav class="nav">
            <a href="index.php?page=home">Home</a>
            <a href="index.php?page=attendance">Take Attendance</a>
            <a href="index.php?page=attendance_records">Records</a>
            <a href="index.php?page=admin">Admin Panel</a>
            <span class="muted"><?= htmlspecialchars(\GreetA\Auth::getUsername()) ?></span>
            <a href="index.php?page=logout">Logout</a>
        </nav>
    </header>
    <?php endif; ?>
    <main class="container">
