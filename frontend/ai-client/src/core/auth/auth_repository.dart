/// Auth Repository
///
/// Handles authentication lifecycle: login, refresh, logout.

import 'package:dio/dio.dart';
import '../network/api_client.dart';
import 'auth_storage.dart';
import 'jwt_utils.dart';

class AuthException implements Exception {
  final String message;
  final int? statusCode;

  AuthException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

class User {
  final String id;
  final String email;
  final String tenantId;
  final List<String> roles;
  final List<String> permissions;

  User({
    required this.id,
    required this.email,
    required this.tenantId,
    required this.roles,
    required this.permissions,
  });

  bool hasRole(String role) => roles.contains(role);
  bool hasPermission(String permission) => permissions.contains(permission);
}

class AuthRepository {
  final Dio _httpClient;
  final AuthStorage _storage;
  final String _baseUrl;

  User? _currentUser;
  bool _isRefreshing = false;

  AuthRepository({
    required AuthStorage storage,
    String? baseUrl,
  })  : _storage = storage,
        _baseUrl = baseUrl ?? 'http://localhost:8001',
        _httpClient = Dio(BaseOptions(
          baseUrl: baseUrl ?? 'http://localhost:8001',
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 30),
        ));

  User? get currentUser => _currentUser;
  bool get isAuthenticated => _currentUser != null;

  /// Login with credentials
  Future<User> login({
    required String email,
    required String password,
    String? tenantSlug,
  }) async {
    try {
      final response = await _httpClient.post(
        '/auth/login',
        data: {
          'email': email,
          'password': password,
          if (tenantSlug != null) 'tenant_slug': tenantSlug,
        },
      );

      final accessToken = response.data['access_token'] as String;

      // Store tokens
      await _storage.saveAccessToken(accessToken);

      // Parse user from token
      final payload = JwtUtils.decode(accessToken);
      if (payload == null) {
        throw AuthException('Invalid token received');
      }

      await _storage.saveTenantId(payload.tenantId);
      await _storage.saveUserId(payload.sub);

      _currentUser = User(
        id: payload.sub,
        email: payload.email,
        tenantId: payload.tenantId,
        roles: payload.roles,
        permissions: payload.permissions,
      );

      return _currentUser!;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw AuthException('Invalid credentials', statusCode: 401);
      }
      throw AuthException('Login failed: ${e.message}');
    }
  }

  /// Refresh access token
  Future<bool> refresh() async {
    if (_isRefreshing) return false;
    _isRefreshing = true;

    try {
      final response = await _httpClient.post('/auth/refresh');
      final accessToken = response.data['access_token'] as String;

      await _storage.saveAccessToken(accessToken);

      final payload = JwtUtils.decode(accessToken);
      if (payload != null) {
        _currentUser = User(
          id: payload.sub,
          email: payload.email,
          tenantId: payload.tenantId,
          roles: payload.roles,
          permissions: payload.permissions,
        );
      }

      return true;
    } catch (e) {
      await logout();
      return false;
    } finally {
      _isRefreshing = false;
    }
  }

  /// Logout and clear tokens
  Future<void> logout() async {
    try {
      final token = await _storage.getAccessToken();
      if (token != null) {
        await _httpClient.post(
          '/auth/logout',
          options: Options(headers: {'Authorization': 'Bearer $token'}),
        );
      }
    } catch (_) {
      // Ignore logout errors
    } finally {
      await _storage.clearAll();
      _currentUser = null;
    }
  }

  /// Check if token needs refresh
  Future<bool> checkAndRefreshIfNeeded() async {
    final token = await _storage.getAccessToken();
    if (token == null) return false;

    if (JwtUtils.isExpired(token, bufferSeconds: 60)) {
      return await refresh();
    }

    return true;
  }

  /// Restore session from storage
  Future<User?> restoreSession() async {
    final token = await _storage.getAccessToken();
    if (token == null) return null;

    if (JwtUtils.isExpired(token)) {
      final refreshed = await refresh();
      if (!refreshed) return null;
    }

    final payload = JwtUtils.decode(token);
    if (payload == null) return null;

    _currentUser = User(
      id: payload.sub,
      email: payload.email,
      tenantId: payload.tenantId,
      roles: payload.roles,
      permissions: payload.permissions,
    );

    return _currentUser;
  }
}
