import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';
import '../../features/splash/screens/splash_screen.dart';
import '../../features/onboarding/screens/onboarding_screen.dart';
import '../../features/auth/screens/signin_screen.dart';
import '../../features/auth/screens/signup_screen.dart';
import '../../features/home/screens/home_screen.dart';
import '../../features/chat/screens/chat_screen.dart';
import '../../features/tools/screens/tools_screen.dart';
import '../../features/tools/screens/breathing_bubble_screen.dart';
import '../../features/tools/screens/calm_puzzle_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/crisis/screens/crisis_screen.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/onboarding/:step',
      builder: (context, state) {
        final step = int.tryParse(state.pathParameters['step'] ?? '0') ?? 0;
        return OnboardingScreen(initialStep: step);
      },
    ),
    GoRoute(
      path: '/signin',
      builder: (context, state) => const SignInScreen(),
    ),
    GoRoute(
      path: '/signup',
      builder: (context, state) => const SignUpScreen(),
    ),
    GoRoute(
      path: '/home',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/chat',
      builder: (context, state) => const ChatScreen(),
    ),
    GoRoute(
      path: '/tools',
      builder: (context, state) => const ToolsScreen(),
    ),
    GoRoute(
      path: '/breathing-bubble',
      builder: (context, state) => const BreathingBubbleScreen(),
    ),
    GoRoute(
      path: '/calm-puzzle',
      builder: (context, state) => const CalmPuzzleScreen(),
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => const ProfileScreen(),
    ),
    GoRoute(
      path: '/crisis',
      builder: (context, state) => const CrisisScreen(),
    ),
  ],
);
