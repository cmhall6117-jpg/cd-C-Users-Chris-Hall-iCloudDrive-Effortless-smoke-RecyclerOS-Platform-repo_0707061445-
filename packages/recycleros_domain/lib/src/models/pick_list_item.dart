class PickListItem {
  final String pickListItemId;
  final String vehicleId;
  final String yardName;
  final String row;
  final int year;
  final String make;
  final String model;
  final String? vin;
  final String availabilityStatus;

  const PickListItem({
    required this.pickListItemId,
    required this.vehicleId,
    required this.yardName,
    required this.row,
    required this.year,
    required this.make,
    required this.model,
    this.vin,
    required this.availabilityStatus,
  });
}
