import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class MissionControlScreen extends StatelessWidget {
  const MissionControlScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final actions = [
      ('Opportunity Discovery', '/opportunities'),
      ('Vehicle Record', '/vehicles/VEH-000001'),
      ('Procurement', '/procurement/OPP-DEMO-000001'),
      ('Pick List', '/pick-list'),
      ('Inventory Intake', '/inventory/intake'),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('RecyclerOS Pro Mission Control')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Today''s Priorities', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          for (final action in actions)
            Card(
              child: ListTile(
                title: Text(action.$1),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go(action.$2),
              ),
            ),
        ],
      ),
    );
  }
}
