<?php if (!$faculty): ?>
    <p class="muted">Faculty not found.</p>
    <a href="index.php?page=admin" class="btn">Back to Admin</a>
<?php else: ?>
<div class="card">
    <h2 style="margin-top: 0;">Edit Faculty</h2>
    <form method="post" action="index.php?page=admin_save_faculty">
        <input type="hidden" name="faculty_id" value="<?= htmlspecialchars($faculty->id) ?>">
        <p>
            <label>Faculty ID</label><br>
            <input type="text" value="<?= htmlspecialchars($faculty->id) ?>" disabled style="width: 100%; background: #222;">
        </p>
        <p>
            <label>Full Name</label><br>
            <input type="text" name="name" value="<?= htmlspecialchars($faculty->name) ?>" required style="width: 100%;">
        </p>
        <p>
            <label>Email (optional)</label><br>
            <input type="email" name="email" value="<?= htmlspecialchars($faculty->email ?? '') ?>" style="width: 100%;">
        </p>
        <p>
            <label>Phone (optional)</label><br>
            <input type="text" name="phone" value="<?= htmlspecialchars($faculty->phone ?? '') ?>" style="width: 100%;">
        </p>
        <p>
            <button type="submit" class="btn">Update</button>
            <a href="index.php?page=admin" class="btn btn-secondary">Cancel</a>
        </p>
    </form>
</div>
<?php endif; ?>
