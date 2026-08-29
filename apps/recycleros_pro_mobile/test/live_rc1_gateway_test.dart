import 'package:flutter_test/flutter_test.dart';
import 'package:recycleros_domain/recycleros_domain.dart';
import 'package:recycleros_pro_mobile/src/data/dio_rc1_gateway.dart';
import 'package:recycleros_pro_mobile/src/data/rc1_gateway.dart';

const _liveApiEnabled = bool.fromEnvironment('RECYCLEROS_LIVE_API_TEST');
const _testPassword = String.fromEnvironment('RECYCLEROS_TEST_PASSWORD');

void main() {
  test(
    'completes the RC1 path against a running FastAPI service',
    () async {
      final gateway = DioRc1Gateway();
      final session = await gateway.signIn(
        email: 'operator@effortlesssmoke.com',
        password: _testPassword,
      );
      final membership = session.memberships.single;
      final tenant = TenantScope(
        organizationId: membership.organizationId,
        workspaceId: membership.workspaceId,
      );

      final opportunity = await gateway.createOpportunity(
        tenant,
        title: '2019 Ford F-150 live integration',
        vin: '1FTFW1E50KFA00001',
        year: 2019,
        make: 'Ford',
        model: 'F-150',
      );
      final vehicle = await gateway.createVehicle(
        tenant,
        opportunity: opportunity,
      );
      final updatedVehicle = await gateway.updateVehicleMileage(
        tenant,
        vehicle: vehicle,
        mileage: 141500,
      );
      final scenarios = await gateway.getProcurementAnalysis(
        tenant,
        opportunityId: opportunity.opportunityId,
      );
      final decidedOpportunity = await gateway.updateProcurementDecision(
        tenant,
        opportunity: opportunity,
        intent: ProcurementIntent.partOut,
      );
      final pendingPick = await gateway.createPickListItem(
        tenant,
        vehicle: updatedVehicle,
      );
      final availablePick = await gateway.updatePickListAvailability(
        tenant,
        item: pendingPick,
        availabilityStatus: 'available',
      );
      final activeSession = await gateway.startFocusPoint(
        tenant,
        vehicleId: vehicle.vehicleId,
      );
      final completedSession = await gateway.completeFocusPoint(
        tenant,
        harvestSessionId: activeSession.harvestSessionId,
      );
      final inventory = await gateway.createInventoryItem(
        tenant,
        partName: 'ECM / PCM',
        storageLocation: 'A-12',
        condition: PartCondition.usedUntested,
        status: InventoryStatus.available,
        sourceVehicleId: vehicle.vehicleId,
        harvestSessionId: completedSession.harvestSessionId,
      );

      expect(opportunity.opportunityCode, 'OPP-000001');
      expect(vehicle.vehicleCode, 'VEH-000001');
      expect(updatedVehicle.mileage, 141500);
      expect(scenarios, hasLength(3));
      expect(decidedOpportunity.procurementIntent, ProcurementIntent.partOut);
      expect(availablePick.availabilityStatus, 'available');
      expect(completedSession.status, 'completed');
      expect(inventory.inventoryCode, 'INV-000001');
      expect(inventory.sourceVehicleId, vehicle.vehicleId);
    },
    skip: !_liveApiEnabled,
  );
}
