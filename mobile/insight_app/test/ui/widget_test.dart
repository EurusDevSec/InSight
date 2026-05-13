import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:insight_app/ui/home/home_screen.dart';
import 'package:insight_app/ui/widgets/gl_indicator.dart';
import 'package:insight_app/ui/widgets/disclaimer_banner.dart';
import 'package:insight_app/ui/panic/panic_screen.dart';
import 'package:insight_app/viewmodels/panic_viewmodel.dart';
import 'package:insight_app/viewmodels/history_viewmodel.dart';
import 'package:insight_app/viewmodels/settings_viewmodel.dart';
import 'package:insight_app/data/services/local_storage_service.dart';

/// Helper: wrap HomeScreen with required providers + router.
Future<Widget> _wrapHomeScreen() async {
  SharedPreferences.setMockInitialValues({});
  final storage = LocalStorageService();
  await storage.init();

  final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/camera', builder: (_, __) => const SizedBox()),
      GoRoute(path: '/panic', builder: (_, __) => const SizedBox()),
      GoRoute(path: '/profile', builder: (_, __) => const SizedBox()),
      GoRoute(path: '/history', builder: (_, __) => const SizedBox()),
    ],
  );

  return MultiProvider(
    providers: [
      ChangeNotifierProvider(create: (_) => HistoryViewModel(storage)),
      ChangeNotifierProvider(create: (_) => SettingsViewModel(storage)),
    ],
    child: MaterialApp.router(routerConfig: router),
  );
}

void main() {
  setUpAll(() async {
    SharedPreferences.setMockInitialValues({});
  });

  group('HomeScreen', () {
    testWidgets('shows greeting and quick action cards', (tester) async {
      await tester.pumpWidget(await _wrapHomeScreen());
      await tester.pumpAndSettle();

      // Quick action card labels
      expect(find.text('Chụp ảnh\nphân tích'), findsOneWidget);
      expect(find.text('Ước lượng\nnhanh ⚡'), findsOneWidget);
    });

    testWidgets('shows disclaimer', (tester) async {
      await tester.pumpWidget(await _wrapHomeScreen());
      await tester.pumpAndSettle();

      // Scroll to find disclaimer at bottom
      await tester.dragUntilVisible(
        find.textContaining('Không thay thế chỉ định'),
        find.byType(SingleChildScrollView),
        const Offset(0, -200),
      );

      expect(
        find.textContaining('Không thay thế chỉ định'),
        findsOneWidget,
      );
    });

    testWidgets('shows tips section', (tester) async {
      await tester.pumpWidget(await _wrapHomeScreen());
      await tester.pumpAndSettle();

      // Scroll to find tips
      await tester.dragUntilVisible(
        find.textContaining('Mẹo'),
        find.byType(SingleChildScrollView),
        const Offset(0, -200),
      );

      expect(find.textContaining('Mẹo'), findsOneWidget);
    });
  });

  group('GlIndicator', () {
    testWidgets('shows GL value and low level', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Center(
              child: GlIndicator(glycemicLoad: 5.0, glLevel: 'low'),
            ),
          ),
        ),
      );
      // Wait for animation to complete
      await tester.pumpAndSettle();

      expect(find.text('5.0'), findsOneWidget);
      expect(find.text('Thấp'), findsOneWidget);
      expect(find.text('GL'), findsOneWidget);
    });

    testWidgets('shows medium level', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Center(
              child: GlIndicator(glycemicLoad: 13.7, glLevel: 'medium'),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('13.7'), findsOneWidget);
      expect(find.text('Trung bình'), findsOneWidget);
    });

    testWidgets('shows high level', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Center(
              child: GlIndicator(glycemicLoad: 33.0, glLevel: 'high'),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('33.0'), findsOneWidget);
      expect(find.text('Cao'), findsOneWidget);
    });
  });

  group('DisclaimerBanner', () {
    testWidgets('shows warning text', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: Scaffold(body: DisclaimerBanner())),
      );

      expect(find.textContaining('tham khảo'), findsOneWidget);
      expect(find.textContaining('bác sĩ'), findsOneWidget);
      expect(find.byIcon(Icons.warning_amber), findsOneWidget);
    });
  });

  group('PanicScreen', () {
    testWidgets('shows grid of common dishes', (tester) async {
      final router = GoRouter(
        initialLocation: '/',
        routes: [
          GoRoute(
            path: '/',
            builder: (_, __) => ChangeNotifierProvider(
              create: (_) => PanicViewModel(),
              child: const PanicScreen(),
            ),
          ),
        ],
      );

      await tester.pumpWidget(MaterialApp.router(routerConfig: router));

      expect(find.text('Chọn món đang ăn'), findsOneWidget);
      expect(find.text('Cơm trắng (1 chén)'), findsOneWidget);
      expect(find.text('Phở bò (1 tô)'), findsOneWidget);
    });

    testWidgets('selecting a dish shows result', (tester) async {
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

      // Tap the first dish card
      await tester.tap(find.text('Cơm trắng (1 chén)'));
      await tester.pumpAndSettle();

      // Should show GL result
      expect(find.text('33'), findsOneWidget); // GL value section
      expect(find.text('Chọn món khác'), findsOneWidget);
      expect(find.text('Xong'), findsOneWidget);
    });
  });
}
