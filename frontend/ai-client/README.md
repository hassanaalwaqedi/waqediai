# WaqediAI AI Client

Enterprise AI Experience App (Flutter).

## Tech Stack

- Flutter 3.16+
- Dart 3.2+
- flutter_bloc (state management)
- dio (networking)
- get_it (DI)

## Structure

```
ai-client/
├── src/
│   ├── main.dart
│   ├── core/
│   │   ├── di/injection.dart
│   │   ├── network/api_client.dart
│   │   └── theme/app_theme.dart
│   └── features/
│       ├── auth/
│       ├── chat/
│       └── documents/
├── assets/
└── pubspec.yaml
```

## Features

- AI Copilot Chat
- Document Q&A
- Citation display
- Multi-tenant support

## Running

```bash
flutter pub get
flutter run
```

## Platform Support

- Mobile (Android/iOS)
- Web
- Desktop (future)
