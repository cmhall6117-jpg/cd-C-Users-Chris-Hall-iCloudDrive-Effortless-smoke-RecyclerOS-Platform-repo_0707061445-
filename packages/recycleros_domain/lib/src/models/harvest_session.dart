class HarvestSession {
  final String harvestSessionId;
  final String vehicleId;
  final DateTime startedAt;
  final DateTime? endedAt;
  final double? latitude;
  final double? longitude;
  final String status;

  const HarvestSession({
    required this.harvestSessionId,
    required this.vehicleId,
    required this.startedAt,
    this.endedAt,
    this.latitude,
    this.longitude,
    required this.status,
  });
}
