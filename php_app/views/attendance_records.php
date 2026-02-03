<form method="get" action="index.php" style="margin-bottom: 1rem;">
    <input type="hidden" name="page" value="attendance_records">
    <label>Date:</label>
    <input type="date" name="date" value="<?= htmlspecialchars($date) ?>">
    <button type="submit" class="btn">View</button>
    <a href="index.php?page=export_csv&date=<?= urlencode($date) ?>" class="btn btn-secondary">Export CSV</a>
</form>
<div class="card">
    <h2 style="margin-top: 0;">Attendance for <?= htmlspecialchars($date) ?></h2>
    <?php if (empty($records)): ?>
        <p class="muted">No attendance records for this date.</p>
    <?php else: ?>
        <table>
            <thead>
                <tr><th>ID</th><th>Name</th><th>Time</th><th>Status</th></tr>
            </thead>
            <tbody>
                <?php foreach ($records as $r): ?>
                    <tr>
                        <td><?= htmlspecialchars($r->facultyId) ?></td>
                        <td><?= htmlspecialchars($r->facultyName) ?></td>
                        <td><?= htmlspecialchars($r->time) ?></td>
                        <td><?= htmlspecialchars($r->status) ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    <?php endif; ?>
</div>
