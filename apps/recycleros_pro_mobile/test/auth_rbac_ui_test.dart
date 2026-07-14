import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:recycleros_pro_mobile/src/app/recycleros_app.dart';
import 'package:recycleros_pro_mobile/src/state/rc1_workflow.dart';

import 'support/fake_rc1_gateway.dart';

void main() {
  testWidgets('keeps the user on sign in when authentication fails', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          rc1GatewayProvider.overrideWithValue(
            FakeRc1Gateway(signInError: 'Invalid email or password.'),
          ),
        ],
        child: const RecyclerOSApp(),
      ),
    );

    await _submitLogin(tester);

    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Invalid email or password.'), findsOneWidget);
  });

  testWidgets('viewer can select a workspace but cannot create records', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          rc1GatewayProvider.overrideWithValue(FakeRc1Gateway(role: 'viewer')),
        ],
        child: const RecyclerOSApp(),
      ),
    );

    await _submitLogin(tester);
    expect(find.textContaining('Viewer'), findsOneWidget);
    await tester.tap(find.byKey(const Key('workspaceTile')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('missionOpportunity')));
    await tester.pumpAndSettle();

    final createButton = tester.widget<FilledButton>(
      find.byKey(const Key('createOpportunity')),
    );
    expect(createButton.onPressed, isNull);
  });
}

Future<void> _submitLogin(WidgetTester tester) async {
  await tester.enterText(
    find.byKey(const Key('emailField')),
    'operator@effortlesssmoke.com',
  );
  await tester.enterText(
    find.byKey(const Key('passwordField')),
    'local-rc1',
  );
  await tester.tap(find.byKey(const Key('loginContinue')));
  await tester.pumpAndSettle();
}
