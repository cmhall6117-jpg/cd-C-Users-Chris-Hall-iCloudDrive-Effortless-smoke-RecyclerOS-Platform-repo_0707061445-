class BusinessEvent {
  final String eventId;
  final String eventType;
  final String objectId;
  final String createdBy;
  final DateTime occurredAt;
  final Map<String, dynamic> payload;

  const BusinessEvent({
    required this.eventId,
    required this.eventType,
    required this.objectId,
    required this.createdBy,
    required this.occurredAt,
    required this.payload,
  });
}
