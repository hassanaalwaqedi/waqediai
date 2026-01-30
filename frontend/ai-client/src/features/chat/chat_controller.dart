/// Chat Controller
///
/// Manages chat state with policy enforcement.

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';

import 'message_model.dart';
import 'citation_model.dart';
import '../../core/ai/rag_client.dart';
import '../../core/ai/chat_policy.dart';

// Events
abstract class ChatEvent extends Equatable {
  const ChatEvent();

  @override
  List<Object?> get props => [];
}

class ChatInitialized extends ChatEvent {}

class ChatMessageSent extends ChatEvent {
  final String content;

  const ChatMessageSent(this.content);

  @override
  List<Object?> get props => [content];
}

class ChatNewConversation extends ChatEvent {}

class ChatConversationSelected extends ChatEvent {
  final String conversationId;

  const ChatConversationSelected(this.conversationId);

  @override
  List<Object?> get props => [conversationId];
}

class ChatCleared extends ChatEvent {}

// State
class ChatState extends Equatable {
  final List<Message> messages;
  final bool isLoading;
  final String? currentConversationId;
  final List<String> conversationIds;
  final String? error;
  final PolicyResult? lastPolicyResult;

  const ChatState({
    this.messages = const [],
    this.isLoading = false,
    this.currentConversationId,
    this.conversationIds = const [],
    this.error,
    this.lastPolicyResult,
  });

  ChatState copyWith({
    List<Message>? messages,
    bool? isLoading,
    String? currentConversationId,
    List<String>? conversationIds,
    String? error,
    PolicyResult? lastPolicyResult,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      currentConversationId: currentConversationId ?? this.currentConversationId,
      conversationIds: conversationIds ?? this.conversationIds,
      error: error,
      lastPolicyResult: lastPolicyResult,
    );
  }

  @override
  List<Object?> get props => [messages, isLoading, currentConversationId, error];
}

// BLoC
class ChatController extends Bloc<ChatEvent, ChatState> {
  final RAGClient _ragClient;
  final _uuid = const Uuid();

  ChatController({required RAGClient ragClient})
      : _ragClient = ragClient,
        super(const ChatState()) {
    on<ChatInitialized>(_onInitialized);
    on<ChatMessageSent>(_onMessageSent);
    on<ChatNewConversation>(_onNewConversation);
    on<ChatConversationSelected>(_onConversationSelected);
    on<ChatCleared>(_onCleared);
  }

  void _onInitialized(ChatInitialized event, Emitter<ChatState> emit) {
    final conversationId = _uuid.v4();
    emit(state.copyWith(
      currentConversationId: conversationId,
      conversationIds: [conversationId],
      messages: [Message.system(ChatPolicy.welcomeMessage)],
    ));
  }

  Future<void> _onMessageSent(ChatMessageSent event, Emitter<ChatState> emit) async {
    if (event.content.trim().isEmpty) return;

    // Add user message
    final userMessage = Message.user(event.content);
    emit(state.copyWith(
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null,
    ));

    try {
      // Query RAG service
      final response = await _ragClient.query(
        message: event.content,
        conversationId: state.currentConversationId,
      );

      // Apply policy validation
      final policyResult = ChatPolicy.validateResponse(
        answer: response.answer,
        citations: response.citations,
        confidence: response.confidence,
      );

      if (policyResult.isBlocked) {
        // Policy blocked - show refusal
        final refusalMessage = Message.system(
          policyResult.userMessage ?? ChatPolicy.noResultsMessage,
        );
        emit(state.copyWith(
          messages: [...state.messages, refusalMessage],
          isLoading: false,
          lastPolicyResult: policyResult,
        ));
        return;
      }

      // Build assistant message
      final assistantMessage = Message.assistant(
        id: response.traceId ?? _uuid.v4(),
        content: response.answer,
        citations: response.citations,
        confidence: response.confidence,
        language: response.language,
      );

      final newMessages = [...state.messages, assistantMessage];

      // Add warning if low confidence
      if (policyResult.hasWarning) {
        newMessages.add(Message.system(ChatPolicy.lowConfidenceDisclaimer));
      }

      emit(state.copyWith(
        messages: newMessages,
        isLoading: false,
        lastPolicyResult: policyResult,
      ));
    } catch (e) {
      emit(state.copyWith(
        isLoading: false,
        error: e.toString(),
        messages: [
          ...state.messages,
          Message.system('An error occurred. Please try again.'),
        ],
      ));
    }
  }

  void _onNewConversation(ChatNewConversation event, Emitter<ChatState> emit) {
    final conversationId = _uuid.v4();
    emit(ChatState(
      currentConversationId: conversationId,
      conversationIds: [...state.conversationIds, conversationId],
      messages: [Message.system(ChatPolicy.welcomeMessage)],
    ));
  }

  void _onConversationSelected(ChatConversationSelected event, Emitter<ChatState> emit) {
    // In a real app, load messages from storage
    emit(state.copyWith(currentConversationId: event.conversationId));
  }

  void _onCleared(ChatCleared event, Emitter<ChatState> emit) {
    emit(state.copyWith(messages: []));
  }
}
