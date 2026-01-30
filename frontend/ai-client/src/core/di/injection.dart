/// Dependency injection configuration
///
/// Uses get_it for service locator pattern.

import 'package:get_it/get_it.dart';
import '../auth/auth_storage.dart';
import '../auth/auth_repository.dart';
import '../network/api_client.dart';
import '../../features/auth/auth_bloc.dart';
import '../../features/chat/chat_bloc.dart';
import '../../features/chat/chat_repository.dart';

final getIt = GetIt.instance;

/// Configure all dependencies
Future<void> configureDependencies() async {
  // Core - Storage
  getIt.registerLazySingleton<AuthStorage>(() => AuthStorage());

  // Core - Auth
  getIt.registerLazySingleton<AuthRepository>(
    () => AuthRepository(
      storage: getIt<AuthStorage>(),
      baseUrl: const String.fromEnvironment(
        'AUTH_API_URL',
        defaultValue: 'http://localhost:8001',
      ),
    ),
  );

  // Core - Network
  getIt.registerLazySingleton<RagApiClient>(
    () => RagApiClient(storage: getIt<AuthStorage>()),
  );

  // Repositories
  getIt.registerLazySingleton<ChatRepository>(
    () => ChatRepository(apiClient: getIt<RagApiClient>()),
  );

  // BLoCs
  getIt.registerFactory<AuthBloc>(
    () => AuthBloc(authRepository: getIt<AuthRepository>()),
  );

  getIt.registerFactory<ChatBloc>(
    () => ChatBloc(chatRepository: getIt<ChatRepository>()),
  );
}
