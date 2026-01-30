/// Citation Model
///
/// Represents a source citation from a document.

import 'package:equatable/equatable.dart';

class Citation extends Equatable {
  final String chunkId;
  final String documentId;
  final String textExcerpt;
  final String? documentTitle;
  final int? pageNumber;

  const Citation({
    required this.chunkId,
    required this.documentId,
    required this.textExcerpt,
    this.documentTitle,
    this.pageNumber,
  });

  factory Citation.fromJson(Map<String, dynamic> json) {
    return Citation(
      chunkId: json['chunk_id'] ?? '',
      documentId: json['document_id'] ?? '',
      textExcerpt: json['text_excerpt'] ?? '',
      documentTitle: json['document_title'],
      pageNumber: json['page_number'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'chunk_id': chunkId,
      'document_id': documentId,
      'text_excerpt': textExcerpt,
      if (documentTitle != null) 'document_title': documentTitle,
      if (pageNumber != null) 'page_number': pageNumber,
    };
  }

  /// Short display label
  String get label => documentTitle ?? documentId.substring(0, 8);

  /// Full reference
  String get reference {
    final page = pageNumber != null ? ' (p.$pageNumber)' : '';
    return '$label$page';
  }

  @override
  List<Object?> get props => [chunkId, documentId, textExcerpt];
}
