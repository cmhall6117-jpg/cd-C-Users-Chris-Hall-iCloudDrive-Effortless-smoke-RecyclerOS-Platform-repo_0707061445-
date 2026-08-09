import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:recycleros_domain/recycleros_domain.dart';

import '../data/dio_rc1_gateway.dart';
import '../data/rc1_gateway.dart';

final rc1GatewayProvider = Provider<Rc1Gateway>((ref) => DioRc1Gateway());

final rc1WorkflowProvider =
    StateNotifierProvider<Rc1WorkflowController, Rc1WorkflowState>(
  (ref) => Rc1WorkflowController(ref.watch(rc1GatewayProvider)),
);

class Rc1WorkflowState {
  const Rc1WorkflowState({
    this.userId,
    this.userEmail,
    this.displayName,
    this.sessionExpiresAt,
    this.memberships = const [],
    this.organizationId = '',
    this.organizationName = '',
    this.workspaceId = '',
    this.workspaceName = '',
    this.workspaceRole = '',
    this.workspaceSelected = false,
    this.opportunities = const [],
    this.activeOpportunityId,
    this.activeVehicle,
    this.procurementScenarios = const [],
    this.pickListItems = const [],
    this.harvestSession,
    this.selectedParts = const <String>{},
    this.inventoryItems = const [],
    this.isBusy = false,
    this.errorMessage,
  });

  final String? userId;
  final String? userEmail;
  final String? displayName;
  final DateTime? sessionExpiresAt;
  final List<TenantMembership> memberships;
  final String organizationId;
  final String organizationName;
  final String workspaceId;
  final String workspaceName;
  final String workspaceRole;
  final bool workspaceSelected;
  final List<Opportunity> opportunities;
  final String? activeOpportunityId;
  final Vehicle? activeVehicle;
  final List<ProcurementScenario> procurementScenarios;
  final List<PickListItem> pickListItems;
  final HarvestSession? harvestSession;
  final Set<String> selectedParts;
  final List<InventoryItem> inventoryItems;
  final bool isBusy;
  final String? errorMessage;

  Opportunity? get activeOpportunity {
    for (final opportunity in opportunities) {
      if (opportunity.opportunityId == activeOpportunityId) {
        return opportunity;
      }
    }
    return null;
  }

  bool get canOperate => const {
        'owner',
        'admin',
        'operator',
      }.contains(workspaceRole);

  TenantScope get tenant => TenantScope(
        organizationId: organizationId,
        workspaceId: workspaceId,
      );

  Rc1WorkflowState copyWith({
    String? userId,
    String? userEmail,
    String? displayName,
    DateTime? sessionExpiresAt,
    List<TenantMembership>? memberships,
    String? organizationId,
    String? organizationName,
    String? workspaceId,
    String? workspaceName,
    String? workspaceRole,
    bool? workspaceSelected,
    List<Opportunity>? opportunities,
    String? activeOpportunityId,
    Vehicle? activeVehicle,
    List<ProcurementScenario>? procurementScenarios,
    List<PickListItem>? pickListItems,
    HarvestSession? harvestSession,
    Set<String>? selectedParts,
    List<InventoryItem>? inventoryItems,
    bool? isBusy,
    String? errorMessage,
    bool clearError = false,
  }) {
    return Rc1WorkflowState(
      userId: userId ?? this.userId,
      userEmail: userEmail ?? this.userEmail,
      displayName: displayName ?? this.displayName,
      sessionExpiresAt: sessionExpiresAt ?? this.sessionExpiresAt,
      memberships: memberships ?? this.memberships,
      organizationId: organizationId ?? this.organizationId,
      organizationName: organizationName ?? this.organizationName,
      workspaceId: workspaceId ?? this.workspaceId,
      workspaceName: workspaceName ?? this.workspaceName,
      workspaceRole: workspaceRole ?? this.workspaceRole,
      workspaceSelected: workspaceSelected ?? this.workspaceSelected,
      opportunities: opportunities ?? this.opportunities,
      activeOpportunityId: activeOpportunityId ?? this.activeOpportunityId,
      activeVehicle: activeVehicle ?? this.activeVehicle,
      procurementScenarios:
          procurementScenarios ?? this.procurementScenarios,
      pickListItems: pickListItems ?? this.pickListItems,
      harvestSession: harvestSession ?? this.harvestSession,
      selectedParts: selectedParts ?? this.selectedParts,
      inventoryItems: inventoryItems ?? this.inventoryItems,
      isBusy: isBusy ?? this.isBusy,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}

class Rc1WorkflowController extends StateNotifier<Rc1WorkflowState> {
  Rc1WorkflowController(this._gateway) : super(const Rc1WorkflowState());

  final Rc1Gateway _gateway;

  Future<AuthSession?> signIn(String email, String password) async {
    _startRequest();
    try {
      final session = await _gateway.signIn(
        email: email.trim(),
        password: password,
      );
      if (session.memberships.isEmpty) {
        throw const Rc1GatewayException(
          'This account has no RecyclerOS workspace access.',
        );
      }
      final firstMembership = session.memberships.first;
      state = state.copyWith(
        userId: session.userId,
        userEmail: session.email,
        displayName: session.displayName,
        sessionExpiresAt: session.expiresAt,
        memberships: session.memberships,
        organizationId: firstMembership.organizationId,
        organizationName: firstMembership.organizationName,
        workspaceId: firstMembership.workspaceId,
        workspaceName: firstMembership.workspaceName,
        workspaceRole: firstMembership.role,
        workspaceSelected: false,
        isBusy: false,
        clearError: true,
      );
      return session;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
  }

  void selectWorkspace(TenantMembership membership) {
    state = state.copyWith(
      organizationId: membership.organizationId,
      organizationName: membership.organizationName,
      workspaceId: membership.workspaceId,
      workspaceName: membership.workspaceName,
      workspaceRole: membership.role,
      workspaceSelected: true,
    );
  }

  Future<Opportunity?> createOpportunity({
    required String title,
    String? vin,
    int? year,
    String? make,
    String? model,
  }) async {
    _startRequest();
    try {
      final opportunity = await _gateway.createOpportunity(
        state.tenant,
        title: title.trim(),
        vin: _clean(vin),
        year: year,
        make: _clean(make),
        model: _clean(model),
      );
      state = state.copyWith(
        opportunities: [...state.opportunities, opportunity],
        activeOpportunityId: opportunity.opportunityId,
        procurementScenarios: const [],
        isBusy: false,
        clearError: true,
      );
      return opportunity;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
  }

  Future<Vehicle?> createVehicleRecord(String opportunityId) async {
    if (state.activeVehicle != null &&
        state.activeOpportunityId == opportunityId) {
      return state.activeVehicle;
    }

    final opportunity = state.opportunities.firstWhere(
      (item) => item.opportunityId == opportunityId,
    );
    _startRequest();
    try {
      final vehicle = await _gateway.createVehicle(
        state.tenant,
        opportunity: opportunity,
      );
      state = state.copyWith(
        activeOpportunityId: opportunityId,
        activeVehicle: vehicle,
        isBusy: false,
        clearError: true,
      );
      return vehicle;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
  }

  Future<List<ProcurementScenario>?> loadProcurementAnalysis(
    String opportunityId,
  ) async {
    _startRequest();
    try {
      final scenarios = await _gateway.getProcurementAnalysis(
        state.tenant,
        opportunityId: opportunityId,
      );
      state = state.copyWith(
        procurementScenarios: scenarios,
        isBusy: false,
        clearError: true,
      );
      return scenarios;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
  }

  Future<PickListItem?> addToPickList(String vehicleId) async {
    for (final item in state.pickListItems) {
      if (item.vehicleId == vehicleId) {
        return item;
      }
    }

    final vehicle = state.activeVehicle;
    if (vehicle == null || vehicle.vehicleId != vehicleId) {
      _failRequest(const Rc1GatewayException('Vehicle record is not active.'));
      return null;
    }

    _startRequest();
    try {
      final item = await _gateway.createPickListItem(
        state.tenant,
        vehicle: vehicle,
      );
      state = state.copyWith(
        pickListItems: [...state.pickListItems, item],
        isBusy: false,
        clearError: true,
      );
      return item;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
  }

  Future<PickListItem?> setAvailability(
    String pickListItemId,
    String availabilityStatus,
  ) async {
    final item = state.pickListItems.firstWhere(
      (entry) => entry.pickListItemId == pickListItemId,
    );
    _startRequest();
    try {
      final updated = await _gateway.updatePickListAvailability(
        state.tenant,
        item: item,
        availabilityStatus: availabilityStatus,
      );
      state = state.copyWith(
        pickListItems: [
          for (final current in state.pickListItems)
            if (current.pickListItemId == pickListItemId) updated else current,
        ],
        isBusy: false,
        clearError: true,
      );
      return updated;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
  }

  Future<HarvestSession?> startFocusPoint(String vehicleId) async {
    final current = state.harvestSession;
    if (current != null &&
        current.vehicleId == vehicleId &&
        current.status == 'active') {
      return current;
    }

    _startRequest();
    try {
      final session = await _gateway.startFocusPoint(
        state.tenant,
        vehicleId: vehicleId,
      );
      state = state.copyWith(
        harvestSession: session,
        isBusy: false,
        clearError: true,
      );
      return session;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
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

  Future<HarvestSession?> completeFocusPoint() async {
    final current = state.harvestSession;
    if (current == null) {
      _failRequest(const Rc1GatewayException('Harvest session is not active.'));
      return null;
    }

    _startRequest();
    try {
      final session = await _gateway.completeFocusPoint(
        state.tenant,
        harvestSessionId: current.harvestSessionId,
      );
      state = state.copyWith(
        harvestSession: session,
        isBusy: false,
        clearError: true,
      );
      return session;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
  }

  Future<InventoryItem?> createInventoryItem({
    required String partName,
    required String storageLocation,
    required PartCondition condition,
    required InventoryStatus status,
  }) async {
    _startRequest();
    try {
      final item = await _gateway.createInventoryItem(
        state.tenant,
        partName: partName.trim(),
        storageLocation: storageLocation.trim(),
        condition: condition,
        status: status,
        sourceVehicleId: state.activeVehicle?.vehicleId,
        harvestSessionId: state.harvestSession?.harvestSessionId,
      );
      state = state.copyWith(
        inventoryItems: [...state.inventoryItems, item],
        isBusy: false,
        clearError: true,
      );
      return item;
    } on Object catch (error) {
      _failRequest(error);
      return null;
    }
  }

  void _startRequest() {
    state = state.copyWith(isBusy: true, clearError: true);
  }

  void _failRequest(Object error) {
    state = state.copyWith(
      isBusy: false,
      errorMessage: error.toString(),
    );
  }

  static String? _clean(String? value) {
    final cleaned = value?.trim();
    return cleaned == null || cleaned.isEmpty ? null : cleaned;
  }
}
