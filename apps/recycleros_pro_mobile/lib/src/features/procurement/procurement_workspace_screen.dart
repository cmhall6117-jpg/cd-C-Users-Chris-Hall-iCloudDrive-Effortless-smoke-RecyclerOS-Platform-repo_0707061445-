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
  ProcurementIntent? _selectedIntent;

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
    final recommendedIntent = _recommendedIntent(state.procurementScenarios);
    final selectedIntent = _selectedIntent ??
        (opportunity.procurementIntent == ProcurementIntent.undecided
            ? recommendedIntent
            : opportunity.procurementIntent);
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
          RadioGroup<ProcurementIntent>(
            groupValue: selectedIntent,
            onChanged: (value) {
              if (value != null && state.canOperate && !state.isBusy) {
                setState(() {
                  _selectedIntent = value;
                });
              }
            },
            child: Column(
              children: [
                for (final scenario in state.procurementScenarios)
                  Card(
                    color: scenario.intent == selectedIntent
                        ? Theme.of(context).colorScheme.primaryContainer
                        : null,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: BorderSide(
                        color: scenario.intent == selectedIntent
                            ? Theme.of(context).colorScheme.primary
                            : Theme.of(context).colorScheme.outlineVariant,
                        width: scenario.intent == selectedIntent ? 2 : 1,
                      ),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: InkWell(
                      key: ValueKey(
                        'procurementOption-${scenario.intent.name}',
                      ),
                      onTap: state.canOperate && !state.isBusy
                          ? () => setState(() {
                                _selectedIntent = scenario.intent;
                              })
                          : null,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Radio<ProcurementIntent>(
                                  value: scenario.intent,
                                  enabled:
                                      state.canOperate && !state.isBusy,
                                ),
                                const SizedBox(width: 4),
                                Expanded(
                                  child: Text(
                                    _intentLabel(scenario.intent),
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleMedium
                                        ?.copyWith(
                                          fontWeight: FontWeight.w700,
                                        ),
                                  ),
                                ),
                                if (scenario.intent == recommendedIntent)
                                  const Tooltip(
                                    message: 'Recommended outcome',
                                    child: Icon(Icons.recommend_outlined),
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
                                Text(
                                  'Confidence ${scenario.confidenceScore.toInt()}%',
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            key: const Key('procurementApprove'),
            onPressed: vehicle == null ||
                    state.isBusy ||
                    !state.canOperate ||
                    selectedIntent == null
                ? null
                : () => _approveSelection(
                      context,
                      opportunity!,
                      vehicle,
                      selectedIntent,
                    ),
            icon: Icon(
              selectedIntent == ProcurementIntent.partOut
                  ? Icons.playlist_add_check
                  : Icons.check_circle_outline,
            ),
            label: Text(_approvalLabel(selectedIntent)),
          ),
        ],
      ),
    );
  }

  static String _intentLabel(ProcurementIntent intent) {
    return switch (intent) {
      ProcurementIntent.resale => 'Sell Whole (Resale)',
      ProcurementIntent.personalUse => 'Personal Buy / Use',
      ProcurementIntent.partOut => 'Part Out',
      ProcurementIntent.undecided => 'Undecided',
    };
  }

  static String _approvalLabel(ProcurementIntent? intent) {
    return switch (intent) {
      ProcurementIntent.resale => 'Approve Sell Whole',
      ProcurementIntent.personalUse => 'Approve Personal Buy / Use',
      ProcurementIntent.partOut => 'Approve Part Out and Add to Pick List',
      ProcurementIntent.undecided || null => 'Select an Outcome',
    };
  }

  static ProcurementIntent? _recommendedIntent(
    List<ProcurementScenario> scenarios,
  ) {
    ProcurementScenario? recommended;
    for (final scenario in scenarios) {
      if (recommended == null ||
          scenario.confidenceScore > recommended.confidenceScore) {
        recommended = scenario;
      }
    }
    return recommended?.intent;
  }

  Future<void> _approveSelection(
    BuildContext context,
    Opportunity opportunity,
    Vehicle vehicle,
    ProcurementIntent intent,
  ) async {
    final controller = ref.read(rc1WorkflowProvider.notifier);
    final updated = await controller.updateProcurementDecision(
      opportunity.opportunityId,
      intent,
    );
    if (!context.mounted) {
      return;
    }
    if (updated == null) {
      _showError(context, 'Procurement outcome could not be saved.');
      return;
    }

    if (intent != ProcurementIntent.partOut) {
      context.go(AppPaths.vehicle(vehicle.vehicleCode));
      return;
    }

    final item = await controller.addToPickList(vehicle.vehicleId);
    if (!context.mounted) {
      return;
    }
    if (item != null) {
      context.go(AppPaths.pickList);
    } else {
      _showError(context, 'Pick-list item could not be created.');
    }
  }

  void _showError(BuildContext context, String fallback) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ref.read(rc1WorkflowProvider).errorMessage ?? fallback,
        ),
      ),
    );
  }
}
