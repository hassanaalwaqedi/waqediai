/// Confidence Indicator Widget
///
/// Shows AI confidence level.

import 'package:flutter/material.dart';

class ConfidenceIndicator extends StatelessWidget {
  final double confidence;
  final bool showText;

  const ConfidenceIndicator({
    super.key,
    required this.confidence,
    this.showText = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getColor();
    final label = _getLabel();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getIcon(), size: 12, color: color),
          if (showText) ...[
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getColor() {
    if (confidence >= 0.8) return const Color(0xFF10B981);
    if (confidence >= 0.5) return const Color(0xFFF59E0B);
    return const Color(0xFFEF4444);
  }

  IconData _getIcon() {
    if (confidence >= 0.8) return Icons.check_circle;
    if (confidence >= 0.5) return Icons.info;
    return Icons.warning;
  }

  String _getLabel() {
    if (confidence >= 0.8) return 'High confidence';
    if (confidence >= 0.5) return 'Moderate confidence';
    return 'Low confidence';
  }
}
