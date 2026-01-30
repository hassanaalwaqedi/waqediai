/// Chat Message Bubble Widget
///
/// Renders messages with citations.

import 'package:flutter/material.dart';
import '../message_model.dart';
import '../citation_model.dart';

class MessageBubble extends StatelessWidget {
  final Message message;
  final void Function(Citation)? onCitationTap;

  const MessageBubble({
    super.key,
    required this.message,
    this.onCitationTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: _buildContent(context),
    );
  }

  Widget _buildContent(BuildContext context) {
    switch (message.role) {
      case MessageRole.user:
        return _UserBubble(message: message);
      case MessageRole.assistant:
        return _AssistantBubble(
          message: message,
          onCitationTap: onCitationTap,
        );
      case MessageRole.system:
        return _SystemBubble(message: message);
    }
  }
}

class _UserBubble extends StatelessWidget {
  final Message message;

  const _UserBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(width: 48),
        Flexible(
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              message.content,
              style: const TextStyle(color: Colors.white, fontSize: 15),
            ),
          ),
        ),
        const SizedBox(width: 8),
        CircleAvatar(
          radius: 16,
          backgroundColor: Theme.of(context).colorScheme.primary.withOpacity(0.3),
          child: const Icon(Icons.person, size: 18, color: Colors.white),
        ),
      ],
    );
  }
}

class _AssistantBubble extends StatelessWidget {
  final Message message;
  final void Function(Citation)? onCitationTap;

  const _AssistantBubble({
    required this.message,
    this.onCitationTap,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 16,
          backgroundColor: Theme.of(context).colorScheme.secondary.withOpacity(0.3),
          child: const Icon(Icons.auto_awesome, size: 18, color: Colors.white),
        ),
        const SizedBox(width: 8),
        Flexible(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      message.content,
                      style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.5),
                    ),
                    if (message.citations.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      const Divider(color: Color(0xFF334155)),
                      const SizedBox(height: 8),
                      _CitationsList(
                        citations: message.citations,
                        onTap: onCitationTap,
                      ),
                    ],
                  ],
                ),
              ),
              if (message.isLowConfidence)
                Padding(
                  padding: const EdgeInsets.only(top: 4, left: 8),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, size: 14, color: Colors.amber.shade400),
                      const SizedBox(width: 4),
                      Text(
                        'Limited context',
                        style: TextStyle(fontSize: 12, color: Colors.amber.shade400),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(width: 48),
      ],
    );
  }
}

class _SystemBubble extends StatelessWidget {
  final Message message;

  const _SystemBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B).withOpacity(0.5),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          message.content,
          style: TextStyle(color: Colors.grey.shade400, fontSize: 13),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}

class _CitationsList extends StatelessWidget {
  final List<Citation> citations;
  final void Function(Citation)? onTap;

  const _CitationsList({
    required this.citations,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.article_outlined, size: 14, color: Colors.grey.shade400),
            const SizedBox(width: 4),
            Text(
              'Sources',
              style: TextStyle(fontSize: 12, color: Colors.grey.shade400, fontWeight: FontWeight.w500),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: citations.asMap().entries.map((entry) {
            final index = entry.key + 1;
            final citation = entry.value;
            return _CitationChip(
              index: index,
              citation: citation,
              onTap: () => onTap?.call(citation),
            );
          }).toList(),
        ),
      ],
    );
  }
}

class _CitationChip extends StatelessWidget {
  final int index;
  final Citation citation;
  final VoidCallback? onTap;

  const _CitationChip({
    required this.index,
    required this.citation,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.primary.withOpacity(0.15),
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: Theme.of(context).colorScheme.primary.withOpacity(0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '[$index]',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              citation.label,
              style: TextStyle(fontSize: 11, color: Colors.grey.shade300),
            ),
          ],
        ),
      ),
    );
  }
}
