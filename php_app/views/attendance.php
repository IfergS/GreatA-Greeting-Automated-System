<?php
$success = $_SESSION['attendance_success'] ?? null;
$error = $_SESSION['attendance_error'] ?? null;
unset($_SESSION['attendance_success'], $_SESSION['attendance_error']);
?>
<?php if ($success): ?>
    <div class="alert alert-success"><?= htmlspecialchars($success) ?></div>
<?php endif; ?>
<?php if ($error): ?>
    <div class="alert alert-error"><?= htmlspecialchars($error) ?></div>
<?php endif; ?>
<div class="card">
    <h2 style="margin-top: 0;">Take Attendance</h2>
    <p class="muted">Enter faculty ID to mark attendance for today. One record per faculty per day.</p>
    <form method="post" action="index.php?page=attendance_mark">
        <p>
            <label>Faculty ID</label><br>
            <select name="faculty_id" required style="width: 100%; min-height: 38px;">
                <option value="">-- Select faculty --</option>
                <?php foreach ($facultyList as $f): ?>
                    <option value="<?= htmlspecialchars($f->id) ?>"><?= htmlspecialchars($f->id . ' - ' . $f->name) ?></option>
                <?php endforeach; ?>
            </select>
        </p>
        <?php if (empty($facultyList)): ?>
            <p class="muted">No faculty yet. <a href="index.php?page=admin_add_faculty">Add faculty</a> in Admin Panel first.</p>
        <?php else: ?>
            <button type="submit" class="btn">Mark Attendance</button>
        <?php endif; ?>
    </form>
</div>
