import 'package:flutter/material.dart';

class VehicleTwinScreen extends StatelessWidget {
  const VehicleTwinScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final timeline = [
      ('Opportunity Discovered', 'Auction lead created'),
      ('Vehicle Evaluated', 'VIN decoded and procurement intent assigned'),
      ('Vehicle Received', 'Vehicle received into active asset inventory'),
      ('Focus Point Started', 'Harvest session opened'),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Vehicle Digital Twin')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('2019 Ford F-150', style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('VIN: Pending scan'),
          const Text('Lifecycle Status: Active Harvest'),
          const Text('Procurement Intent: Part-Out'),
          const SizedBox(height: 16),
          const Card(
            child: ListTile(
              leading: Icon(Icons.analytics),
              title: Text('Recovery Summary'),
              subtitle: Text('Estimated value, harvested value, remaining value, and scrap value will appear here.'),
            ),
          ),
          const SizedBox(height: 16),
          const Text('Vehicle Timeline', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          for (final item in timeline)
            Card(
              child: ListTile(
                leading: const Icon(Icons.timeline),
                title: Text(item.$1),
                subtitle: Text(item.$2),
              ),
            ),
        ],
      ),
    );
  }
}
