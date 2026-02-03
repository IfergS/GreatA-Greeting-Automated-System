class Admin {
  final int? id;
  final String username;
  final String password;
  final String? email;
  final String? fullName;
  final DateTime? createdAt;
  final DateTime? lastLogin;
  final bool isActive;

  Admin({
    this.id,
    required this.username,
    required this.password,
    this.email,
    this.fullName,
    this.createdAt,
    this.lastLogin,
    this.isActive = true,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'password': password,
      'email': email,
      'fullName': fullName,
      'createdAt': createdAt?.toIso8601String(),
      'lastLogin': lastLogin?.toIso8601String(),
      'isActive': isActive ? 1 : 0,
    };
  }

  factory Admin.fromJson(Map<String, dynamic> json) {
    return Admin(
      id: json['id'] as int?,
      username: json['username'] as String,
      password: json['password'] as String,
      email: json['email'] as String?,
      fullName: json['fullName'] as String?,
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'] as String)
          : null,
      lastLogin: json['lastLogin'] != null
          ? DateTime.parse(json['lastLogin'] as String)
          : null,
      isActive: (json['isActive'] as int? ?? 1) == 1,
    );
  }

  Admin copyWith({
    int? id,
    String? username,
    String? password,
    String? email,
    String? fullName,
    DateTime? createdAt,
    DateTime? lastLogin,
    bool? isActive,
  }) {
    return Admin(
      id: id ?? this.id,
      username: username ?? this.username,
      password: password ?? this.password,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      createdAt: createdAt ?? this.createdAt,
      lastLogin: lastLogin ?? this.lastLogin,
      isActive: isActive ?? this.isActive,
    );
  }
}

