import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:altea_mobile/main.dart';

void main() {
  testWidgets('App renders registration screen', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: AlteaApp(),
      ),
    );
    await tester.pumpAndSettle();

    // Verify that the registration screen is displayed
    expect(find.text('Join Altea'), findsOneWidget);
    expect(find.text('Create your account to get started'), findsOneWidget);
  });
}
