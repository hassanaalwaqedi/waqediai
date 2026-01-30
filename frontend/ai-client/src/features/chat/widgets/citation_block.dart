/// Citation Block Widget
///
/// Renders all citations for an AI message.

import 'package:flutter/material.dart';
import '../citation_data.dart';
import 'citation_card.dart';

class CitationBlock extends StatelessWidget {
  final List<CitationData> citations;
  final void Function(CitationData)? onCitationTap;

  const CitationBlock({
    super.key,
    required this.citations,
    this.onCitationTap,
  });

  @override
  Widget build(BuildContext context) {
    if (citations.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.only(top: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A).withOpacity(0.5),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 12),
          _buildCitationList(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        const Icon(Icons.verified, size: 16, color: Color(0xFF10B981)),
        const SizedBox(width: 6),
        Text(
          'Verified Sources (${citations.length})',
          style: const TextStyle(
            color: Color(0xFF10B981),
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildCitationList() {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: citations.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final citation = citations[index];
        return CitationCard(
          citation: citation,
          index: index,
          onTap: () => onCitationTap?.call(citation),
        );
      },
    );
  }
}
