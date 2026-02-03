<?php
namespace GreetA;

class Auth {
    public static function startSession(): void {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
    }

    public static function login(string $username, string $password): bool {
        self::startSession();
        $db = Database::getConnection();
        $stmt = $db->prepare('SELECT id, username, password, fullName FROM admins WHERE username = ? AND isActive = 1');
        $stmt->execute([strtolower(trim($username))]);
        $row = $stmt->fetch();
        if (!$row || !password_verify($password, $row['password'])) {
            self::logLogin($username, false);
            return false;
        }
        self::logLogin($username, true);
        $db->prepare('UPDATE admins SET lastLogin = NOW() WHERE id = ?')->execute([$row['id']]);
        $_SESSION['admin_id'] = (int) $row['id'];
        $_SESSION['admin_username'] = $row['username'];
        $_SESSION['admin_name'] = $row['fullName'] ?? $row['username'];
        return true;
    }

    public static function logout(): void {
        self::startSession();
        $_SESSION = [];
        if (ini_get('session.use_cookies')) {
            $p = session_get_cookie_params();
            setcookie(session_name(), '', time() - 42000, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
        }
        session_destroy();
    }

    public static function isLoggedIn(): bool {
        self::startSession();
        return !empty($_SESSION['admin_id']);
    }

    public static function requireLogin(): void {
        if (!self::isLoggedIn()) {
            header('Location: index.php?page=login');
            exit;
        }
    }

    public static function getAdminId(): ?int {
        self::startSession();
        return isset($_SESSION['admin_id']) ? (int) $_SESSION['admin_id'] : null;
    }

    public static function getUsername(): string {
        self::startSession();
        return $_SESSION['admin_username'] ?? '';
    }

    private static function logLogin(string $username, bool $success): void {
        $db = Database::getConnection();
        $stmt = $db->prepare('INSERT INTO login_logs (username, success, ipAddress) VALUES (?, ?, ?)');
        $stmt->execute([$username, $success ? 1 : 0, $_SERVER['REMOTE_ADDR'] ?? null]);
    }
}
