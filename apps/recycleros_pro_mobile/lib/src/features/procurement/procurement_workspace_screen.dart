import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:recycleros_domain/recycleros_domain.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class ProcurementWorkspaceScreen extends ConsumerStatefulWidget {
  const ProcurementWorkspaceScreen({required this.opportunityId, super.key});

  final String opportunityId;

  @override
  ConsumerState<ProcurementWorkspaceScreen> createState() =>
      _ProcurementWorkspaceScreenState();
}

class _ProcurementWorkspaceScreenState
    extends ConsumerState<ProcurementWorkspaceScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (mounted) {
        await ref
            .read(rc1WorkflowProvider.notifier)
            .loadProcurementAnalysis(widget.opportunityId);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rc1WorkflowProvider);
    Opportunity? opportunity;
    for (final item in state.opportunities) {
      if (item.opportunityId == widget.opportunityId) {
        opportunity = item;
        break;
      }
    }
    final vehicle = state.activeVehicle;

    if (opportunity == null) {
      return Rc1Scaffold(
        title: 'Procurement',
        body: Center(
          child: FilledButton.icon(
            onPressed: () => context.go(AppPaths.opportunities),
            icon: const Icon(Icons.arrow_back),
            label: const Text('Return to Opportunities'),
          ),
        ),
      );
    }

    final currency = NumberFormat.simpleCurrency(decimalDigits: 0);
    return Rc1Scaffold(
      title: 'Procurement',
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          PageHeader(
            title: opportunity.title,
            detail: '${opportunity.opportunityCode}  |  Non-dealer public',
          ),
          const SizedBox(height: 20),
          if (state.isBusy && state.procurementScenarios.isEmpty)
            const Center(child: CircularProgressIndicator()),
          if (state.errorMessage != null &&
              state.procurementScenarios.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 20),
              child: Text(
                state.errorMessage!,
                textAlign: TextAlign.center,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ),
          for (final scenario in state.procurementScenarios)
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          scenario.intent == ProcurementIntent.partOut
                              ? Icons.recommend_outlined
                              : Icons.calculate_outlined,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            _intentLabel(scenario.intent),
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(fontWeight: FontWeight.w700),
                          ),
                        ),
                        if (scenario.intent == ProcurementIntent.partOut)
                          const Icon(
                            Icons.check_circle,
                            color: Color(0xFF1F5C4A),
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 20,
                      runSpacing: 8,
                      children: [
                        Text(
                          'Max bid ${currency.format(scenario.recommendedMaxBid)}',
                        ),
                        Text(
                          'Net ${currency.format(scenario.projectedNetProfit)}',
                        ),
                        Text('Confidence ${scenario.confidenceScore.toInt()}%'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 16),
          FilledButton.icon(
            key: const Key('procurementApprove'),
            onPressed: vehicle == null ||
                    state.isBusy ||
                    state.procurementScenarios.isEmpty
                ? null
                : () async {
                    final item = await ref
                        .read(rc1WorkflowProvider.notifier)
                        .addToPickList(vehicle!.vehicleId);
                    if (!context.mounted) {
                      return;
                    }
                    if (item != null) {
                      context.go(AppPaths.pickList);
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            ref.read(rc1WorkflowProvider).errorMessage ??
                                'Pick-list item could not be created.',
                          ),
                        ),
                      );
                    }
                  },
            icon: const Icon(Icons.playlist_add_check),
            label: const Text('Approve Part-Out and Add to Pick List'),
          ),
        ],
      ),
    );
  }

  static String _intentLabel(ProcurementIntent intent) {
    return switch (intent) {
      ProcurementIntent.resale => 'Resale',
      ProcurementIntent.personalUse => 'Personal Use',
      ProcurementIntent.partOut => 'Part-Out',
      ProcurementIntent.undecided => 'Undecided',
    };
  }
}
