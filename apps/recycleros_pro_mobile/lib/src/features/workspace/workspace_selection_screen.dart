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
            detail: state.displayName ?? state.userEmail ?? 'RecyclerOS user',
          ),
          const SizedBox(height: 20),
          for (var index = 0; index < state.memberships.length; index++)
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              child: ListTile(
                key: index == 0
                    ? const Key('workspaceTile')
                    : ValueKey(
                        'workspace-${state.memberships[index].workspaceId}',
                      ),
                contentPadding: const EdgeInsets.all(16),
                leading: const Icon(Icons.warehouse_outlined),
                title: Text(state.memberships[index].workspaceName),
                subtitle: Text(
                  '${state.memberships[index].organizationName}  |  '
                  '${_roleLabel(state.memberships[index].role)}',
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  ref
                      .read(rc1WorkflowProvider.notifier)
                      .selectWorkspace(state.memberships[index]);
                  context.go(AppPaths.missionControl);
                },
              ),
            ),
          if (state.memberships.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Text('No workspace access is assigned.'),
            ),
        ],
      ),
    );
  }

  static String _roleLabel(String role) {
    return '${role[0].toUpperCase()}${role.substring(1)}';
  }
}
