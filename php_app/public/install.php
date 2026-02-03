<?php
/**
 * One-time setup: create default admin (admin / admin123)
 * Run once after importing sql/schema.sql
 */
require_once dirname(__DIR__) . '/bootstrap.php';

use GreetA\Database;

try {
    $pdo = Database::getConnection();
    $stmt = $pdo->query("SELECT 1 FROM admins WHERE username = 'admin' LIMIT 1");
    if ($stmt->fetch()) {
        echo 'Admin user already exists. No action needed.';
        exit;
    }
    $hash = password_hash('admin123', PASSWORD_DEFAULT);
    $stmt = $pdo->prepare('INSERT INTO admins (username, password, email, fullName, isActive) VALUES (?, ?, ?, ?, 1)');
    $stmt->execute(['admin', $hash, 'admin@greeta.com', 'System Administrator']);
    echo 'Default admin created: username = admin, password = admin123';
} catch (Throwable $e) {
    echo 'Error: ' . htmlspecialchars($e->getMessage());
}
