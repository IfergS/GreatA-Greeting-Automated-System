<?php
namespace GreetA;

class Faculty {
    public string $id;
    public string $name;
    public ?string $email;
    public ?string $phone;
    public ?string $registrationDate;

    public function __construct(array $row) {
        $r = array_change_key_case($row, CASE_LOWER);
        $this->id = (string) ($r['id'] ?? '');
        $this->name = (string) ($r['name'] ?? '');
        $this->email = isset($r['email']) && $r['email'] !== '' ? (string) $r['email'] : null;
        $this->phone = isset($r['phone']) && $r['phone'] !== '' ? (string) $r['phone'] : null;
        $this->registrationDate = $r['registrationdate'] ?? null;
    }

    public static function getAll(): array {
        $db = Database::getConnection();
        $stmt = $db->query('SELECT id, name, email, phone, registrationDate FROM faculty ORDER BY name');
        $list = [];
        while ($row = $stmt->fetch()) {
            $list[] = new self($row);
        }
        return $list;
    }

    public static function getById(string $id): ?self {
        $db = Database::getConnection();
        $stmt = $db->prepare('SELECT id, name, email, phone, registrationDate FROM faculty WHERE id = ?');
        $stmt->execute([$id]);
        $row = $stmt->fetch();
        return $row ? new self($row) : null;
    }

    public static function create(string $id, string $name, ?string $email = null, ?string $phone = null): bool {
        $db = Database::getConnection();
        $stmt = $db->prepare('INSERT INTO faculty (id, name, email, phone) VALUES (?, ?, ?, ?)');
        return $stmt->execute([trim($id), trim($name), $email ?: null, $phone ?: null]);
    }

    public static function update(string $id, string $name, ?string $email = null, ?string $phone = null): bool {
        $db = Database::getConnection();
        $stmt = $db->prepare('UPDATE faculty SET name = ?, email = ?, phone = ? WHERE id = ?');
        return $stmt->execute([trim($name), $email ?: null, $phone ?: null, $id]);
    }

    public static function delete(string $id): bool {
        $db = Database::getConnection();
        $stmt = $db->prepare('DELETE FROM faculty WHERE id = ?');
        return $stmt->execute([$id]);
    }

    public static function count(): int {
        $db = Database::getConnection();
        return (int) $db->query('SELECT COUNT(*) FROM faculty')->fetchColumn();
    }
}
