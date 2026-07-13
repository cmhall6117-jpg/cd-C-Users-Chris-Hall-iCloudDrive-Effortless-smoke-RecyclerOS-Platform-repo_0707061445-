import 'package:flutter/material.dart';

class OpportunityDiscoveryScreen extends StatefulWidget {
  const OpportunityDiscoveryScreen({super.key});

  @override
  State<OpportunityDiscoveryScreen> createState() => _OpportunityDiscoveryScreenState();
}

class _OpportunityDiscoveryScreenState extends State<OpportunityDiscoveryScreen> {
  final titleController = TextEditingController();
  final vinController = TextEditingController();

  String procurementIntent = 'undecided';
  String sourceType = 'manual';

  @override
  void dispose() {
    titleController.dispose();
    vinController.dispose();
    super.dispose();
  }

  void saveOpportunity() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Opportunity saved locally. Sync pending.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final intents = ['undecided', 'resale', 'personalUse', 'partOut'];
    final sources = ['manual', 'salvageYard', 'nonDealerAuction', 'dealerAuction', 'privateSeller', 'marketplace'];

    return Scaffold(
      appBar: AppBar(title: const Text('Opportunity Discovery')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: saveOpportunity,
        icon: const Icon(Icons.save),
        label: const Text('Save'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Create Opportunity', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          TextField(
            controller: titleController,
            decoration: const InputDecoration(labelText: 'Opportunity Title', border: OutlineInputBorder()),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: vinController,
            decoration: const InputDecoration(
              labelText: 'VIN',
              border: OutlineInputBorder(),
              suffixIcon: Icon(Icons.qr_code_scanner),
            ),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: sourceType,
            decoration: const InputDecoration(labelText: 'Source Type', border: OutlineInputBorder()),
            items: sources.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
            onChanged: (value) => setState(() => sourceType = value ?? sourceType),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: procurementIntent,
            decoration: const InputDecoration(labelText: 'Procurement Intent', border: OutlineInputBorder()),
            items: intents.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
            onChanged: (value) => setState(() => procurementIntent = value ?? procurementIntent),
          ),
        ],
      ),
    );
  }
}
