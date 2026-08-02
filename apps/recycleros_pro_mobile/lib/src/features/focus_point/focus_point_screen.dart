import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class FocusPointScreen extends ConsumerStatefulWidget {
  const FocusPointScreen({required this.vehicleId, super.key});

  final String vehicleId;

  @override
  ConsumerState<FocusPointScreen> createState() => _FocusPointScreenState();
}

class _FocusPointScreenState extends ConsumerState<FocusPointScreen> {
  static const parts = [
    'ECM / PCM',
    'Transmission',
    'LED Headlights',
    'Instrument Cluster',
    'Tailgate',
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (mounted) {
        await ref
            .read(rc1WorkflowProvider.notifier)
            .startFocusPoint(widget.vehicleId);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rc1WorkflowProvider);
    final vehicle = state.activeVehicle;
    final session = state.harvestSession;
    final matchingItems = state.pickListItems
        .where((entry) => entry.vehicleId == widget.vehicleId)
        .toList();
    final item = matchingItems.isEmpty ? null : matchingItems.first;

    if (vehicle == null ||
        vehicle.vehicleId != widget.vehicleId ||
        item == null) {
      return Rc1Scaffold(
        title: 'Focus Point',
        body: Center(
          child: FilledButton.icon(
            onPressed: () => context.go(AppPaths.pickList),
            icon: const Icon(Icons.arrow_back),
            label: const Text('Return to Pick List'),
          ),
        ),
      );
    }

    return Rc1Scaffold(
      title: 'Focus Point',
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          PageHeader(
            title: '${item.year} ${item.make} ${item.model}',
            detail: '${item.yardName}  |  Row ${item.row}',
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: Theme.of(context).colorScheme.outlineVariant,
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.timer_outlined),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        session?.status == 'active'
                            ? 'KPI timer active'
                            : 'Starting session',
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.w700),
                      ),
                      Text('Yard and row confirmed'),
                    ],
                  ),
                ),
                const Icon(Icons.location_on_outlined),
              ],
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'Available Parts',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          for (final part in parts)
            CheckboxListTile(
              key: ValueKey('part-$part'),
              contentPadding: EdgeInsets.zero,
              title: Text(part),
              value: state.selectedParts.contains(part),
              onChanged: state.canOperate
                  ? (value) => ref
                      .read(rc1WorkflowProvider.notifier)
                      .togglePart(part, value ?? false)
                  : null,
            ),
          const SizedBox(height: 12),
          FilledButton.icon(
            key: const Key('completeFocus'),
            onPressed: state.selectedParts.isEmpty ||
                    state.isBusy ||
                    !state.canOperate
                ? null
                : () async {
                    final session = await ref
                        .read(rc1WorkflowProvider.notifier)
                        .completeFocusPoint();
                    if (!context.mounted) {
                      return;
                    }
                    if (session != null) {
                      context.go(AppPaths.inventoryIntake);
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            ref.read(rc1WorkflowProvider).errorMessage ??
                                'Focus Point could not be completed.',
                          ),
                        ),
                      );
                    }
                  },
            icon: const Icon(Icons.check),
            label: const Text('Complete Focus Point'),
          ),
          const SizedBox(height: 8),
          TextButton.icon(
            onPressed: () => context.go(AppPaths.pickList),
            icon: const Icon(Icons.arrow_back),
            label: const Text('Back to Pick List'),
          ),
        ],
      ),
    );
  }
}
