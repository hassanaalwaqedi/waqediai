/// WaqediAI - Enterprise AI Experience App
///
/// Main entry point for the Flutter AI client.

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'core/di/injection.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/presentation/bloc/auth_bloc.dart';
import 'features/auth/presentation/pages/login_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await configureDependencies();
  runApp(const WaqediAIApp());
}

class WaqediAIApp extends StatelessWidget {
  const WaqediAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => getIt<AuthBloc>()),
      ],
      child: MaterialApp(
        title: 'WaqediAI',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: const LoginPage(),
      ),
    );
  }
}
