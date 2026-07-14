import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:recycleros_domain/recycleros_domain.dart';
import 'package:uuid/uuid.dart';

final rc1WorkflowProvider =
    StateNotifierProvider<Rc1WorkflowController, Rc1WorkflowState>(
  (ref) => Rc1WorkflowController(),
);

const procurementScenarios = <ProcurementScenario>[
  ProcurementScenario(
    intent: ProcurementIntent.resale,
    projectedRevenue: 9500.0,
    projectedCosts: 7550.0,
    recommendedMaxBid: 4800.0,
    projectedNetProfit: 1950.0,
    projectedMarginPercent: 20.5,
    confidenceScore: 72.0,
  ),
  ProcurementScenario(
    intent: ProcurementIntent.personalUse,
    projectedRevenue: 0.0,
    projectedCosts: 5300.0,
    recommendedMaxBid: 5300.0,
    projectedNetProfit: 0.0,
    projectedMarginPercent: 0.0,
    confidenceScore: 65.0,
  ),
  ProcurementScenario(
    intent: ProcurementIntent.partOut,
    projectedRevenue: 8500.0,
    projectedCosts: 5250.0,
    recommendedMaxBid: 3900.0,
    projectedNetProfit: 3250.0,
    projectedMarginPercent: 38.2,
    confidenceScore: 81.0,
  ),
];

class Rc1WorkflowState {
  const Rc1WorkflowState({
    this.userEmail,
    this.organizationId = 'org-local',
    this.organizationName = 'Effortless Smoke, LLC',
    this.workspaceId = 'workspace-local',
    this.workspaceName = 'RecyclerOS Operations',
    this.workspaceSelected = false,
    this.opportunities = const [],
    this.activeOpportunityId,
    this.activeVehicle,
    this.pickListItems = const [],
    this.harvestSession,
    this.selectedParts = const <String>{},
    this.inventoryItems = const [],
  });

  final String? userEmail;
  final String organizationId;
  final String organizationName;
  final String workspaceId;
  final String workspaceName;
  final bool workspaceSelected;
  final List<Opportunity> opportunities;
  final String? activeOpportunityId;
  final Vehicle? activeVehicle;
  final List<PickListItem> pickListItems;
  final HarvestSession? harvestSession;
  final Set<String> selectedParts;
  final List<InventoryItem> inventoryItems;

  Opportunity? get activeOpportunity {
    for (final opportunity in opportunities) {
      if (opportunity.opportunityId == activeOpportunityId) {
        return opportunity;
      }
    }
    return null;
  }

  Rc1WorkflowState copyWith({
    String? userEmail,
    bool? workspaceSelected,
    List<Opportunity>? opportunities,
    String? activeOpportunityId,
    Vehicle? activeVehicle,
    List<PickListItem>? pickListItems,
    HarvestSession? harvestSession,
    Set<String>? selectedParts,
    List<InventoryItem>? inventoryItems,
  }) {
    return Rc1WorkflowState(
      userEmail: userEmail ?? this.userEmail,
      organizationId: organizationId,
      organizationName: organizationName,
      workspaceId: workspaceId,
      workspaceName: workspaceName,
      workspaceSelected: workspaceSelected ?? this.workspaceSelected,
      opportunities: opportunities ?? this.opportunities,
      activeOpportunityId: activeOpportunityId ?? this.activeOpportunityId,
      activeVehicle: activeVehicle ?? this.activeVehicle,
      pickListItems: pickListItems ?? this.pickListItems,
      harvestSession: harvestSession ?? this.harvestSession,
      selectedParts: selectedParts ?? this.selectedParts,
      inventoryItems: inventoryItems ?? this.inventoryItems,
    );
  }
}

class Rc1WorkflowController extends StateNotifier<Rc1WorkflowState> {
  Rc1WorkflowController() : super(const Rc1WorkflowState());

  final Uuid _uuid = const Uuid();

  void signIn(String email) {
    state = state.copyWith(userEmail: email.trim());
  }

  void selectWorkspace() {
    state = state.copyWith(workspaceSelected: true);
  }

  Opportunity createOpportunity({
    required String title,
    String? vin,
    int? year,
    String? make,
    String? model,
  }) {
    final now = DateTime.now().toUtc();
    final sequence = state.opportunities.length + 1;
    final opportunity = Opportunity(
      opportunityId: _uuid.v4(),
      opportunityCode: 'OPP-${sequence.toString().padLeft(6, '0')}',
      title: title.trim(),
      source: OpportunitySource.manual,
      status: OpportunityStatus.discovered,
      procurementIntent: ProcurementIntent.partOut,
      vin: _clean(vin),
      year: year,
      make: _clean(make),
      model: _clean(model),
      estimatedMaxBid: 3900.0,
      estimatedNetProfit: 3250.0,
      confidenceScore: 81.0,
      createdAt: now,
      updatedAt: now,
    );
    state = state.copyWith(
      opportunities: [...state.opportunities, opportunity],
      activeOpportunityId: opportunity.opportunityId,
    );
    return opportunity;
  }

  Vehicle createVehicleRecord(String opportunityId) {
    if (state.activeVehicle != null &&
        state.activeOpportunityId == opportunityId) {
      return state.activeVehicle!;
    }

    final opportunity = state.opportunities.firstWhere(
      (item) => item.opportunityId == opportunityId,
    );
    final now = DateTime.now().toUtc();
    final vehicle = Vehicle(
      vehicleId: _uuid.v4(),
      vehicleCode: 'VEH-000001',
      vin: opportunity.vin,
      year: opportunity.year,
      make: opportunity.make,
      model: opportunity.model,
      mileage: 126000,
      lifecycleStatus: VehicleLifecycleStatus.evaluated,
      createdAt: now,
      updatedAt: now,
    );
    state = state.copyWith(
      activeOpportunityId: opportunityId,
      activeVehicle: vehicle,
    );
    return vehicle;
  }

  PickListItem addToPickList(String vehicleId) {
    for (final item in state.pickListItems) {
      if (item.vehicleId == vehicleId) {
        return item;
      }
    }

    final vehicle = state.activeVehicle!;
    final item = PickListItem(
      pickListItemId: _uuid.v4(),
      vehicleId: vehicleId,
      yardName: 'Greenville Pull-A-Part',
      row: '12',
      year: vehicle.year ?? DateTime.now().year,
      make: vehicle.make ?? 'Unknown',
      model: vehicle.model ?? 'Vehicle',
      vin: vehicle.vin,
      availabilityStatus: 'pending',
    );
    state = state.copyWith(pickListItems: [...state.pickListItems, item]);
    return item;
  }

  void setAvailability(String pickListItemId, String availabilityStatus) {
    final items = state.pickListItems.map((item) {
      if (item.pickListItemId != pickListItemId) {
        return item;
      }
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
    }).toList();
    state = state.copyWith(pickListItems: items);
  }

  HarvestSession startFocusPoint(String vehicleId) {
    final current = state.harvestSession;
    if (current != null &&
        current.vehicleId == vehicleId &&
        current.status == 'active') {
      return current;
    }

    final session = HarvestSession(
      harvestSessionId: _uuid.v4(),
      vehicleId: vehicleId,
      startedAt: DateTime.now().toUtc(),
      status: 'active',
    );
    state = state.copyWith(harvestSession: session);
    return session;
  }

  void togglePart(String partName, bool selected) {
    final parts = {...state.selectedParts};
    if (selected) {
      parts.add(partName);
    } else {
      parts.remove(partName);
    }
    state = state.copyWith(selectedParts: parts);
  }

  void completeFocusPoint() {
    final current = state.harvestSession;
    if (current == null) {
      return;
    }
    state = state.copyWith(
      harvestSession: HarvestSession(
        harvestSessionId: current.harvestSessionId,
        vehicleId: current.vehicleId,
        startedAt: current.startedAt,
        endedAt: DateTime.now().toUtc(),
        latitude: current.latitude,
        longitude: current.longitude,
        status: 'completed',
      ),
    );
  }

  InventoryItem createInventoryItem({
    required String partName,
    required String storageLocation,
    required PartCondition condition,
    required InventoryStatus status,
  }) {
    final now = DateTime.now().toUtc();
    final sequence = state.inventoryItems.length + 1;
    final item = InventoryItem(
      inventoryItemId: _uuid.v4(),
      inventoryCode: 'INV-${sequence.toString().padLeft(6, '0')}',
      partName: partName.trim(),
      sourceVehicleId: state.activeVehicle?.vehicleId,
      harvestSessionId: state.harvestSession?.harvestSessionId,
      storageLocationId: storageLocation.trim(),
      condition: condition,
      status: status,
      quantity: 1,
      estimatedValue: 225.0,
      createdAt: now,
      updatedAt: now,
    );
    state = state.copyWith(inventoryItems: [...state.inventoryItems, item]);
    return item;
  }

  static String? _clean(String? value) {
    final cleaned = value?.trim();
    return cleaned == null || cleaned.isEmpty ? null : cleaned;
  }
}
