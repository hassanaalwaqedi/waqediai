/// Chat Page
///
/// Main ChatGPT-style interface.

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'chat_controller.dart';
import 'message_model.dart';
import 'citation_model.dart';
import '../../shared/widgets/message_bubble.dart';
import '../../shared/widgets/chat_input.dart';
import '../../shared/widgets/conversation_sidebar.dart';
import '../../core/ai/rag_client.dart';
import '../../core/auth/auth_storage.dart';

class ChatPage extends StatelessWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => ChatController(
        ragClient: RAGClient(storage: AuthStorage()),
      )..add(ChatInitialized()),
      child: const _ChatPageContent(),
    );
  }
}

class _ChatPageContent extends StatelessWidget {
  const _ChatPageContent();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 768;

          return Row(
            children: [
              if (isWide) _buildSidebar(context),
              Expanded(child: _ChatArea()),
            ],
          );
        },
      ),
      drawer: LayoutBuilder(
        builder: (context, constraints) {
          if (constraints.maxWidth > 768) return const SizedBox.shrink();
          return Drawer(child: _buildSidebarContent(context));
        },
      ),
    );
  }

  Widget _buildSidebar(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        border: Border(right: BorderSide(color: Color(0xFF1E293B))),
      ),
      child: _buildSidebarContent(context),
    );
  }

  Widget _buildSidebarContent(BuildContext context) {
    return BlocBuilder<ChatController, ChatState>(
      builder: (context, state) {
        return ConversationSidebar(
          conversationIds: state.conversationIds,
          currentId: state.currentConversationId,
          onSelect: (id) {
            context.read<ChatController>().add(ChatConversationSelected(id));
          },
          onNewChat: () {
            context.read<ChatController>().add(ChatNewConversation());
          },
        );
      },
    );
  }
}

class _ChatArea extends StatelessWidget {
  final _scrollController = ScrollController();

  _ChatArea();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _AppBar(),
        Expanded(child: _MessageList(scrollController: _scrollController)),
        _InputArea(scrollController: _scrollController),
      ],
    );
  }
}

class _AppBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final isNarrow = MediaQuery.of(context).size.width <= 768;

    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: const BoxDecoration(
        color: Color(0xFF0F172A),
        border: Border(bottom: BorderSide(color: Color(0xFF1E293B))),
      ),
      child: Row(
        children: [
          if (isNarrow)
            IconButton(
              icon: const Icon(Icons.menu, color: Colors.white),
              onPressed: () => Scaffold.of(context).openDrawer(),
            ),
          if (isNarrow) const SizedBox(width: 8),
          const Text(
            'WaqediAI',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF10B981).withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: Color(0xFF10B981),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                const Text(
                  'Enterprise',
                  style: TextStyle(color: Color(0xFF10B981), fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MessageList extends StatelessWidget {
  final ScrollController scrollController;

  const _MessageList({required this.scrollController});

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<ChatController, ChatState>(
      listenWhen: (prev, curr) => prev.messages.length != curr.messages.length,
      listener: (context, state) {
        // Scroll to bottom on new message
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (scrollController.hasClients) {
            scrollController.animateTo(
              scrollController.position.maxScrollExtent,
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeOut,
            );
          }
        });
      },
      builder: (context, state) {
        if (state.messages.isEmpty) {
          return _EmptyState();
        }

        return ListView.builder(
          controller: scrollController,
          padding: const EdgeInsets.symmetric(vertical: 16),
          itemCount: state.messages.length + (state.isLoading ? 1 : 0),
          itemBuilder: (context, index) {
            if (index == state.messages.length && state.isLoading) {
              return _LoadingIndicator();
            }

            final message = state.messages[index];
            return MessageBubble(
              message: message,
              onCitationTap: (citation) => _showCitationDetail(context, citation),
            );
          },
        );
      },
    );
  }

  void _showCitationDetail(BuildContext context, Citation citation) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => _CitationDetailSheet(citation: citation),
    );
  }
}

class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.auto_awesome, size: 64, color: Colors.grey.shade600),
          const SizedBox(height: 16),
          Text(
            'WaqediAI',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Ask questions about your documents',
            style: TextStyle(color: Colors.grey.shade500, fontSize: 14),
          ),
        ],
      ),
    );
  }
}

class _LoadingIndicator extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Row(
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: Theme.of(context).colorScheme.secondary.withOpacity(0.3),
            child: const Icon(Icons.auto_awesome, size: 18, color: Colors.white),
          ),
          const SizedBox(width: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _DotIndicator(),
                const SizedBox(width: 4),
                _DotIndicator(delay: 150),
                const SizedBox(width: 4),
                _DotIndicator(delay: 300),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DotIndicator extends StatefulWidget {
  final int delay;

  const _DotIndicator({this.delay = 0});

  @override
  State<_DotIndicator> createState() => _DotIndicatorState();
}

class _DotIndicatorState extends State<_DotIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    Future.delayed(Duration(milliseconds: widget.delay), () {
      if (mounted) _controller.repeat(reverse: true);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: Colors.grey.shade400.withOpacity(0.4 + _controller.value * 0.6),
            shape: BoxShape.circle,
          ),
        );
      },
    );
  }
}

class _InputArea extends StatelessWidget {
  final ScrollController scrollController;

  const _InputArea({required this.scrollController});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ChatController, ChatState>(
      buildWhen: (prev, curr) => prev.isLoading != curr.isLoading,
      builder: (context, state) {
        return ChatInput(
          isLoading: state.isLoading,
          onSend: (text) {
            context.read<ChatController>().add(ChatMessageSent(text));
          },
          hintText: 'Ask about your documents...',
        );
      },
    );
  }
}

class _CitationDetailSheet extends StatelessWidget {
  final Citation citation;

  const _CitationDetailSheet({required this.citation});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.article, color: Colors.white),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  citation.label,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close, color: Colors.grey),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(color: Color(0xFF334155)),
          const SizedBox(height: 16),
          Text(
            'Source Excerpt',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              citation.textExcerpt,
              style: const TextStyle(color: Colors.white, height: 1.5),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Text(
                  'Document ID: ${citation.documentId}',
                  style: TextStyle(color: Colors.grey.shade500, fontSize: 11),
                ),
              ),
              if (citation.pageNumber != null)
                Text(
                  'Page ${citation.pageNumber}',
                  style: TextStyle(color: Colors.grey.shade500, fontSize: 11),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
