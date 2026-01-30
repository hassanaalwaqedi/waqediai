/// Chat Policy
///
/// Defines enterprise policies for AI responses.

class ChatPolicy {
  /// Minimum confidence threshold to display answer
  static const double minConfidenceThreshold = 0.3;

  /// Confidence below which to show disclaimer
  static const double lowConfidenceThreshold = 0.5;

  /// Maximum context tokens per query
  static const int maxContextTokens = 3000;

  /// Required permissions for chat
  static const String chatPermission = 'knowledge:query';

  /// Validate AI response before rendering
  static PolicyResult validateResponse({
    required String answer,
    required List<dynamic> citations,
    required double confidence,
  }) {
    // Rule 1: Must have citations
    if (citations.isEmpty) {
      return PolicyResult.blocked(
        reason: 'Response has no citations',
        userMessage: 'Unable to provide an answer with verifiable sources.',
      );
    }

    // Rule 2: Must meet minimum confidence
    if (confidence < minConfidenceThreshold) {
      return PolicyResult.blocked(
        reason: 'Confidence below threshold',
        userMessage: 'Unable to find reliable information for your question.',
      );
    }

    // Rule 3: Low confidence warning
    if (confidence < lowConfidenceThreshold) {
      return PolicyResult.warning(
        message: 'This answer is based on limited context. Please verify with source documents.',
      );
    }

    return PolicyResult.allowed();
  }

  /// Get refusal message based on reason
  static String getRefusalMessage(String reason) {
    switch (reason) {
      case 'no_documents':
        return 'No relevant documents found. Please upload related materials or try a different question.';
      case 'insufficient_permissions':
        return 'You do not have permission to access this knowledge base.';
      case 'rate_limited':
        return 'Request limit reached. Please wait a moment.';
      default:
        return 'Unable to process your request at this time.';
    }
  }

  /// System messages for policy enforcement
  static String get welcomeMessage =>
      'Welcome to WaqediAI. I can answer questions based on your organization\'s documents. '
      'All answers include citations to source materials.';

  static String get noResultsMessage =>
      'I couldn\'t find relevant information in the available documents. '
      'Try rephrasing your question or contact your administrator.';

  static String get lowConfidenceDisclaimer =>
      '⚠️ This response is based on limited context. Please verify with the cited sources.';
}

enum PolicyResultType { allowed, warning, blocked }

class PolicyResult {
  final PolicyResultType type;
  final String? message;
  final String? userMessage;
  final String? reason;

  const PolicyResult._({
    required this.type,
    this.message,
    this.userMessage,
    this.reason,
  });

  factory PolicyResult.allowed() => const PolicyResult._(type: PolicyResultType.allowed);

  factory PolicyResult.warning({required String message}) =>
      PolicyResult._(type: PolicyResultType.warning, message: message);

  factory PolicyResult.blocked({required String reason, required String userMessage}) =>
      PolicyResult._(type: PolicyResultType.blocked, reason: reason, userMessage: userMessage);

  bool get isAllowed => type == PolicyResultType.allowed;
  bool get hasWarning => type == PolicyResultType.warning;
  bool get isBlocked => type == PolicyResultType.blocked;
}
