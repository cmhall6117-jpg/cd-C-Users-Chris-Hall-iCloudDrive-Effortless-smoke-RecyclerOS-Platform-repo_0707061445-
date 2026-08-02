import 'package:recycleros_domain/recycleros_domain.dart';

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
