import 'package:recycleros_domain/recycleros_domain.dart';

class TenantMembership {
  const TenantMembership({
    required this.organizationId,
    required this.organizationName,
    required this.workspaceId,
    required this.workspaceName,
    required this.role,
  });

  final String organizationId;
  final String organizationName;
  final String workspaceId;
  final String workspaceName;
  final String role;
}

class AuthSession {
  const AuthSession({
    required this.userId,
    required this.email,
    required this.displayName,
    required this.expiresAt,
    required this.memberships,
  });

  final String userId;
  final String email;
  final String displayName;
  final DateTime expiresAt;
  final List<TenantMembership> memberships;
}

class TenantScope {
  const TenantScope({
    required this.organizationId,
    required this.workspaceId,
  });

  final String organizationId;
  final String workspaceId;

  Map<String, String> get headers => {
        'X-Organization-ID': organizationId,
        'X-Workspace-ID': workspaceId,
      };
}

abstract interface class Rc1Gateway {
  Future<AuthSession> signIn({
    required String email,
    required String password,
  });

  Future<Opportunity> createOpportunity(
    TenantScope tenant, {
    required String title,
    String? vin,
    int? year,
    String? make,
    String? model,
  });

  Future<Vehicle> createVehicle(
    TenantScope tenant, {
    required Opportunity opportunity,
  });

  Future<List<ProcurementScenario>> getProcurementAnalysis(
    TenantScope tenant, {
    required String opportunityId,
  });

  Future<PickListItem> createPickListItem(
    TenantScope tenant, {
    required Vehicle vehicle,
  });

  Future<PickListItem> updatePickListAvailability(
    TenantScope tenant, {
    required PickListItem item,
    required String availabilityStatus,
  });

  Future<HarvestSession> startFocusPoint(
    TenantScope tenant, {
    required String vehicleId,
  });

  Future<HarvestSession> completeFocusPoint(
    TenantScope tenant, {
    required String harvestSessionId,
  });

  Future<InventoryItem> createInventoryItem(
    TenantScope tenant, {
    required String partName,
    required String storageLocation,
    required PartCondition condition,
    required InventoryStatus status,
    String? sourceVehicleId,
    String? harvestSessionId,
  });
}

class Rc1GatewayException implements Exception {
  const Rc1GatewayException(this.message);

  final String message;

  @override
  String toString() => message;
}
