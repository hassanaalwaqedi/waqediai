/// Chat Repository
///
/// Handles RAG API communication.

import '../core/network/api_client.dart';

class ChatMessage {
  final String id;
  final String content;
  final bool isUser;
  final List<Citation> citations;
  final double confidence;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.content,
    required this.isUser,
    this.citations = const [],
    this.confidence = 0.0,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class Citation {
  final String chunkId;
  final String documentId;
  final String textExcerpt;

  Citation({
    required this.chunkId,
    required this.documentId,
    required this.textExcerpt,
  });

  factory Citation.fromJson(Map<String, dynamic> json) {
    return Citation(
      chunkId: json['chunk_id'] ?? '',
      documentId: json['document_id'] ?? '',
      textExcerpt: json['text_excerpt'] ?? '',
    );
  }
}

class ChatRepository {
  final RagApiClient _apiClient;

  ChatRepository({required RagApiClient apiClient}) : _apiClient = apiClient;

  Future<ChatMessage> sendMessage({
    required String message,
    String? conversationId,
    int topK = 5,
  }) async {
    final response = await _apiClient.post('/query', data: {
      'query': message,
      'top_k': topK,
      if (conversationId != null) 'conversation_id': conversationId,
    });

    final data = response.data;
    final citations = (data['citations'] as List? ?? [])
        .map((c) => Citation.fromJson(c as Map<String, dynamic>))
        .toList();

    return ChatMessage(
      id: data['trace_id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      content: data['answer'] ?? '',
      isUser: false,
      citations: citations,
      confidence: (data['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
