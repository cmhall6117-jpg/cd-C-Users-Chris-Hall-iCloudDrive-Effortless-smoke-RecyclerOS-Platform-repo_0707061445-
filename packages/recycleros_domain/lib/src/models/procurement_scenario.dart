import 'procurement_intent.dart';

class ProcurementScenario {
  final ProcurementIntent intent;
  final double projectedRevenue;
  final double projectedCosts;
  final double recommendedMaxBid;
  final double projectedNetProfit;
  final double projectedMarginPercent;
  final double confidenceScore;

  const ProcurementScenario({
    required this.intent,
    required this.projectedRevenue,
    required this.projectedCosts,
    required this.recommendedMaxBid,
    required this.projectedNetProfit,
    required this.projectedMarginPercent,
    required this.confidenceScore,
  });
}
