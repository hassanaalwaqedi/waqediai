/// Message Model
///
/// Represents a chat message with citations.

import 'package:equatable/equatable.dart';
import 'citation_model.dart';

enum MessageRole { user, assistant, system }

enum MessageStatus { sending, sent, error }

class Message extends Equatable {
  final String id;
  final String content;
  final MessageRole role;
  final MessageStatus status;
  final List<Citation> citations;
  final double confidence;
  final String language;
  final DateTime timestamp;
  final String? error;

  const Message({
    required this.id,
    required this.content,
    required this.role,
    this.status = MessageStatus.sent,
    this.citations = const [],
    this.confidence = 0.0,
    this.language = 'en',
    DateTime? timestamp,
    this.error,
  }) : timestamp = timestamp ?? const _DefaultTimestamp();

  /// User message factory
  factory Message.user(String content) {
    return Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      role: MessageRole.user,
      status: MessageStatus.sent,
      timestamp: DateTime.now(),
    );
  }

  /// Assistant message factory
  factory Message.assistant({
    required String id,
    required String content,
    required List<Citation> citations,
    required double confidence,
    String language = 'en',
  }) {
    return Message(
      id: id,
      content: content,
      role: MessageRole.assistant,
      status: MessageStatus.sent,
      citations: citations,
      confidence: confidence,
      language: language,
      timestamp: DateTime.now(),
    );
  }

  /// System message factory
  factory Message.system(String content) {
    return Message(
      id: 'sys_${DateTime.now().millisecondsSinceEpoch}',
      content: content,
      role: MessageRole.system,
      status: MessageStatus.sent,
      timestamp: DateTime.now(),
    );
  }

  /// Policy checks
  bool get hasCitations => citations.isNotEmpty;
  bool get isLowConfidence => confidence > 0 && confidence < 0.5;
  bool get isValid => role == MessageRole.user || (role == MessageRole.assistant && hasCitations);

  Message copyWith({
    String? content,
    MessageStatus? status,
    List<Citation>? citations,
    double? confidence,
    String? error,
  }) {
    return Message(
      id: id,
      content: content ?? this.content,
      role: role,
      status: status ?? this.status,
      citations: citations ?? this.citations,
      confidence: confidence ?? this.confidence,
      language: language,
      timestamp: timestamp,
      error: error ?? this.error,
    );
  }

  @override
  List<Object?> get props => [id, content, role, status, citations, confidence];
}

class _DefaultTimestamp implements DateTime {
  const _DefaultTimestamp();
  
  @override
  dynamic noSuchMethod(Invocation invocation) => DateTime.now();
}
