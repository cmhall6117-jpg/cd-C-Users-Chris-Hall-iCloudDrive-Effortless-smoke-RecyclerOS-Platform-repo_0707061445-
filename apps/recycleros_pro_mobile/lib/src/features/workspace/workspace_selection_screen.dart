import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class WorkspaceSelectionScreen extends StatelessWidget {
  const WorkspaceSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Select Workspace')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Effortless Smoke, LLC', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              leading: const Icon(Icons.store),
              title: const Text('RecyclerOS Operations'),
              subtitle: const Text('Primary RC1 workspace'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.go('/mission-control'),
            ),
          ),
        ],
      ),
    );
  }
}
