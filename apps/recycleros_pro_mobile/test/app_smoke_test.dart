import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:recycleros_pro_mobile/src/app/app_routes.dart';
import 'package:recycleros_pro_mobile/src/app/recycleros_app.dart';
import 'package:recycleros_pro_mobile/src/state/rc1_workflow.dart';

import 'support/fake_rc1_gateway.dart';

void main() {
  testWidgets('renders the login screen', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          rc1GatewayProvider.overrideWithValue(FakeRc1Gateway()),
        ],
        child: const RecyclerOSApp(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('RecyclerOS Pro'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);
  });

  testWidgets('redirects an unauthenticated operational deep link to login', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          rc1GatewayProvider.overrideWithValue(FakeRc1Gateway()),
        ],
        child: const RecyclerOSApp(
          initialLocation: AppPaths.opportunities,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('RecyclerOS Pro'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('New Opportunity'), findsNothing);
  });
}
