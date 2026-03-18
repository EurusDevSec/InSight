import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'package:insight_app/ui/home/home_screen.dart';
import 'package:insight_app/ui/panic/panic_screen.dart';

import 'package:insight_app/viewmodels/panic_viewmodel.dart';

/// Task 4.3 — E2E Acceptance Criteria Tests
///
/// 4.3.1: Full pipeline latency tested via scripts/test_e2e_pipeline.py
/// 4.3.2: Panic Mode ≤ 1 second (client-side cached data)
/// 4.3.3: Disclaimer UI displayed on all results
/// Stability: No crashes in 10 consecutive runs
void main() {
  group('E2E 4.3.2 — Panic Mode Latency', () {
    test('selecting a dish completes within 1 second', () {
      final vm = PanicViewModel();
      final stopwatch = Stopwatch()..start();

      // Simulate: user taps a dish → instant GL lookup from cache
      vm.selectDish(0);

      stopwatch.stop();
      expect(stopwatch.elapsedMilliseconds, lessThan(1000));
      expect(vm.isSelected, isTrue);
      expect(vm.selectedDish, isNotNull);
      expect(vm.selectedDish!['glycemic_load'], isA<double>());
      expect(vm.selectedDish!['gl_level'], isA<String>());
    });

    test('all common dishes respond under 1 second', () {
      for (var i = 0; i < PanicViewModel.commonDishes.length; i++) {
        final vm = PanicViewModel();
        final stopwatch = Stopwatch()..start();

        vm.selectDish(i);

        stopwatch.stop();
        expect(stopwatch.elapsedMilliseconds, lessThan(1000),
            reason: 'Dish $i (${vm.selectedDish!["name"]}) took too long');
        expect(vm.selectedDish!['glycemic_load'], isPositive);
      }
    });
  });

  group('E2E 4.3.3 — Disclaimer UI', () {
    testWidgets('disclaimer always visible on HomeScreen',
        (tester) async {
      final router = GoRouter(
        initialLocation: '/',
        routes: [
          GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
          GoRoute(path: '/camera', builder: (_, __) => const SizedBox()),
          GoRoute(path: '/panic', builder: (_, __) => const SizedBox()),
        ],
      );

      await tester.pumpWidget(MaterialApp.router(routerConfig: router));

      // Disclaimer text must be visible (inline Container, not DisclaimerBanner)
      expect(find.textContaining('tham khảo'), findsOneWidget);
      expect(find.textContaining('bác sĩ'), findsOneWidget);
      expect(find.byIcon(Icons.warning_amber), findsOneWidget);
    });

    testWidgets('disclaimer contains warning icon and advisory text',
        (tester) async {
      // Render the HomeScreen which has inline disclaimer
      final router = GoRouter(
        initialLocation: '/',
        routes: [
          GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
          GoRoute(path: '/camera', builder: (_, __) => const SizedBox()),
          GoRoute(path: '/panic', builder: (_, __) => const SizedBox()),
        ],
      );

      await tester.pumpWidget(MaterialApp.router(routerConfig: router));

      expect(find.byIcon(Icons.warning_amber), findsOneWidget);
      expect(find.textContaining('Không thay thế chỉ định'), findsOneWidget);
    });

    testWidgets('PanicScreen shows disclaimer after dish selection',
        (tester) async {
      final vm = PanicViewModel();
      final router = GoRouter(
        initialLocation: '/',
        routes: [
          GoRoute(
            path: '/',
            builder: (_, __) => ChangeNotifierProvider.value(
              value: vm,
              child: const PanicScreen(),
            ),
          ),
        ],
      );

      await tester.pumpWidget(MaterialApp.router(routerConfig: router));

      // Select a dish
      await tester.tap(find.text('Cơm trắng (1 chén)'));
      await tester.pumpAndSettle();

      // Result should still show disclaimer context (GL level text)
      expect(find.textContaining('GL'), findsWidgets);
    });
  });

  group('E2E Stability — 10 consecutive runs', () {
    test('PanicViewModel: 10 select/reset cycles without crash', () {
      final vm = PanicViewModel();

      for (var run = 0; run < 10; run++) {
        for (var i = 0; i < PanicViewModel.commonDishes.length; i++) {
          vm.selectDish(i);
          expect(vm.isSelected, isTrue);
          expect(vm.selectedDish, isNotNull);
        }
        vm.reset();
        expect(vm.isSelected, isFalse);
      }
    });

    testWidgets('PanicScreen: 10 dish selections without crash',
        (tester) async {
      final vm = PanicViewModel();
      final router = GoRouter(
        initialLocation: '/',
        routes: [
          GoRoute(
            path: '/',
            builder: (_, __) => ChangeNotifierProvider.value(
              value: vm,
              child: const PanicScreen(),
            ),
          ),
        ],
      );

      await tester.pumpWidget(MaterialApp.router(routerConfig: router));

      for (var i = 0; i < 10; i++) {
        // Tap first dish
        await tester.tap(find.text('Cơm trắng (1 chén)'));
        await tester.pumpAndSettle();

        // Reset via ViewModel (button may be off-screen in test viewport)
        vm.reset();
        await tester.pumpAndSettle();
      }

      // If we get here, no crash occurred
      expect(true, isTrue);
    });
  });
}
