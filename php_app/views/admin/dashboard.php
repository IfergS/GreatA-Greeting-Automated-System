<?php
$message = $_SESSION['message'] ?? null;
unset($_SESSION['message']);
?>
<?php if ($message): ?>
    <div class="alert alert-success"><?= htmlspecialchars($message) ?></div>
<?php endif; ?>
<div class="card">
    <h2 style="margin-top: 0;">Admin Panel - Faculty List</h2>
    <p><a href="index.php?page=admin_add_faculty" class="btn">+ Add Faculty</a></p>
    <?php if (empty($facultyList)): ?>
        <p class="muted">No faculty yet. Add one to get started.</p>
    <?php else: ?>
        <table>
            <thead>
                <tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Actions</th></tr>
            </thead>
            <tbody>
                <?php foreach ($facultyList as $f): ?>
                    <tr>
                        <td><?= htmlspecialchars($f->id) ?></td>
                        <td><?= htmlspecialchars($f->name) ?></td>
                        <td><?= htmlspecialchars($f->email ?? '-') ?></td>
                        <td><?= htmlspecialchars($f->phone ?? '-') ?></td>
                        <td>
                            <a href="index.php?page=admin_view_faculty&id=<?= urlencode($f->id) ?>">Edit</a>
                            &nbsp;|&nbsp;
                            <a href="index.php?page=admin_delete_faculty&id=<?= urlencode($f->id) ?>" onclick="return confirm('Delete this faculty?');">Delete</a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    <?php endif; ?>
</div>
