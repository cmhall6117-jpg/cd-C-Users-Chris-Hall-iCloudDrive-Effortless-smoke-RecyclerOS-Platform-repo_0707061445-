import 'package:flutter/material.dart';

class ProcurementWorkspaceScreen extends StatelessWidget {
  const ProcurementWorkspaceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final scenarios = [
      ('Resale', 'Max Bid: \$4,800', 'Projected Net: \$1,950'),
      ('Personal Use', 'Max Value: \$5,300', 'Value-focused'),
      ('Part-Out', 'Max Bid: \$3,900', 'Projected Net: \$3,250'),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Procurement Workspace')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Procurement Analysis', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('Auction Access: Non-Dealer Public'),
          const Text('Vehicle: 2019 Ford F-150'),
          const SizedBox(height: 16),
          for (final scenario in scenarios)
            Card(
              child: ListTile(
                leading: const Icon(Icons.calculate),
                title: Text(scenario.$1),
                subtitle: Text('${scenario.$2} • ${scenario.$3}'),
                trailing: const Icon(Icons.chevron_right),
              ),
            ),
        ],
      ),
    );
  }
}
