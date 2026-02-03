<div class="card">
    <p><strong>📅 Date:</strong> <?= date('d F Y') ?></p>
    <p><strong>🕐 Time:</strong> <span id="clock"><?= date('H:i:s') ?></span></p>
</div>
<div class="card">
    <p><strong>📊 Total Faculty:</strong> <?= (int) $facultyCount ?></p>
</div>
<div style="display: flex; gap: 1rem; flex-wrap: wrap;">
    <a href="index.php?page=attendance" class="btn">▶ Take Attendance</a>
    <a href="index.php?page=admin" class="btn btn-secondary">⚙️ Admin Panel</a>
</div>
<script>
(function(){
    function pad(n){ return n < 10 ? '0'+n : n; }
    function tick(){
        var d = new Date();
        document.getElementById('clock').textContent = pad(d.getHours())+':'+pad(d.getMinutes())+':'+pad(d.getSeconds());
    }
    setInterval(tick, 1000);
})();
</script>
