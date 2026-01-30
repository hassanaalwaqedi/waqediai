/// AI Message
///
/// Represents an AI response with MANDATORY citations.

import 'package:equatable/equatable.dart';
import 'citation_data.dart';

enum AIMessageState {
  streaming,    // Text arriving
  pending,      // Waiting for citations
  validated,    // Citations verified
  rejected,     // No citations - blocked
  error,        // Request failed
}

class AIMessage extends Equatable {
  final String id;
  final String queryId;
  final String content;
  final List<CitationData> citations;
  final double confidence;
  final String language;
  final AIMessageState state;
  final DateTime timestamp;
  final String? errorMessage;

  const AIMessage({
    required this.id,
    required this.queryId,
    required this.content,
    required this.citations,
    required this.confidence,
    this.language = 'en',
    this.state = AIMessageState.pending,
    required this.timestamp,
    this.errorMessage,
  });

  factory AIMessage.fromJson(Map<String, dynamic> json) {
    final citations = (json['citations'] as List? ?? [])
        .map((c) => CitationData.fromJson(c as Map<String, dynamic>))
        .where((c) => c.isValid)
        .toList();

    final confidence = (json['confidence'] as num?)?.toDouble() ?? 0.0;
    final hasValidCitations = citations.isNotEmpty;

    return AIMessage(
      id: json['trace_id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      queryId: json['metadata']?['query_id'] ?? '',
      content: json['answer'] ?? '',
      citations: citations,
      confidence: confidence,
      language: json['language'] ?? 'en',
      state: hasValidCitations ? AIMessageState.validated : AIMessageState.rejected,
      timestamp: DateTime.now(),
    );
  }

  /// CRITICAL: Message can only be rendered if validated
  bool get canRender => state == AIMessageState.validated && citations.isNotEmpty;

  /// Check if low confidence
  bool get isLowConfidence => confidence > 0 && confidence < 0.5;

  /// Get safe content or refusal message
  String get displayContent {
    if (state == AIMessageState.rejected || citations.isEmpty) {
      return _getRefusalMessage();
    }
    if (state == AIMessageState.streaming) {
      return content;
    }
    return content;
  }

  String _getRefusalMessage() {
    return 'No relevant documents found to answer this question. '
           'Please try rephrasing or contact your administrator.';
  }

  /// Create a streaming message (not yet validated)
  factory AIMessage.streaming(String partialContent) {
    return AIMessage(
      id: 'stream_${DateTime.now().millisecondsSinceEpoch}',
      queryId: '',
      content: partialContent,
      citations: const [],
      confidence: 0.0,
      state: AIMessageState.streaming,
      timestamp: DateTime.now(),
    );
  }

  /// Create error message
  factory AIMessage.error(String message) {
    return AIMessage(
      id: 'error_${DateTime.now().millisecondsSinceEpoch}',
      queryId: '',
      content: message,
      citations: const [],
      confidence: 0.0,
      state: AIMessageState.error,
      timestamp: DateTime.now(),
      errorMessage: message,
    );
  }

  AIMessage copyWith({
    String? content,
    List<CitationData>? citations,
    double? confidence,
    AIMessageState? state,
    String? errorMessage,
  }) {
    return AIMessage(
      id: id,
      queryId: queryId,
      content: content ?? this.content,
      citations: citations ?? this.citations,
      confidence: confidence ?? this.confidence,
      language: language,
      state: state ?? this.state,
      timestamp: timestamp,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  @override
  List<Object?> get props => [id, content, citations, state];
}
