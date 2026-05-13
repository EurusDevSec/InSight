import 'package:go_router/go_router.dart';

import '../ui/shell/app_shell.dart';
import '../ui/onboarding/onboarding_screen.dart';
import '../ui/home/home_screen.dart';
import '../ui/camera/camera_screen.dart';
import '../ui/food_form/food_form_screen.dart';
import '../ui/result/result_screen.dart';
import '../ui/panic/panic_screen.dart';
import '../ui/history/history_screen.dart';
import '../ui/history/meal_detail_screen.dart';
import '../ui/settings/settings_screen.dart';
import '../ui/profile/patient_profile_screen.dart';
import '../ui/analytics/analytics_screen.dart';
import '../ui/chat/chat_screen.dart';

/// Create router — call with hasOnboarded flag.
GoRouter createRouter({required bool hasOnboarded}) {
  return GoRouter(
    initialLocation: hasOnboarded ? '/' : '/onboarding',
    routes: [
      // Onboarding (no bottom nav)
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),

      // Shell with bottom navigation
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return AppShell(
            currentIndex: navigationShell.currentIndex,
            onTap: (index) => navigationShell.goBranch(index),
            child: navigationShell,
          );
        },
        branches: [
          // Tab 0: Home
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/',
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          // Tab 1: Analytics
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/analytics',
                builder: (context, state) => const AnalyticsScreen(),
              ),
            ],
          ),
          // Tab 2: History
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/history',
                builder: (context, state) => const HistoryScreen(),
              ),
            ],
          ),
          // Tab 3: Settings
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/settings',
                builder: (context, state) => const SettingsScreen(),
              ),
            ],
          ),
        ],
      ),

      // Full-screen routes (no bottom nav)
      GoRoute(
        path: '/camera',
        builder: (context, state) => const CameraScreen(),
      ),
      GoRoute(
        path: '/food-form',
        builder: (context, state) => const FoodFormScreen(),
      ),
      GoRoute(
        path: '/result',
        builder: (context, state) => const ResultScreen(),
      ),
      GoRoute(
        path: '/panic',
        builder: (context, state) => const PanicScreen(),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const PatientProfileScreen(),
      ),
      GoRoute(
        path: '/history/detail',
        builder: (context, state) {
          final meal = state.extra as Map<String, dynamic>;
          return MealDetailScreen(meal: meal);
        },
      ),
      GoRoute(
        path: '/chat',
        builder: (context, state) => const ChatScreen(),
      ),
    ],
  );
}

