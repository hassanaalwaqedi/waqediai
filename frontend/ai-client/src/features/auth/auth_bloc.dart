/// Auth BLoC
///
/// Manages authentication state for Flutter app.

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../core/auth/auth_repository.dart';
import '../../core/auth/auth_storage.dart';

// Events
abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class AuthCheckRequested extends AuthEvent {}

class AuthLoginRequested extends AuthEvent {
  final String email;
  final String password;
  final String? tenantSlug;

  const AuthLoginRequested({
    required this.email,
    required this.password,
    this.tenantSlug,
  });

  @override
  List<Object?> get props => [email, password, tenantSlug];
}

class AuthLogoutRequested extends AuthEvent {}

class AuthRefreshRequested extends AuthEvent {}

// States
abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthAuthenticated extends AuthState {
  final User user;

  const AuthAuthenticated(this.user);

  @override
  List<Object?> get props => [user];
}

class AuthUnauthenticated extends AuthState {
  final String? message;

  const AuthUnauthenticated({this.message});

  @override
  List<Object?> get props => [message];
}

class AuthError extends AuthState {
  final String message;

  const AuthError(this.message);

  @override
  List<Object?> get props => [message];
}

// BLoC
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;

  AuthBloc({required AuthRepository authRepository})
      : _authRepository = authRepository,
        super(AuthInitial()) {
    on<AuthCheckRequested>(_onCheckRequested);
    on<AuthLoginRequested>(_onLoginRequested);
    on<AuthLogoutRequested>(_onLogoutRequested);
    on<AuthRefreshRequested>(_onRefreshRequested);
  }

  Future<void> _onCheckRequested(
    AuthCheckRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    try {
      final user = await _authRepository.restoreSession();
      if (user != null) {
        emit(AuthAuthenticated(user));
      } else {
        emit(const AuthUnauthenticated());
      }
    } catch (e) {
      emit(const AuthUnauthenticated());
    }
  }

  Future<void> _onLoginRequested(
    AuthLoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    try {
      final user = await _authRepository.login(
        email: event.email,
        password: event.password,
        tenantSlug: event.tenantSlug,
      );
      emit(AuthAuthenticated(user));
    } on AuthException catch (e) {
      emit(AuthError(e.message));
    } catch (e) {
      emit(AuthError('Login failed: $e'));
    }
  }

  Future<void> _onLogoutRequested(
    AuthLogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    await _authRepository.logout();
    emit(const AuthUnauthenticated(message: 'Logged out'));
  }

  Future<void> _onRefreshRequested(
    AuthRefreshRequested event,
    Emitter<AuthState> emit,
  ) async {
    final success = await _authRepository.refresh();
    if (!success) {
      emit(const AuthUnauthenticated(message: 'Session expired'));
    }
  }

  // Helper methods for permission checking
  bool hasRole(String role) {
    final currentState = state;
    if (currentState is AuthAuthenticated) {
      return currentState.user.hasRole(role);
    }
    return false;
  }

  bool hasPermission(String permission) {
    final currentState = state;
    if (currentState is AuthAuthenticated) {
      return currentState.user.hasPermission(permission);
    }
    return false;
  }
}
