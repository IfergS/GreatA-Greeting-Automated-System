<?php
namespace GreetA;

class Attendance {
    public int $id;
    public string $facultyId;
    public string $facultyName;
    public string $date;
    public string $time;
    public string $status;

    public function __construct(array $row) {
        $r = array_change_key_case($row, CASE_LOWER);
        $this->id = (int) ($r['id'] ?? 0);
        $this->facultyId = (string) ($r['facultyid'] ?? '');
        $this->facultyName = (string) ($r['facultyname'] ?? '');
        $this->date = (string) ($r['date'] ?? '');
        $this->time = (string) ($r['time'] ?? '');
        $this->status = (string) ($r['status'] ?? 'present');
    }

    public static function mark(string $facultyId, string $facultyName): bool {
        $db = Database::getConnection();
        $stmt = $db->prepare('INSERT INTO attendance (facultyId, facultyName, date, time, status) VALUES (?, ?, CURDATE(), CURTIME(), ?) ON DUPLICATE KEY UPDATE time = CURTIME(), status = VALUES(status)');
        return $stmt->execute([$facultyId, $facultyName, 'present']);
    }

    /** Check if faculty already marked today */
    public static function alreadyMarkedToday(string $facultyId): bool {
        $db = Database::getConnection();
        $stmt = $db->prepare('SELECT 1 FROM attendance WHERE facultyId = ? AND date = CURDATE() LIMIT 1');
        $stmt->execute([$facultyId]);
        return (bool) $stmt->fetch();
    }

    public static function getForDate(string $date): array {
        $db = Database::getConnection();
        $stmt = $db->prepare('SELECT id, facultyId, facultyName, date, time, status FROM attendance WHERE date = ? ORDER BY time');
        $stmt->execute([$date]);
        $list = [];
        while ($row = $stmt->fetch()) {
            $list[] = new self($row);
        }
        return $list;
    }

    public static function getRecent(int $limit = 100): array {
        $db = Database::getConnection();
        $stmt = $db->query('SELECT id, facultyId, facultyName, date, time, status FROM attendance ORDER BY date DESC, time DESC LIMIT ' . (int) $limit);
        $list = [];
        while ($row = $stmt->fetch()) {
            $list[] = new self($row);
        }
        return $list;
    }

    public static function exportCsv(string $date): string {
        $rows = self::getForDate($date);
        $out = "Id,,Name,,Date,,Time\n";
        foreach ($rows as $a) {
            $out .= sprintf("'%s',,%s,,%s,,%s\n", $a->facultyId, $a->facultyName, $a->date, $a->time);
        }
        return $out;
    }
}
