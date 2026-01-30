/// Citation Data
///
/// Represents a verified source citation.

import 'package:equatable/equatable.dart';

enum SourceType { pdf, audio, image, text, unknown }

class CitationData extends Equatable {
  final String documentId;
  final String documentTitle;
  final String chunkId;
  final int? page;
  final String snippet;
  final String language;
  final SourceType sourceType;

  const CitationData({
    required this.documentId,
    required this.documentTitle,
    required this.chunkId,
    this.page,
    required this.snippet,
    required this.language,
    required this.sourceType,
  });

  factory CitationData.fromJson(Map<String, dynamic> json) {
    return CitationData(
      documentId: json['document_id'] ?? '',
      documentTitle: json['document_title'] ?? 'Unknown Document',
      chunkId: json['chunk_id'] ?? '',
      page: json['page'],
      snippet: json['snippet'] ?? json['text_excerpt'] ?? '',
      language: json['language'] ?? 'en',
      sourceType: _parseSourceType(json['source_type']),
    );
  }

  static SourceType _parseSourceType(String? type) {
    switch (type) {
      case 'pdf': return SourceType.pdf;
      case 'audio': return SourceType.audio;
      case 'image': return SourceType.image;
      case 'text': return SourceType.text;
      default: return SourceType.unknown;
    }
  }

  String get sourceIcon {
    switch (sourceType) {
      case SourceType.pdf: return '📄';
      case SourceType.audio: return '🎧';
      case SourceType.image: return '🖼️';
      case SourceType.text: return '📝';
      case SourceType.unknown: return '📎';
    }
  }

  String get reference => page != null ? '$documentTitle (p. $page)' : documentTitle;

  bool get isValid => documentId.isNotEmpty && chunkId.isNotEmpty && snippet.isNotEmpty;

  @override
  List<Object?> get props => [documentId, chunkId];
}
