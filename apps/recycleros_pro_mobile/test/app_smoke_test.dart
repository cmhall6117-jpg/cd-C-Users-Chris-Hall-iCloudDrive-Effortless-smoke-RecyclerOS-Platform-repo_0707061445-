import 'package:flutter_test/flutter_test.dart';
import 'package:recycleros_pro_mobile/src/app/recycleros_app.dart';

void main() {
  testWidgets('renders the login screen', (tester) async {
    await tester.pumpWidget(const RecyclerOSApp());
    await tester.pumpAndSettle();

    expect(find.text('RecyclerOS Pro'), findsOneWidget);
    expect(find.text('Login'), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);
  });
}
