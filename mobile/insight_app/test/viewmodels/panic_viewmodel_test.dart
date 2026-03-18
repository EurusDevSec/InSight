import 'package:flutter_test/flutter_test.dart';

import 'package:insight_app/viewmodels/panic_viewmodel.dart';

void main() {
  group('PanicViewModel', () {
    late PanicViewModel vm;

    setUp(() {
      vm = PanicViewModel();
    });

    test('initial state is not selected', () {
      expect(vm.isSelected, isFalse);
      expect(vm.selectedDish, isNull);
    });

    test('commonDishes has entries', () {
      expect(PanicViewModel.commonDishes, isNotEmpty);
      expect(PanicViewModel.commonDishes.length, greaterThanOrEqualTo(5));
    });

    test('each dish has required fields', () {
      for (final dish in PanicViewModel.commonDishes) {
        expect(dish.containsKey('name'), isTrue);
        expect(dish.containsKey('carbs_g'), isTrue);
        expect(dish.containsKey('glycemic_load'), isTrue);
        expect(dish.containsKey('gl_level'), isTrue);
        expect(dish['carbs_g'], isA<double>());
        expect(dish['glycemic_load'], isA<double>());
      }
    });

    test('selectDish updates state', () {
      var notified = false;
      vm.addListener(() => notified = true);

      vm.selectDish(0);

      expect(vm.isSelected, isTrue);
      expect(vm.selectedDish, isNotNull);
      expect(vm.selectedDish!['name'], PanicViewModel.commonDishes[0]['name']);
      expect(notified, isTrue);
    });

    test('selectDish with different index', () {
      vm.selectDish(2);
      expect(vm.selectedDish!['name'], PanicViewModel.commonDishes[2]['name']);
    });

    test('reset clears selection', () {
      vm.selectDish(0);
      expect(vm.isSelected, isTrue);

      vm.reset();
      expect(vm.isSelected, isFalse);
      expect(vm.selectedDish, isNull);
    });

    test('notifyListeners fires on selectDish', () {
      var count = 0;
      vm.addListener(() => count++);

      vm.selectDish(0);
      vm.selectDish(1);
      vm.reset();

      expect(count, 3);
    });
  });
}
