import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class OpportunityDiscoveryScreen extends StatelessWidget {
  const OpportunityDiscoveryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Opportunity Discovery')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Create or research acquisition opportunities.', style: TextStyle(fontSize: 20)),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              title: const Text('VIN Search'),
              subtitle: const Text('Decode vehicle and evaluate procurement intent.'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.go('/vehicles/VEH-000001'),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text('Auction Opportunity'),
              subtitle: const Text('Compare resale, personal use, and part-out scenarios.'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.go('/procurement/OPP-DEMO-000001'),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text('Salvage Yard Lead'),
              subtitle: const Text('Create pick opportunity from yard inventory.'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.go('/pick-list'),
            ),
          ),
        ],
      ),
    );
  }
}
