import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:recycleros_domain/recycleros_domain.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class InventoryIntakeScreen extends ConsumerStatefulWidget {
  const InventoryIntakeScreen({super.key});

  @override
  ConsumerState<InventoryIntakeScreen> createState() =>
      _InventoryIntakeScreenState();
}

class _InventoryIntakeScreenState
    extends ConsumerState<InventoryIntakeScreen> {
  final _formKey = GlobalKey<FormState>();
  final _partNameController = TextEditingController();
  final _locationController = TextEditingController(text: 'A-12');
  PartCondition _condition = PartCondition.usedUntested;
  InventoryStatus _status = InventoryStatus.available;
  String? _lastInventoryCode;

  @override
  void initState() {
    super.initState();
    final selectedParts = ref.read(rc1WorkflowProvider).selectedParts;
    if (selectedParts.isNotEmpty) {
      _partNameController.text = selectedParts.first;
    }
  }

  @override
  void dispose() {
    _partNameController.dispose();
    _locationController.dispose();
    super.dispose();
  }

  Future<void> _saveInventory() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    final item = await ref
        .read(rc1WorkflowProvider.notifier)
        .createInventoryItem(
          partName: _partNameController.text,
          storageLocation: _locationController.text,
          condition: _condition,
          status: _status,
        );
    if (!mounted) {
      return;
    }
    if (item == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            ref.read(rc1WorkflowProvider).errorMessage ??
                'Inventory could not be created.',
          ),
        ),
      );
      return;
    }
    setState(() => _lastInventoryCode = item.inventoryCode);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('${item.inventoryCode} saved.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rc1WorkflowProvider);

    return Rc1Scaffold(
      title: 'Inventory Intake',
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
          PageHeader(
            title: 'Create Inventory Item',
            detail: '${state.inventoryItems.length} item created this session',
          ),
          const SizedBox(height: 20),
          Form(
            key: _formKey,
            child: Column(
              children: [
                TextFormField(
                  key: const Key('inventoryPartName'),
                  controller: _partNameController,
                  decoration: const InputDecoration(
                    labelText: 'Part Name',
                    prefixIcon: Icon(Icons.settings_outlined),
                  ),
                  validator: (value) => (value ?? '').trim().isEmpty
                      ? 'Enter a part name.'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  key: const Key('inventoryLocation'),
                  controller: _locationController,
                  decoration: const InputDecoration(
                    labelText: 'Storage Location',
                    prefixIcon: Icon(Icons.location_on_outlined),
                    suffixIcon: Icon(Icons.qr_code_scanner),
                  ),
                  validator: (value) => (value ?? '').trim().isEmpty
                      ? 'Enter a storage location.'
                      : null,
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<PartCondition>(
                  initialValue: _condition,
                  decoration: const InputDecoration(labelText: 'Condition'),
                  items: PartCondition.values
                      .map(
                        (condition) => DropdownMenuItem(
                          value: condition,
                          child: Text(_label(condition.name)),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _condition = value);
                    }
                  },
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<InventoryStatus>(
                  initialValue: _status,
                  decoration: const InputDecoration(labelText: 'Inventory Status'),
                  items: InventoryStatus.values
                      .map(
                        (status) => DropdownMenuItem(
                          value: status,
                          child: Text(_label(status.name)),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _status = value);
                    }
                  },
                ),
                const SizedBox(height: 16),
                Align(
                  alignment: Alignment.centerRight,
                  child: FilledButton.icon(
                    key: const Key('createInventory'),
                    onPressed: state.isBusy ? null : _saveInventory,
                    icon: const Icon(Icons.inventory_2_outlined),
                    label: const Text('Create Inventory'),
                  ),
                ),
              ],
            ),
          ),
          if (_lastInventoryCode != null) ...[
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle_outline),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      '$_lastInventoryCode ready for sync',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.w700),
                    ),
                  ),
                ],
              ),
            ),
          ],
          if (state.inventoryItems.isNotEmpty) ...[
            const SizedBox(height: 24),
            Text(
              'Session Inventory',
              style: Theme.of(context)
                  .textTheme
                  .titleLarge
                  ?.copyWith(fontWeight: FontWeight.w700),
            ),
            for (final item in state.inventoryItems)
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.inventory_2_outlined),
                title: Text(item.partName),
                subtitle: Text(
                  '${item.inventoryCode}  |  ${item.storageLocationId}',
                ),
              ),
          ],
        ],
      ),
    );
  }

  static String _label(String value) {
    final spaced = value.replaceAllMapped(
      RegExp(r'([a-z])([A-Z])'),
      (match) => '${match.group(1)} ${match.group(2)}',
    );
    return '${spaced[0].toUpperCase()}${spaced.substring(1)}';
  }
}
