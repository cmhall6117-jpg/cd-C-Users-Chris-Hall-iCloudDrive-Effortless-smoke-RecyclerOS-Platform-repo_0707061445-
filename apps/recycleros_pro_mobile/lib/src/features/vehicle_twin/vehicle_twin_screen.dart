import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:recycleros_domain/recycleros_domain.dart';

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
                onEdit: state.canOperate && !state.isBusy
                    ? () => _editMileage(context, ref, vehicle)
                    : null,
              ),
              _VehicleFact(
                label: 'Lifecycle',
                value: _label(vehicle.lifecycleStatus.name),
              ),
              _VehicleFact(
                label: 'Intent',
                value: _intentLabel(
                  opportunity?.procurementIntent ??
                      ProcurementIntent.undecided,
                ),
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

  static Future<void> _editMileage(
    BuildContext context,
    WidgetRef ref,
    Vehicle vehicle,
  ) async {
    final mileage = await showDialog<int>(
      context: context,
      builder: (_) => _MileageDialog(
        initialMileage: vehicle.mileage,
      ),
    );
    if (mileage == null || !context.mounted) {
      return;
    }

    final updated = await ref
        .read(rc1WorkflowProvider.notifier)
        .updateVehicleMileage(vehicle.vehicleId, mileage);
    if (!context.mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          updated == null
              ? ref.read(rc1WorkflowProvider).errorMessage ??
                  'Mileage could not be updated.'
              : 'Mileage updated to $mileage mi.',
        ),
      ),
    );
  }

  static String _intentLabel(ProcurementIntent intent) {
    return switch (intent) {
      ProcurementIntent.resale => 'Sell Whole',
      ProcurementIntent.personalUse => 'Personal Buy / Use',
      ProcurementIntent.partOut => 'Part Out',
      ProcurementIntent.undecided => 'Undecided',
    };
  }

  static String _label(String value) {
    final label = value.replaceAllMapped(
      RegExp(r'([a-z])([A-Z])'),
      (match) => '${match.group(1)} ${match.group(2)}',
    );
    return label.isEmpty
        ? label
        : '${label[0].toUpperCase()}${label.substring(1)}';
  }
}

class _MileageDialog extends StatefulWidget {
  const _MileageDialog({required this.initialMileage});

  final int? initialMileage;

  @override
  State<_MileageDialog> createState() => _MileageDialogState();
}

class _MileageDialogState extends State<_MileageDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: widget.initialMileage?.toString() ?? '',
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Update Mileage'),
      content: Form(
        key: _formKey,
        child: TextFormField(
          key: const Key('vehicleMileageField'),
          controller: _controller,
          autofocus: true,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: 'Current mileage',
            suffixText: 'mi',
          ),
          validator: (value) {
            final parsed = int.tryParse(value?.trim() ?? '');
            if (parsed == null || parsed < 0) {
              return 'Enter a valid mileage.';
            }
            return null;
          },
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(
          key: const Key('vehicleMileageSave'),
          onPressed: () {
            if (_formKey.currentState?.validate() ?? false) {
              Navigator.of(context).pop(
                int.parse(_controller.text.trim()),
              );
            }
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}

class _VehicleFact extends StatelessWidget {
  const _VehicleFact({
    required this.label,
    required this.value,
    this.onEdit,
  });

  final String label;
  final String value;
  final VoidCallback? onEdit;

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
          Row(
            children: [
              Expanded(
                child: Text(
                  label,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
              if (onEdit != null)
                IconButton(
                  key: const Key('vehicleMileageEdit'),
                  onPressed: onEdit,
                  icon: const Icon(Icons.edit_outlined),
                  tooltip: 'Edit mileage',
                  visualDensity: VisualDensity.compact,
                ),
            ],
          ),
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
