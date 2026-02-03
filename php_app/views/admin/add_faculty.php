<div class="card">
    <h2 style="margin-top: 0;">Add Faculty</h2>
    <form method="post" action="index.php?page=admin_save_faculty">
        <p>
            <label>Faculty ID (unique)</label><br>
            <input type="text" name="faculty_id" required placeholder="e.g. 2021-430" style="width: 100%;">
        </p>
        <p>
            <label>Full Name</label><br>
            <input type="text" name="name" required style="width: 100%;">
        </p>
        <p>
            <label>Email (optional)</label><br>
            <input type="email" name="email" style="width: 100%;">
        </p>
        <p>
            <label>Phone (optional)</label><br>
            <input type="text" name="phone" style="width: 100%;">
        </p>
        <p>
            <button type="submit" class="btn">Save Faculty</button>
            <a href="index.php?page=admin" class="btn btn-secondary">Cancel</a>
        </p>
    </form>
</div>
