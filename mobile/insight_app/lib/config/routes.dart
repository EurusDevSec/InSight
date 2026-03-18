import 'package:go_router/go_router.dart';

import '../ui/home/home_screen.dart';
import '../ui/camera/camera_screen.dart';
import '../ui/food_form/food_form_screen.dart';
import '../ui/result/result_screen.dart';
import '../ui/panic/panic_screen.dart';

/// App-wide route configuration using go_router.
final GoRouter router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
    ),
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
  ],
);
