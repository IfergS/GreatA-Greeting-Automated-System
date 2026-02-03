class Attendance {
  final String id;
  final String facultyId;
  final String facultyName;
  final DateTime date;
  final DateTime time;
  final String? status; // 'present', 'late', etc.

  Attendance({
    required this.id,
    required this.facultyId,
    required this.facultyName,
    required this.date,
    required this.time,
    this.status,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'facultyId': facultyId,
      'facultyName': facultyName,
      'date': date.toIso8601String(),
      'time': time.toIso8601String(),
      'status': status ?? 'present',
    };
  }

  factory Attendance.fromJson(Map<String, dynamic> json) {
    return Attendance(
      id: json['id'] ?? '',
      facultyId: json['facultyId'] ?? '',
      facultyName: json['facultyName'] ?? '',
      date: DateTime.parse(json['date']),
      time: DateTime.parse(json['time']),
      status: json['status'],
    );
  }

  bool isSameDay(DateTime other) {
    return date.year == other.year &&
        date.month == other.month &&
        date.day == other.day;
  }
}

