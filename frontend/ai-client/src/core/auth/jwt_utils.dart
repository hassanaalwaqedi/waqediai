/// JWT Utilities for Flutter
///
/// Handles JWT parsing and expiry checking.

import 'dart:convert';

class JwtPayload {
  final String sub;
  final String email;
  final String tenantId;
  final List<String> roles;
  final List<String> permissions;
  final int exp;
  final int iat;

  JwtPayload({
    required this.sub,
    required this.email,
    required this.tenantId,
    required this.roles,
    required this.permissions,
    required this.exp,
    required this.iat,
  });

  factory JwtPayload.fromJson(Map<String, dynamic> json) {
    return JwtPayload(
      sub: json['sub'] ?? '',
      email: json['email'] ?? '',
      tenantId: json['tenant_id'] ?? '',
      roles: List<String>.from(json['roles'] ?? []),
      permissions: List<String>.from(json['permissions'] ?? []),
      exp: json['exp'] ?? 0,
      iat: json['iat'] ?? 0,
    );
  }

  bool get isExpired {
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    return exp <= now;
  }

  bool isExpiringIn(int seconds) {
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    return exp <= now + seconds;
  }

  int get timeRemaining {
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    return exp > now ? exp - now : 0;
  }
}

class JwtUtils {
  /// Decode JWT payload without verification
  static JwtPayload? decode(String token) {
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;

      // Decode base64url
      String payload = parts[1];
      // Add padding if needed
      while (payload.length % 4 != 0) {
        payload += '=';
      }
      payload = payload.replaceAll('-', '+').replaceAll('_', '/');

      final decoded = utf8.decode(base64.decode(payload));
      final json = jsonDecode(decoded) as Map<String, dynamic>;

      return JwtPayload.fromJson(json);
    } catch (e) {
      return null;
    }
  }

  /// Check if token is expired
  static bool isExpired(String token, {int bufferSeconds = 30}) {
    final payload = decode(token);
    if (payload == null) return true;
    return payload.isExpiringIn(bufferSeconds);
  }

  /// Get tenant ID from token
  static String? getTenantId(String token) {
    final payload = decode(token);
    return payload?.tenantId;
  }

  /// Get user ID from token
  static String? getUserId(String token) {
    final payload = decode(token);
    return payload?.sub;
  }
}
