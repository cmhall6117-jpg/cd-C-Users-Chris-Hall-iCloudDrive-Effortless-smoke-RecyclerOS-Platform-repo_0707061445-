import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../state/rc1_workflow.dart';
import 'app_routes.dart';
import 'app_theme.dart';

class RecyclerOSApp extends ConsumerStatefulWidget {
  const RecyclerOSApp({super.key, this.initialLocation});

  final String? initialLocation;

  @override
  ConsumerState<RecyclerOSApp> createState() => _RecyclerOSAppState();
}

class _RecyclerOSAppState extends ConsumerState<RecyclerOSApp> {
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    _router = GoRouter(
      initialLocation: widget.initialLocation,
      routes: appRoutes,
      redirect: (_, routerState) {
        final workflow = ref.read(rc1WorkflowProvider);
        final location = routerState.matchedLocation;
        final expiresAt = workflow.sessionExpiresAt;
        final signedIn = workflow.userId != null &&
            (expiresAt == null || expiresAt.isAfter(DateTime.now()));

        if (!signedIn) {
          return location == AppPaths.login ? null : AppPaths.login;
        }
        if (location == AppPaths.login) {
          return workflow.workspaceSelected
              ? AppPaths.missionControl
              : AppPaths.workspace;
        }
        if (!workflow.workspaceSelected && location != AppPaths.workspace) {
          return AppPaths.workspace;
        }
        return null;
      },
    );
  }

  @override
  void dispose() {
    _router.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'RecyclerOS Pro',
      debugShowCheckedModeBanner: false,
      theme: buildRecyclerOSTheme(),
      routerConfig: _router,
    );
  }
}
