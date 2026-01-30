/// Chat BLoC
///
/// Manages chat state and AI interactions.

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';
import 'chat_repository.dart';

// Events
abstract class ChatEvent extends Equatable {
  const ChatEvent();

  @override
  List<Object?> get props => [];
}

class ChatMessageSent extends ChatEvent {
  final String message;

  const ChatMessageSent(this.message);

  @override
  List<Object?> get props => [message];
}

class ChatCleared extends ChatEvent {}

class ChatNewConversation extends ChatEvent {}

// States
class ChatState extends Equatable {
  final List<ChatMessage> messages;
  final bool isLoading;
  final String? error;
  final String? conversationId;

  const ChatState({
    this.messages = const [],
    this.isLoading = false,
    this.error,
    this.conversationId,
  });

  ChatState copyWith({
    List<ChatMessage>? messages,
    bool? isLoading,
    String? error,
    String? conversationId,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      conversationId: conversationId ?? this.conversationId,
    );
  }

  @override
  List<Object?> get props => [messages, isLoading, error, conversationId];
}

// BLoC
class ChatBloc extends Bloc<ChatEvent, ChatState> {
  final ChatRepository _chatRepository;
  final _uuid = const Uuid();

  ChatBloc({required ChatRepository chatRepository})
      : _chatRepository = chatRepository,
        super(ChatState(conversationId: const Uuid().v4())) {
    on<ChatMessageSent>(_onMessageSent);
    on<ChatCleared>(_onCleared);
    on<ChatNewConversation>(_onNewConversation);
  }

  Future<void> _onMessageSent(
    ChatMessageSent event,
    Emitter<ChatState> emit,
  ) async {
    // Add user message
    final userMessage = ChatMessage(
      id: _uuid.v4(),
      content: event.message,
      isUser: true,
    );

    emit(state.copyWith(
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null,
    ));

    try {
      // Get AI response
      final response = await _chatRepository.sendMessage(
        message: event.message,
        conversationId: state.conversationId,
      );

      emit(state.copyWith(
        messages: [...state.messages, response],
        isLoading: false,
      ));
    } catch (e) {
      emit(state.copyWith(
        isLoading: false,
        error: 'Failed to get response: $e',
      ));
    }
  }

  void _onCleared(ChatCleared event, Emitter<ChatState> emit) {
    emit(ChatState(conversationId: state.conversationId));
  }

  void _onNewConversation(ChatNewConversation event, Emitter<ChatState> emit) {
    emit(ChatState(conversationId: _uuid.v4()));
  }
}
