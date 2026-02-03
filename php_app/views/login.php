<div class="card" style="max-width: 400px; margin: 2rem auto;">
    <h2 style="margin-top: 0;">Admin Login</h2>
    <?php if (!empty($error)): ?>
        <div class="alert alert-error"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>
    <form method="post" action="index.php?page=login">
        <p>
            <label>Username</label><br>
            <input type="text" name="username" required autofocus style="width: 100%;">
        </p>
        <p>
            <label>Password</label><br>
            <input type="password" name="password" required style="width: 100%;">
        </p>
        <p>
            <button type="submit" class="btn">Login</button>
        </p>
    </form>
    <p class="muted">Default: admin / admin123 (run install.php once to create)</p>
</div>
