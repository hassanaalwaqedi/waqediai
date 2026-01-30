/// RAG Client
///
/// Handles communication with RAG service.

import 'package:dio/dio.dart';
import '../auth/auth_storage.dart';
import '../auth/jwt_utils.dart';
import '../../features/chat/citation_model.dart';

class RAGResponse {
  final String answer;
  final List<Citation> citations;
  final double confidence;
  final String answerType;
  final String language;
  final String? traceId;
  final int? latencyMs;

  RAGResponse({
    required this.answer,
    required this.citations,
    required this.confidence,
    required this.answerType,
    required this.language,
    this.traceId,
    this.latencyMs,
  });

  factory RAGResponse.fromJson(Map<String, dynamic> json) {
    return RAGResponse(
      answer: json['answer'] ?? '',
      citations: (json['citations'] as List? ?? [])
          .map((c) => Citation.fromJson(c as Map<String, dynamic>))
          .toList(),
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      answerType: json['answer_type'] ?? 'direct',
      language: json['language'] ?? 'en',
      traceId: json['trace_id'],
      latencyMs: json['latency_ms'],
    );
  }

  bool get hasCitations => citations.isNotEmpty;
}

class RAGClient {
  final Dio _dio;
  final AuthStorage _storage;
  final String _baseUrl;

  RAGClient({
    required AuthStorage storage,
    String? baseUrl,
  })  : _storage = storage,
        _baseUrl = baseUrl ?? 'http://localhost:8009',
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl ?? 'http://localhost:8009',
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 120),
          headers: {'Content-Type': 'application/json'},
        )) {
    _dio.interceptors.add(_AuthInterceptor(_storage));
  }

  /// Send a query to RAG service
  Future<RAGResponse> query({
    required String message,
    String? conversationId,
    int topK = 5,
    Map<String, String>? filters,
  }) async {
    final tenantId = await _storage.getTenantId();
    if (tenantId == null) {
      throw RAGException('No tenant context');
    }

    try {
      final response = await _dio.post('/query', data: {
        'tenant_id': tenantId,
        'query': message,
        'top_k': topK,
        if (conversationId != null) 'conversation_id': conversationId,
        if (filters != null) 'filters': filters,
      });

      return RAGResponse.fromJson(response.data);
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw RAGException('Authentication required');
      }
      if (e.response?.statusCode == 403) {
        throw RAGException('Insufficient permissions');
      }
      throw RAGException('Query failed: ${e.message}');
    }
  }

  /// Health check
  Future<bool> isHealthy() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}

class _AuthInterceptor extends Interceptor {
  final AuthStorage _storage;

  _AuthInterceptor(this._storage);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _storage.getAccessToken();
    final tenantId = await _storage.getTenantId();

    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    if (tenantId != null) {
      options.headers['X-Tenant-ID'] = tenantId;
    }

    handler.next(options);
  }
}

class RAGException implements Exception {
  final String message;
  RAGException(this.message);

  @override
  String toString() => message;
}
