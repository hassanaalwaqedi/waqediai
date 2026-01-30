/// AI Message Bubble Widget
///
/// Renders AI response with MANDATORY citations.
/// WILL NOT render content without valid citations.

import 'package:flutter/material.dart';
import '../ai_message.dart';
import '../citation_data.dart';
import 'citation_block.dart';
import 'confidence_indicator.dart';

class AIMessageBubble extends StatelessWidget {
  final AIMessage message;
  final void Function(CitationData)? onCitationTap;

  const AIMessageBubble({
    super.key,
    required this.message,
    this.onCitationTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAvatar(),
          const SizedBox(width: 12),
          Expanded(child: _buildContent(context)),
          const SizedBox(width: 48),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF3B82F6), Color(0xFF8B5CF6)],
        ),
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Icon(Icons.auto_awesome, size: 18, color: Colors.white),
    );
  }

  Widget _buildContent(BuildContext context) {
    // CRITICAL: Check if message can be rendered
    if (!message.canRender) {
      return _buildRejectedState();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildHeader(),
        const SizedBox(height: 8),
        _buildMessageBody(),
        CitationBlock(
          citations: message.citations,
          onCitationTap: onCitationTap,
        ),
      ],
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        const Text(
          'WaqediAI',
          style: TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(width: 8),
        ConfidenceIndicator(confidence: message.confidence),
        const Spacer(),
        Text(
          _formatTime(message.timestamp),
          style: TextStyle(color: Colors.grey.shade500, fontSize: 11),
        ),
      ],
    );
  }

  Widget _buildMessageBody() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAnswerWithCitationMarkers(),
          if (message.isLowConfidence) ...[
            const SizedBox(height: 12),
            _buildLowConfidenceWarning(),
          ],
        ],
      ),
    );
  }

  Widget _buildAnswerWithCitationMarkers() {
    // Insert citation markers [1], [2], etc. into text
    String text = message.displayContent;
    
    return Text(
      text,
      style: const TextStyle(
        color: Colors.white,
        fontSize: 15,
        height: 1.6,
      ),
    );
  }

  Widget _buildLowConfidenceWarning() {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFFF59E0B).withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFF59E0B).withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.info_outline, size: 16, color: Color(0xFFF59E0B)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'This answer is based on limited context. Please verify with the cited sources.',
              style: TextStyle(
                color: Colors.amber.shade200,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRejectedState() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B).withOpacity(0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF64748B).withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(Icons.search_off, size: 20, color: Colors.grey.shade400),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'No Sources Found',
                  style: TextStyle(
                    color: Colors.grey.shade300,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  message.displayContent,
                  style: TextStyle(
                    color: Colors.grey.shade400,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}
