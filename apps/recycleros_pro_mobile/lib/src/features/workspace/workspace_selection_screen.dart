import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class WorkspaceSelectionScreen extends ConsumerWidget {
  const WorkspaceSelectionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(rc1WorkflowProvider);

    return Rc1Scaffold(
      title: 'Select Workspace',
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          PageHeader(
            title: state.organizationName,
            detail: state.userEmail ?? 'Local RC1 user',
          ),
          const SizedBox(height: 20),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            child: ListTile(
              key: const Key('workspaceTile'),
              contentPadding: const EdgeInsets.all(16),
              leading: const Icon(Icons.warehouse_outlined),
              title: Text(state.workspaceName),
              subtitle: const Text('Primary workspace'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                ref.read(rc1WorkflowProvider.notifier).selectWorkspace();
                context.go(AppPaths.missionControl);
              },
            ),
          ),
        ],
      ),
    );
  }
}
