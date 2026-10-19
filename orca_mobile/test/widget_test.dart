import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:orca_mobile/main.dart';

void main() {
  testWidgets('ORCA home screen renders the demo amount and primary action',
      (WidgetTester tester) async {
    await tester.pumpWidget(const OrcaApp());

    expect(find.text('Amount due this month (demo)'), findsOneWidget);
    expect(find.text('Pay installment'), findsOneWidget);
    expect(find.text('38,000'), findsOneWidget);
  });

  testWidgets('Tapping pay installment opens the pay screen',
      (WidgetTester tester) async {
    await tester.pumpWidget(const OrcaApp());

    await tester.tap(find.text('Pay installment'));
    await tester.pumpAndSettle();

    expect(find.text('Amount toward your Smart TV (TZS)'), findsOneWidget);
  });
}
