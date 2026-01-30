/// Chat Stream Controller
///
/// Handles streaming responses with citation validation.

import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';

import 'ai_message.dart';
import 'citation_data.dart';
import '../core/ai/rag_client.dart';

// Safety states
enum ChatSafetyState {
  ready,
  loading,
  noSources,
  lowConfidence,
  unauthorized,
  error,
}

// Events
abstract class ChatStreamEvent extends Equatable {
  const ChatStreamEvent();
  @override
  List<Object?> get props => [];
}

class ChatStreamSendMessage extends ChatStreamEvent {
  final String content;
  const ChatStreamSendMessage(this.content);
  @override
  List<Object?> get props => [content];
}

class ChatStreamNewConversation extends ChatStreamEvent {}

class ChatStreamClear extends ChatStreamEvent {}

// State
class ChatStreamState extends Equatable {
  final List<ChatEntry> entries;
  final bool isStreaming;
  final ChatSafetyState safetyState;
  final String? conversationId;
  final String? errorMessage;

  const ChatStreamState({
    this.entries = const [],
    this.isStreaming = false,
    this.safetyState = ChatSafetyState.ready,
    this.conversationId,
    this.errorMessage,
  });

  ChatStreamState copyWith({
    List<ChatEntry>? entries,
    bool? isStreaming,
    ChatSafetyState? safetyState,
    String? conversationId,
    String? errorMessage,
  }) {
    return ChatStreamState(
      entries: entries ?? this.entries,
      isStreaming: isStreaming ?? this.isStreaming,
      safetyState: safetyState ?? this.safetyState,
      conversationId: conversationId ?? this.conversationId,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [entries, isStreaming, safetyState, conversationId];
}

// Chat entry (user or AI)
class ChatEntry extends Equatable {
  final String id;
  final bool isUser;
  final String userContent;
  final AIMessage? aiMessage;
  final DateTime timestamp;

  const ChatEntry({
    required this.id,
    required this.isUser,
    this.userContent = '',
    this.aiMessage,
    required this.timestamp,
  });

  factory ChatEntry.user(String content) {
    return ChatEntry(
      id: const Uuid().v4(),
      isUser: true,
      userContent: content,
      timestamp: DateTime.now(),
    );
  }

  factory ChatEntry.ai(AIMessage message) {
    return ChatEntry(
      id: message.id,
      isUser: false,
      aiMessage: message,
      timestamp: message.timestamp,
    );
  }

  @override
  List<Object?> get props => [id, isUser, userContent, aiMessage];
}

// Controller
class ChatStreamController extends Bloc<ChatStreamEvent, ChatStreamState> {
  final RAGClient _ragClient;
  final _uuid = const Uuid();

  ChatStreamController({required RAGClient ragClient})
      : _ragClient = ragClient,
        super(ChatStreamState(conversationId: const Uuid().v4())) {
    on<ChatStreamSendMessage>(_onSendMessage);
    on<ChatStreamNewConversation>(_onNewConversation);
    on<ChatStreamClear>(_onClear);
  }

  Future<void> _onSendMessage(
    ChatStreamSendMessage event,
    Emitter<ChatStreamState> emit,
  ) async {
    if (event.content.trim().isEmpty) return;

    // Add user entry
    final userEntry = ChatEntry.user(event.content);
    emit(state.copyWith(
      entries: [...state.entries, userEntry],
      isStreaming: true,
      safetyState: ChatSafetyState.loading,
      errorMessage: null,
    ));

    try {
      // Query RAG
      final response = await _ragClient.query(
        message: event.content,
        conversationId: state.conversationId,
      );

      // Parse response
      final aiMessage = AIMessage.fromJson({
        'answer': response.answer,
        'citations': response.citations.map((c) => {
          'document_id': c.chunkId.isNotEmpty ? c.documentId : '',
          'document_title': c.documentTitle ?? 'Document',
          'chunk_id': c.chunkId,
          'snippet': c.textExcerpt,
          'language': 'en',
        }).toList(),
        'confidence': response.confidence,
        'trace_id': response.traceId,
        'language': response.language,
      });

      // Determine safety state
      ChatSafetyState safetyState;
      if (!aiMessage.canRender) {
        safetyState = ChatSafetyState.noSources;
      } else if (aiMessage.isLowConfidence) {
        safetyState = ChatSafetyState.lowConfidence;
      } else {
        safetyState = ChatSafetyState.ready;
      }

      final aiEntry = ChatEntry.ai(aiMessage);
      emit(state.copyWith(
        entries: [...state.entries, aiEntry],
        isStreaming: false,
        safetyState: safetyState,
      ));
    } catch (e) {
      final errorMessage = AIMessage.error('Failed to process your request. Please try again.');
      emit(state.copyWith(
        entries: [...state.entries, ChatEntry.ai(errorMessage)],
        isStreaming: false,
        safetyState: ChatSafetyState.error,
        errorMessage: e.toString(),
      ));
    }
  }

  void _onNewConversation(
    ChatStreamNewConversation event,
    Emitter<ChatStreamState> emit,
  ) {
    emit(ChatStreamState(conversationId: _uuid.v4()));
  }

  void _onClear(ChatStreamClear event, Emitter<ChatStreamState> emit) {
    emit(state.copyWith(entries: []));
  }
}
