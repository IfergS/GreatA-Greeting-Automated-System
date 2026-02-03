class Faculty {
  final String id;
  final String name;
  final String? email;
  final String? phone;
  final DateTime? registrationDate;

  Faculty({
    required this.id,
    required this.name,
    this.email,
    this.phone,
    this.registrationDate,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email ?? '',
      'phone': phone ?? '',
      'registrationDate': registrationDate?.toIso8601String() ?? '',
    };
  }

  factory Faculty.fromJson(Map<String, dynamic> json) {
    return Faculty(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'],
      phone: json['phone'],
      registrationDate: json['registrationDate'] != null && json['registrationDate'].toString().isNotEmpty
          ? DateTime.parse(json['registrationDate'])
          : null,
    );
  }

  Faculty copyWith({
    String? id,
    String? name,
    String? email,
    String? phone,
    DateTime? registrationDate,
  }) {
    return Faculty(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      registrationDate: registrationDate ?? this.registrationDate,
    );
  }
}

