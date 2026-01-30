/// Authenticated API Client for Flutter
///
/// Features:
/// - Automatic token injection
/// - Token refresh on 401
/// - Tenant header injection

import 'package:dio/dio.dart';
import '../auth/auth_storage.dart';
import '../auth/jwt_utils.dart';

class AuthenticatedApiClient {
  final Dio _dio;
  final AuthStorage _storage;
  final String _authBaseUrl;

  bool _isRefreshing = false;
  final List<Function(String)> _pendingRequests = [];

  AuthenticatedApiClient({
    required String baseUrl,
    required AuthStorage storage,
    String? authBaseUrl,
  })  : _storage = storage,
        _authBaseUrl = authBaseUrl ?? 'http://localhost:8001',
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 120),
          headers: {
            'Content-Type': 'application/json',
          },
        )) {
    _setupInterceptors();
  }

  Dio get client => _dio;

  void _setupInterceptors() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: _onRequest,
      onError: _onError,
    ));
  }

  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Get and validate token
    String? token = await _storage.getAccessToken();

    if (token != null) {
      // Check if token needs refresh
      if (JwtUtils.isExpired(token, bufferSeconds: 60)) {
        token = await _refreshToken();
      }

      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }

    // Add tenant header
    final tenantId = await _storage.getTenantId();
    if (tenantId != null) {
      options.headers['X-Tenant-ID'] = tenantId;
    }

    handler.next(options);
  }

  Future<void> _onError(
    DioException error,
    ErrorInterceptorHandler handler,
  ) async {
    if (error.response?.statusCode == 401) {
      // Token expired - try refresh
      final newToken = await _refreshToken();

      if (newToken != null) {
        // Retry original request
        final opts = error.requestOptions;
        opts.headers['Authorization'] = 'Bearer $newToken';

        try {
          final response = await _dio.fetch(opts);
          return handler.resolve(response);
        } catch (e) {
          return handler.reject(error);
        }
      }
    }

    handler.next(error);
  }

  Future<String?> _refreshToken() async {
    if (_isRefreshing) {
      // Wait for ongoing refresh
      return Future<String?>((resolve) {
        _pendingRequests.add(resolve as Function(String));
      });
    }

    _isRefreshing = true;

    try {
      final response = await Dio().post(
        '$_authBaseUrl/auth/refresh',
        options: Options(
          headers: {'Content-Type': 'application/json'},
        ),
      );

      final newToken = response.data['access_token'] as String?;

      if (newToken != null) {
        await _storage.saveAccessToken(newToken);

        // Resolve pending requests
        for (final callback in _pendingRequests) {
          callback(newToken);
        }
        _pendingRequests.clear();

        return newToken;
      }
    } catch (e) {
      // Refresh failed - clear tokens
      await _storage.clearAll();
    } finally {
      _isRefreshing = false;
    }

    return null;
  }

  // Convenience methods

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) {
    return _dio.get<T>(path, queryParameters: queryParameters);
  }

  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
  }) {
    return _dio.post<T>(path, data: data);
  }

  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
  }) {
    return _dio.put<T>(path, data: data);
  }

  Future<Response<T>> delete<T>(String path) {
    return _dio.delete<T>(path);
  }
}

/// RAG API Client
class RagApiClient extends AuthenticatedApiClient {
  RagApiClient({
    required AuthStorage storage,
  }) : super(
          baseUrl: const String.fromEnvironment(
            'RAG_API_URL',
            defaultValue: 'http://localhost:8009',
          ),
          storage: storage,
        );
}
