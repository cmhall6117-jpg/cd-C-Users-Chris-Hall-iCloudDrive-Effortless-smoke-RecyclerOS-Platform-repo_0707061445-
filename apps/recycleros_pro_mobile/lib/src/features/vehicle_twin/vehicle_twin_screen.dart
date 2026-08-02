import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class VehicleTwinScreen extends ConsumerWidget {
  const VehicleTwinScreen({required this.vehicleCode, super.key});

  final String vehicleCode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(rc1WorkflowProvider);
    final vehicle = state.activeVehicle;
    if (vehicle == null || vehicle.vehicleCode != vehicleCode) {
      return Rc1Scaffold(
        title: 'Vehicle Record',
        body: Center(
          child: FilledButton.icon(
            onPressed: () => context.go(AppPaths.opportunities),
            icon: const Icon(Icons.arrow_back),
            label: const Text('Return to Opportunities'),
          ),
        ),
      );
    }

    final opportunity = state.activeOpportunity;
    final vehicleName = [vehicle.year, vehicle.make, vehicle.model]
        .where((value) => value != null && value.toString().isNotEmpty)
        .join(' ');
    final timeline = <(IconData, String, String)>[
      (Icons.radar, 'Opportunity discovered', opportunity?.opportunityCode ?? '-'),
      (Icons.fact_check_outlined, 'Vehicle evaluated', vehicle.vehicleCode),
    ];

    return Rc1Scaffold(
      title: 'Vehicle Record',
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          PageHeader(
            title: vehicleName.isEmpty ? vehicle.vehicleCode : vehicleName,
            detail: vehicle.vehicleCode,
          ),
          const SizedBox(height: 20),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _VehicleFact(label: 'VIN', value: vehicle.vin ?? 'Pending'),
              _VehicleFact(
                label: 'Mileage',
                value: vehicle.mileage?.toString() ?? 'Pending',
              ),
              _VehicleFact(
                label: 'Lifecycle',
                value: _label(vehicle.lifecycleStatus.name),
              ),
              _VehicleFact(
                label: 'Intent',
                value: _label(opportunity?.procurementIntent.name ?? 'undecided'),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'Timeline',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          for (final item in timeline)
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(item.$1),
              title: Text(item.$2),
              subtitle: Text(item.$3),
            ),
          const SizedBox(height: 20),
          FilledButton.icon(
            key: const Key('vehicleContinue'),
            onPressed: opportunity == null
                ? null
                : () => context.go(
                      AppPaths.procurement(opportunity.opportunityId),
                    ),
            icon: const Icon(Icons.calculate_outlined),
            label: const Text('Open Procurement'),
          ),
        ],
      ),
    );
  }

  static String _label(String value) {
    return value.replaceAllMapped(
      RegExp(r'([a-z])([A-Z])'),
      (match) => '${match.group(1)} ${match.group(2)}',
    );
  }
}

class _VehicleFact extends StatelessWidget {
  const _VehicleFact({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Container(
      width: 200,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: colors.surface,
        border: Border.all(color: colors.outlineVariant),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 4),
          Text(
            value,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}
