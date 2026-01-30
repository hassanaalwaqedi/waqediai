/// Conversation Sidebar
///
/// Shows conversation history.

import 'package:flutter/material.dart';

class ConversationSidebar extends StatelessWidget {
  final List<String> conversationIds;
  final String? currentId;
  final void Function(String) onSelect;
  final VoidCallback onNewChat;

  const ConversationSidebar({
    super.key,
    required this.conversationIds,
    required this.currentId,
    required this.onSelect,
    required this.onNewChat,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 260,
      color: const Color(0xFF0F172A),
      child: Column(
        children: [
          _Header(onNewChat: onNewChat),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              itemCount: conversationIds.length,
              itemBuilder: (context, index) {
                final id = conversationIds[index];
                final isSelected = id == currentId;
                return _ConversationTile(
                  id: id,
                  index: conversationIds.length - index,
                  isSelected: isSelected,
                  onTap: () => onSelect(id),
                );
              },
            ),
          ),
          _Footer(),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final VoidCallback onNewChat;

  const _Header({required this.onNewChat});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(Icons.auto_awesome, color: Colors.white, size: 24),
              const SizedBox(width: 8),
              const Text(
                'WaqediAI',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: onNewChat,
              icon: const Icon(Icons.add, size: 18),
              label: const Text('New Chat'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.white,
                side: const BorderSide(color: Color(0xFF334155)),
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ConversationTile extends StatelessWidget {
  final String id;
  final int index;
  final bool isSelected;
  final VoidCallback onTap;

  const _ConversationTile({
    required this.id,
    required this.index,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 2),
      decoration: BoxDecoration(
        color: isSelected ? const Color(0xFF1E293B) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
      ),
      child: ListTile(
        dense: true,
        leading: Icon(
          Icons.chat_bubble_outline,
          size: 18,
          color: isSelected ? Colors.white : Colors.grey.shade500,
        ),
        title: Text(
          'Conversation $index',
          style: TextStyle(
            color: isSelected ? Colors.white : Colors.grey.shade300,
            fontSize: 14,
          ),
        ),
        onTap: onTap,
      ),
    );
  }
}

class _Footer extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Color(0xFF1E293B))),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: const Color(0xFF334155),
            child: Icon(Icons.person, size: 18, color: Colors.grey.shade400),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Enterprise User',
              style: TextStyle(color: Colors.grey.shade300, fontSize: 13),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
