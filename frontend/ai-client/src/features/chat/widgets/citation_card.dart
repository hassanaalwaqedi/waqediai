/// Citation Card Widget
///
/// Renders a single citation with document info.

import 'package:flutter/material.dart';
import 'citation_data.dart';

class CitationCard extends StatelessWidget {
  final CitationData citation;
  final int index;
  final VoidCallback? onTap;

  const CitationCard({
    super.key,
    required this.citation,
    required this.index,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFF334155)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            const SizedBox(height: 8),
            _buildSnippet(),
            const SizedBox(height: 8),
            _buildFooter(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: const Color(0xFF3B82F6).withOpacity(0.2),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Center(
            child: Text(
              '${index + 1}',
              style: const TextStyle(
                color: Color(0xFF3B82F6),
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            citation.documentTitle,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        Text(
          citation.sourceIcon,
          style: const TextStyle(fontSize: 16),
        ),
      ],
    );
  }

  Widget _buildSnippet() {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF334155).withOpacity(0.5)),
      ),
      child: Text(
        '"${citation.snippet}"',
        style: TextStyle(
          color: Colors.grey.shade300,
          fontSize: 13,
          fontStyle: FontStyle.italic,
          height: 1.4,
        ),
        maxLines: 3,
        overflow: TextOverflow.ellipsis,
      ),
    );
  }

  Widget _buildFooter() {
    return Row(
      children: [
        Icon(Icons.article_outlined, size: 14, color: Colors.grey.shade500),
        const SizedBox(width: 4),
        Text(
          citation.documentId.substring(0, 8),
          style: TextStyle(color: Colors.grey.shade500, fontSize: 11),
        ),
        if (citation.page != null) ...[
          const SizedBox(width: 12),
          Icon(Icons.bookmark_outline, size: 14, color: Colors.grey.shade500),
          const SizedBox(width: 4),
          Text(
            'Page ${citation.page}',
            style: TextStyle(color: Colors.grey.shade500, fontSize: 11),
          ),
        ],
        const Spacer(),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: const Color(0xFF334155),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            citation.language.toUpperCase(),
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 10,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }
}
