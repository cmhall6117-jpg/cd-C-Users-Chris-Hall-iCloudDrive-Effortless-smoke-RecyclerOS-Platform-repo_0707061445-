import 'package:recycleros_domain/recycleros_domain.dart';
import 'package:recycleros_pro_mobile/src/data/rc1_gateway.dart';

class FakeRc1Gateway implements Rc1Gateway {
  FakeRc1Gateway({this.role = 'operator', this.signInError});

  final String role;
  final String? signInError;
  final List<TenantScope> seenTenants = [];

  int _opportunitySequence = 0;
  int _vehicleSequence = 0;
  int _pickListSequence = 0;
  int _harvestSequence = 0;
  int _inventorySequence = 0;
  HarvestSession? _harvestSession;

  static final DateTime _now = DateTime.utc(2026, 7, 14, 12);

  void _record(TenantScope tenant) {
    seenTenants.add(tenant);
  }

  @override
  Future<AuthSession> signIn({
    required String email,
    required String password,
  }) async {
    if (signInError != null) {
      throw Rc1GatewayException(signInError!);
    }
    return AuthSession(
      userId: 'user-local',
      email: email,
      displayName: 'Local Operator',
      expiresAt: DateTime.now().toUtc().add(const Duration(hours: 8)),
      memberships: [
        TenantMembership(
          organizationId: 'org-local',
          organizationName: 'Effortless Smoke, LLC',
          workspaceId: 'workspace-local',
          workspaceName: 'RecyclerOS Operations',
          role: role,
        ),
      ],
    );
  }

  @override
  Future<Opportunity> createOpportunity(
    TenantScope tenant, {
    required String title,
    String? vin,
    int? year,
    String? make,
    String? model,
  }) async {
    _record(tenant);
    _opportunitySequence += 1;
    return Opportunity(
      opportunityId: 'opportunity-$_opportunitySequence',
      opportunityCode:
          'OPP-${_opportunitySequence.toString().padLeft(6, '0')}',
      title: title,
      source: OpportunitySource.manual,
      status: OpportunityStatus.discovered,
      procurementIntent: ProcurementIntent.partOut,
      vin: vin,
      year: year,
      make: make,
      model: model,
      estimatedMaxBid: 3900,
      estimatedNetProfit: 3250,
      confidenceScore: 81,
      createdAt: _now,
      updatedAt: _now,
    );
  }

  @override
  Future<Vehicle> createVehicle(
    TenantScope tenant, {
    required Opportunity opportunity,
  }) async {
    _record(tenant);
    _vehicleSequence += 1;
    return Vehicle(
      vehicleId: 'vehicle-$_vehicleSequence',
      vehicleCode: 'VEH-${_vehicleSequence.toString().padLeft(6, '0')}',
      vin: opportunity.vin,
      year: opportunity.year,
      make: opportunity.make,
      model: opportunity.model,
      mileage: 126000,
      lifecycleStatus: VehicleLifecycleStatus.discovered,
      createdAt: _now,
      updatedAt: _now,
    );
  }

  @override
  Future<List<ProcurementScenario>> getProcurementAnalysis(
    TenantScope tenant, {
    required String opportunityId,
  }) async {
    _record(tenant);
    return const [
      ProcurementScenario(
        intent: ProcurementIntent.resale,
        projectedRevenue: 9500,
        projectedCosts: 7550,
        recommendedMaxBid: 4800,
        projectedNetProfit: 1950,
        projectedMarginPercent: 20.5,
        confidenceScore: 72,
      ),
      ProcurementScenario(
        intent: ProcurementIntent.personalUse,
        projectedRevenue: 0,
        projectedCosts: 5300,
        recommendedMaxBid: 5300,
        projectedNetProfit: 0,
        projectedMarginPercent: 0,
        confidenceScore: 65,
      ),
      ProcurementScenario(
        intent: ProcurementIntent.partOut,
        projectedRevenue: 8500,
        projectedCosts: 5250,
        recommendedMaxBid: 3900,
        projectedNetProfit: 3250,
        projectedMarginPercent: 38.2,
        confidenceScore: 81,
      ),
    ];
  }

  @override
  Future<PickListItem> createPickListItem(
    TenantScope tenant, {
    required Vehicle vehicle,
  }) async {
    _record(tenant);
    _pickListSequence += 1;
    return PickListItem(
      pickListItemId: 'pick-list-$_pickListSequence',
      vehicleId: vehicle.vehicleId,
      yardName: 'Greenville Pull-A-Part',
      row: '12',
      year: vehicle.year ?? 2026,
      make: vehicle.make ?? 'Unknown',
      model: vehicle.model ?? 'Vehicle',
      vin: vehicle.vin,
      availabilityStatus: 'pending',
    );
  }

  @override
  Future<PickListItem> updatePickListAvailability(
    TenantScope tenant, {
    required PickListItem item,
    required String availabilityStatus,
  }) async {
    _record(tenant);
    return PickListItem(
      pickListItemId: item.pickListItemId,
      vehicleId: item.vehicleId,
      yardName: item.yardName,
      row: item.row,
      year: item.year,
      make: item.make,
      model: item.model,
      vin: item.vin,
      availabilityStatus: availabilityStatus,
    );
  }

  @override
  Future<HarvestSession> startFocusPoint(
    TenantScope tenant, {
    required String vehicleId,
  }) async {
    _record(tenant);
    _harvestSequence += 1;
    _harvestSession = HarvestSession(
      harvestSessionId: 'harvest-$_harvestSequence',
      vehicleId: vehicleId,
      startedAt: _now,
      status: 'active',
    );
    return _harvestSession!;
  }

  @override
  Future<HarvestSession> completeFocusPoint(
    TenantScope tenant, {
    required String harvestSessionId,
  }) async {
    _record(tenant);
    final current = _harvestSession!;
    _harvestSession = HarvestSession(
      harvestSessionId: harvestSessionId,
      vehicleId: current.vehicleId,
      startedAt: current.startedAt,
      endedAt: _now.add(const Duration(minutes: 12)),
      status: 'completed',
    );
    return _harvestSession!;
  }

  @override
  Future<InventoryItem> createInventoryItem(
    TenantScope tenant, {
    required String partName,
    required String storageLocation,
    required PartCondition condition,
    required InventoryStatus status,
    String? sourceVehicleId,
    String? harvestSessionId,
  }) async {
    _record(tenant);
    _inventorySequence += 1;
    return InventoryItem(
      inventoryItemId: 'inventory-$_inventorySequence',
      inventoryCode: 'INV-${_inventorySequence.toString().padLeft(6, '0')}',
      partName: partName,
      sourceVehicleId: sourceVehicleId,
      harvestSessionId: harvestSessionId,
      storageLocationId: storageLocation,
      condition: condition,
      status: status,
      quantity: 1,
      estimatedValue: 225,
      createdAt: _now,
      updatedAt: _now,
    );
  }
}
