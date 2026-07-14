import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class PickListScreen extends ConsumerWidget {
  const PickListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(rc1WorkflowProvider);

    return Rc1Scaffold(
      title: 'Pick List',
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          PageHeader(
            title: 'Yard Queue',
            detail: '${state.pickListItems.length} vehicle queued',
          ),
          const SizedBox(height: 20),
          if (state.pickListItems.isEmpty)
            Center(
              child: FilledButton.icon(
                onPressed: () => context.go(AppPaths.opportunities),
                icon: const Icon(Icons.add),
                label: const Text('Create Opportunity'),
              ),
            ),
          for (final item in state.pickListItems)
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${item.year} ${item.make} ${item.model}',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 4),
                    Text('${item.yardName}  |  Row ${item.row}'),
                    Text('VIN ${item.vin ?? 'Pending'}'),
                    const SizedBox(height: 16),
                    SegmentedButton<String>(
                      key: ValueKey('availability-${item.pickListItemId}'),
                      emptySelectionAllowed: true,
                      showSelectedIcon: false,
                      segments: const [
                        ButtonSegment(
                          value: 'available',
                          icon: Icon(Icons.check_circle_outline),
                          label: Text('Available'),
                        ),
                        ButtonSegment(
                          value: 'unavailable',
                          icon: Icon(Icons.block),
                          label: Text('Unavailable'),
                        ),
                      ],
                      selected: item.availabilityStatus == 'pending'
                          ? const <String>{}
                          : <String>{item.availabilityStatus},
                      onSelectionChanged: (selection) {
                        if (selection.isEmpty) {
                          return;
                        }
                        ref.read(rc1WorkflowProvider.notifier).setAvailability(
                              item.pickListItemId,
                              selection.first,
                            );
                      },
                    ),
                    const SizedBox(height: 16),
                    Align(
                      alignment: Alignment.centerRight,
                      child: FilledButton.icon(
                        key: ValueKey('openFocus-${item.pickListItemId}'),
                        onPressed: item.availabilityStatus == 'available'
                            ? () => context.go(
                                  AppPaths.focusPoint(item.vehicleId),
                                )
                            : null,
                        icon: const Icon(Icons.timer_outlined),
                        label: const Text('Open Focus Point'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
