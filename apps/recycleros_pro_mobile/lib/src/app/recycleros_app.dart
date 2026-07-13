import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'app_routes.dart';

class RecyclerOSApp extends StatelessWidget {
  const RecyclerOSApp({super.key});

  @override
  Widget build(BuildContext context) {
    final router = GoRouter(routes: appRoutes);

    return MaterialApp.router(
      title: 'RecyclerOS Pro',
      theme: ThemeData(useMaterial3: true),
      routerConfig: router,
    );
  }
}
