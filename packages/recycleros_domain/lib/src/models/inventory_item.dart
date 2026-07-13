import 'inventory_status.dart';
import 'part_condition.dart';

class InventoryItem {
  final String inventoryItemId;
  final String inventoryCode;
  final String partName;
  final String? sourceVehicleId;
  final String? harvestSessionId;
  final String? storageLocationId;
  final PartCondition condition;
  final InventoryStatus status;
  final int quantity;
  final double? estimatedValue;
  final DateTime createdAt;
  final DateTime updatedAt;

  const InventoryItem({
    required this.inventoryItemId,
    required this.inventoryCode,
    required this.partName,
    this.sourceVehicleId,
    this.harvestSessionId,
    this.storageLocationId,
    required this.condition,
    required this.status,
    required this.quantity,
    this.estimatedValue,
    required this.createdAt,
    required this.updatedAt,
  });
}
