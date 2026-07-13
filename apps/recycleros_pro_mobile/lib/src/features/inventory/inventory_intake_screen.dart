import 'package:flutter/material.dart';

class InventoryIntakeScreen extends StatefulWidget {
  const InventoryIntakeScreen({super.key});

  @override
  State<InventoryIntakeScreen> createState() => _InventoryIntakeScreenState();
}

class _InventoryIntakeScreenState extends State<InventoryIntakeScreen> {
  final partNameController = TextEditingController();
  final locationController = TextEditingController();
  String condition = 'usedUntested';
  String status = 'available';

  @override
  void dispose() {
    partNameController.dispose();
    locationController.dispose();
    super.dispose();
  }

  void saveInventory() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Inventory item saved locally. Sync pending.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final conditions = ['unknown', 'core', 'usedUntested', 'usedTested', 'refurbished', 'damaged'];
    final statuses = ['available', 'reserved', 'listed', 'sold', 'returned', 'scrapped', 'lost'];

    return Scaffold(
      appBar: AppBar(title: const Text('Inventory Intake')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: saveInventory,
        icon: const Icon(Icons.inventory),
        label: const Text('Create Inventory'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Create Inventory Item', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          TextField(
            controller: partNameController,
            decoration: const InputDecoration(labelText: 'Part Name', border: OutlineInputBorder()),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: locationController,
            decoration: const InputDecoration(
              labelText: 'Storage Location',
              border: OutlineInputBorder(),
              suffixIcon: Icon(Icons.qr_code_scanner),
            ),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: condition,
            decoration: const InputDecoration(labelText: 'Condition', border: OutlineInputBorder()),
            items: conditions.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
            onChanged: (value) => setState(() => condition = value ?? condition),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: status,
            decoration: const InputDecoration(labelText: 'Inventory Status', border: OutlineInputBorder()),
            items: statuses.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
            onChanged: (value) => setState(() => status = value ?? status),
          ),
          const SizedBox(height: 16),
          const Card(
            child: ListTile(
              leading: Icon(Icons.event_note),
              title: Text('Event Created'),
              subtitle: Text('EVT-010 Inventory Created'),
            ),
          )
        ],
      ),
    );
  }
}
