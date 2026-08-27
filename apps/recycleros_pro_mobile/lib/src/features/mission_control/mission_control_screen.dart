import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class MissionControlScreen extends ConsumerWidget {
  const MissionControlScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(rc1WorkflowProvider);
    final vehicle = state.activeVehicle;
    final opportunity = state.activeOpportunity;
    final actions = <_MissionAction>[
      _MissionAction(
        key: const Key('missionOpportunity'),
        icon: Icons.travel_explore,
        title: 'Opportunity Discovery',
        detail: '${state.opportunities.length} active',
        location: AppPaths.opportunities,
      ),
      _MissionAction(
        icon: Icons.directions_car_outlined,
        title: 'Vehicle Record',
        detail: vehicle?.vehicleCode ?? 'No active vehicle',
        location: vehicle == null ? null : AppPaths.vehicle(vehicle.vehicleCode),
      ),
      _MissionAction(
        icon: Icons.calculate_outlined,
        title: 'Procurement',
        detail: opportunity?.opportunityCode ?? 'No active analysis',
        location: opportunity == null
            ? null
            : AppPaths.procurement(opportunity.opportunityId),
      ),
      _MissionAction(
        icon: Icons.format_list_bulleted,
        title: 'Pick List',
        detail: '${state.pickListItems.length} queued',
        location: state.pickListItems.isEmpty ? null : AppPaths.pickList,
      ),
      _MissionAction(
        icon: Icons.inventory_2_outlined,
        title: 'Inventory Intake',
        detail: '${state.inventoryItems.length} created',
        location: AppPaths.inventoryIntake,
      ),
    ];

    return Rc1Scaffold(
      title: 'Mission Control',
      actions: [
        IconButton(
          key: const Key('signOut'),
          tooltip: 'Sign out',
          onPressed: state.isBusy
              ? null
              : () async {
                  final signedOut = await ref
                      .read(rc1WorkflowProvider.notifier)
                      .logout();
                  if (!context.mounted) {
                    return;
                  }
                  if (signedOut) {
                    context.go(AppPaths.login);
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                          ref.read(rc1WorkflowProvider).errorMessage ??
                              'Sign out failed.',
                        ),
                      ),
                    );
                  }
                },
          icon: const Icon(Icons.logout),
        ),
      ],
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          PageHeader(
            title: state.workspaceName,
            detail: state.organizationName,
          ),
          const SizedBox(height: 20),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _Metric(
                label: 'Opportunities',
                value: '${state.opportunities.length}',
                icon: Icons.radar,
              ),
              _Metric(
                label: 'Pick List',
                value: '${state.pickListItems.length}',
                icon: Icons.checklist,
              ),
              _Metric(
                label: 'Inventory',
                value: '${state.inventoryItems.length}',
                icon: Icons.inventory_2_outlined,
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'Operations',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          for (final action in actions)
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              child: ListTile(
                key: action.key,
                enabled: action.location != null,
                leading: Icon(action.icon),
                title: Text(action.title),
                subtitle: Text(action.detail),
                trailing: const Icon(Icons.chevron_right),
                onTap: action.location == null
                    ? null
                    : () => context.go(action.location!),
              ),
            ),
        ],
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value, required this.icon});

  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Container(
      width: 180,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colors.surface,
        border: Border.all(color: colors.outlineVariant),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, color: colors.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(value, style: Theme.of(context).textTheme.titleLarge),
                Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MissionAction {
  const _MissionAction({
    required this.icon,
    required this.title,
    required this.detail,
    required this.location,
    this.key,
  });

  final Key? key;
  final IconData icon;
  final String title;
  final String detail;
  final String? location;
}
