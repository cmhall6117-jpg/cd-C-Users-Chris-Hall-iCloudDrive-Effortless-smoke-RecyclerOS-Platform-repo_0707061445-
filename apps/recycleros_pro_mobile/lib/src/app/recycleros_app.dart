import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'app_routes.dart';
import 'app_theme.dart';

class RecyclerOSApp extends StatefulWidget {
  const RecyclerOSApp({super.key});

  @override
  State<RecyclerOSApp> createState() => _RecyclerOSAppState();
}

class _RecyclerOSAppState extends State<RecyclerOSApp> {
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    _router = GoRouter(routes: appRoutes);
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
