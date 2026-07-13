import 'package:flutter/material.dart';

class OpportunityDiscoveryScreen extends StatelessWidget {
  const OpportunityDiscoveryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Opportunity Discovery')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          Text('Create or research acquisition opportunities.', style: TextStyle(fontSize: 20)),
          SizedBox(height: 16),
          Card(child: ListTile(title: Text('VIN Search'), subtitle: Text('Decode vehicle and evaluate procurement intent.'))),
          Card(child: ListTile(title: Text('Auction Opportunity'), subtitle: Text('Compare resale, personal use, and part-out scenarios.'))),
          Card(child: ListTile(title: Text('Salvage Yard Lead'), subtitle: Text('Create pick opportunity from yard inventory.'))),
        ],
      ),
    );
  }
}
