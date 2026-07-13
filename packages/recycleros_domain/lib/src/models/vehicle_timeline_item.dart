class VehicleTimelineItem {
  final String eventId;
  final String eventType;
  final String title;
  final String? description;
  final DateTime occurredAt;
  final String? createdBy;

  const VehicleTimelineItem({
    required this.eventId,
    required this.eventType,
    required this.title,
    this.description,
    required this.occurredAt,
    this.createdBy,
  });
}
