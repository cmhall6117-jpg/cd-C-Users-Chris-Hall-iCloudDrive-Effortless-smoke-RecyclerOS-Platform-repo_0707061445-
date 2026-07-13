import 'procurement_intent.dart';
import 'opportunity_source.dart';
import 'opportunity_status.dart';

class Opportunity {
  final String opportunityId;
  final String opportunityCode;
  final String title;
  final OpportunitySource source;
  final OpportunityStatus status;
  final ProcurementIntent procurementIntent;
  final String? vin;
  final int? year;
  final String? make;
  final String? model;
  final double? estimatedMaxBid;
  final double? estimatedNetProfit;
  final double? confidenceScore;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Opportunity({
    required this.opportunityId,
    required this.opportunityCode,
    required this.title,
    required this.source,
    required this.status,
    required this.procurementIntent,
    this.vin,
    this.year,
    this.make,
    this.model,
    this.estimatedMaxBid,
    this.estimatedNetProfit,
    this.confidenceScore,
    required this.createdAt,
    required this.updatedAt,
  });
}
