import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class OpportunityDiscoveryScreen extends ConsumerStatefulWidget {
  const OpportunityDiscoveryScreen({super.key});

  @override
  ConsumerState<OpportunityDiscoveryScreen> createState() =>
      _OpportunityDiscoveryScreenState();
}

class _OpportunityDiscoveryScreenState
    extends ConsumerState<OpportunityDiscoveryScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _vinController = TextEditingController();
  final _yearController = TextEditingController();
  final _makeController = TextEditingController();
  final _modelController = TextEditingController();

  @override
  void dispose() {
    _titleController.dispose();
    _vinController.dispose();
    _yearController.dispose();
    _makeController.dispose();
    _modelController.dispose();
    super.dispose();
  }

  Future<void> _createOpportunity() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    final opportunity = await ref
        .read(rc1WorkflowProvider.notifier)
        .createOpportunity(
          title: _titleController.text,
          vin: _vinController.text,
          year: int.tryParse(_yearController.text),
          make: _makeController.text,
          model: _modelController.text,
        );
    if (!mounted) {
      return;
    }
    FocusScope.of(context).unfocus();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          opportunity == null
              ? ref.read(rc1WorkflowProvider).errorMessage ??
                  'Opportunity could not be created.'
              : '${opportunity.opportunityCode} created.',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rc1WorkflowProvider);

    return Rc1Scaffold(
      title: 'Opportunity Discovery',
      actions: [
        IconButton(
          tooltip: 'Mission Control',
          onPressed: () => context.go(AppPaths.missionControl),
          icon: const Icon(Icons.dashboard_outlined),
        ),
      ],
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const PageHeader(title: 'New Opportunity', detail: 'Manual acquisition lead'),
          const SizedBox(height: 20),
          Form(
            key: _formKey,
            child: Column(
              children: [
                TextFormField(
                  key: const Key('opportunityTitle'),
                  controller: _titleController,
                  textInputAction: TextInputAction.next,
                  decoration: const InputDecoration(
                    labelText: 'Opportunity Title',
                    prefixIcon: Icon(Icons.label_outline),
                  ),
                  validator: (value) => (value ?? '').trim().isEmpty
                      ? 'Enter an opportunity title.'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  key: const Key('opportunityVin'),
                  controller: _vinController,
                  textCapitalization: TextCapitalization.characters,
                  decoration: const InputDecoration(
                    labelText: 'VIN',
                    prefixIcon: Icon(Icons.qr_code_scanner),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        key: const Key('opportunityYear'),
                        controller: _yearController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(labelText: 'Year'),
                        validator: (value) {
                          final year = int.tryParse(value ?? '');
                          return year == null || year < 1886 || year > 2100
                              ? 'Valid year required.'
                              : null;
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        key: const Key('opportunityMake'),
                        controller: _makeController,
                        decoration: const InputDecoration(labelText: 'Make'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextFormField(
                  key: const Key('opportunityModel'),
                  controller: _modelController,
                  decoration: const InputDecoration(labelText: 'Model'),
                ),
                const SizedBox(height: 16),
                Align(
                  alignment: Alignment.centerRight,
                  child: FilledButton.icon(
                    key: const Key('createOpportunity'),
                    onPressed: state.isBusy ? null : _createOpportunity,
                    icon: const Icon(Icons.add),
                    label: const Text('Create Opportunity'),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 16),
          Text(
            'Active Opportunities',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          if (state.opportunities.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Text('No opportunities created.'),
            ),
          for (final opportunity in state.opportunities)
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
                      opportunity.title,
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${opportunity.opportunityCode}  |  '
                      '${opportunity.year ?? '-'} ${opportunity.make ?? ''} '
                      '${opportunity.model ?? ''}',
                    ),
                    const SizedBox(height: 12),
                    Align(
                      alignment: Alignment.centerRight,
                      child: FilledButton.tonalIcon(
                        key: ValueKey(
                          'createVehicle-${opportunity.opportunityCode}',
                        ),
                        onPressed: state.isBusy
                            ? null
                            : () async {
                                final vehicle = await ref
                              .read(rc1WorkflowProvider.notifier)
                              .createVehicleRecord(opportunity.opportunityId);
                                if (!context.mounted) {
                                  return;
                                }
                                if (vehicle != null) {
                                  context.go(
                                    AppPaths.vehicle(vehicle.vehicleCode),
                                  );
                                } else {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        ref
                                                .read(rc1WorkflowProvider)
                                                .errorMessage ??
                                            'Vehicle could not be created.',
                                      ),
                                    ),
                                  );
                                }
                              },
                        icon: const Icon(Icons.directions_car_outlined),
                        label: const Text('Create Vehicle Record'),
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
