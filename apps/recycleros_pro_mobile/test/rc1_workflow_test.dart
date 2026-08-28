import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:recycleros_domain/recycleros_domain.dart';
import 'package:recycleros_pro_mobile/src/app/recycleros_app.dart';
import 'package:recycleros_pro_mobile/src/state/rc1_workflow.dart';

import 'support/fake_rc1_gateway.dart';

void main() {
  testWidgets('completes the primary RC1 workflow', (tester) async {
    final gateway = FakeRc1Gateway();
    tester.view.physicalSize = const Size(430, 932);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [rc1GatewayProvider.overrideWithValue(gateway)],
        child: const RecyclerOSApp(),
      ),
    );
    await tester.pumpAndSettle();

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

    expect(find.text('Select Workspace'), findsOneWidget);
    await tester.tap(find.byKey(const Key('workspaceTile')));
    await tester.pumpAndSettle();

    expect(find.text('Mission Control'), findsOneWidget);
    await tester.tap(find.byKey(const Key('missionOpportunity')));
    await tester.pumpAndSettle();

    await tester.enterText(
      find.byKey(const Key('opportunityTitle')),
      '2019 Ford F-150 auction lead',
    );
    await tester.enterText(
      find.byKey(const Key('opportunityVin')),
      '1FTFW1E50KFA00001',
    );
    await tester.enterText(find.byKey(const Key('opportunityYear')), '2019');
    await tester.enterText(find.byKey(const Key('opportunityMake')), 'Ford');
    await tester.enterText(find.byKey(const Key('opportunityModel')), 'F-150');
    await tester.ensureVisible(find.byKey(const Key('createOpportunity')));
    await tester.tap(find.byKey(const Key('createOpportunity')));
    await tester.pumpAndSettle();

    expect(find.textContaining('OPP-000001'), findsWidgets);
    final createVehicle =
        find.byKey(const ValueKey('createVehicle-OPP-000001'));
    await tester.ensureVisible(createVehicle);
    await tester.tap(createVehicle);
    await tester.pumpAndSettle();

    expect(find.text('Vehicle Record'), findsOneWidget);
    expect(find.text('VEH-000001'), findsWidgets);
    await tester.tap(find.byKey(const Key('vehicleMileageEdit')));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('vehicleMileageField')),
      '141500',
    );
    await tester.tap(find.byKey(const Key('vehicleMileageSave')));
    await tester.pumpAndSettle();
    expect(find.text('141500'), findsOneWidget);
    await tester.ensureVisible(find.byKey(const Key('vehicleContinue')));
    await tester.tap(find.byKey(const Key('vehicleContinue')));
    await tester.pumpAndSettle();

    expect(find.text('Procurement'), findsOneWidget);
    await tester.tap(
      find.byKey(const ValueKey('procurementOption-personalUse')),
    );
    await tester.pumpAndSettle();
    expect(find.text('Approve Personal Buy / Use'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('procurementOption-resale')));
    await tester.pumpAndSettle();
    expect(find.text('Approve Sell Whole'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('procurementOption-partOut')));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('procurementApprove')));
    await tester.tap(find.byKey(const Key('procurementApprove')));
    await tester.pumpAndSettle();

    expect(find.text('Pick List'), findsOneWidget);
    await tester.tap(find.text('Available'));
    await tester.pumpAndSettle();
    final openFocus = find.text('Open Focus Point');
    await tester.ensureVisible(openFocus);
    await tester.tap(openFocus);
    await tester.pumpAndSettle();

    expect(find.text('Focus Point'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('part-ECM / PCM')));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('completeFocus')));
    await tester.tap(find.byKey(const Key('completeFocus')));
    await tester.pumpAndSettle();

    expect(find.text('Inventory Intake'), findsOneWidget);
    final partNameField = tester.widget<TextFormField>(
      find.byKey(const Key('inventoryPartName')),
    );
    expect(partNameField.controller?.text, 'ECM / PCM');
    await tester.ensureVisible(find.byKey(const Key('createInventory')));
    await tester.tap(find.byKey(const Key('createInventory')));
    await tester.pumpAndSettle();

    expect(find.textContaining('INV-000001'), findsWidgets);
    expect(find.text('Session Inventory'), findsOneWidget);
    await tester.tap(find.byTooltip('Mission Control'));
    await tester.pumpAndSettle();
    expect(find.text('Mission Control'), findsOneWidget);
    await tester.tap(find.byKey(const Key('signOut')));
    await tester.pumpAndSettle();

    expect(gateway.logoutCalls, 1);
    expect(gateway.lastUpdatedMileage, 141500);
    expect(gateway.lastProcurementIntent, ProcurementIntent.partOut);
    expect(find.text('Sign in'), findsOneWidget);
    expect(gateway.seenTenants, hasLength(10));
    expect(
      gateway.seenTenants.every(
        (tenant) =>
            tenant.organizationId == 'org-local' &&
            tenant.workspaceId == 'workspace-local',
      ),
      isTrue,
    );
    expect(tester.takeException(), isNull);
  });
}
