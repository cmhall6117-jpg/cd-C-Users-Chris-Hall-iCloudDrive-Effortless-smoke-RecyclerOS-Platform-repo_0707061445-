import 'package:go_router/go_router.dart';

import '../features/auth/login_screen.dart';
import '../features/focus_point/focus_point_screen.dart';
import '../features/inventory/inventory_intake_screen.dart';
import '../features/mission_control/mission_control_screen.dart';
import '../features/opportunity_discovery/opportunity_discovery_screen.dart';
import '../features/pick_list/pick_list_screen.dart';
import '../features/procurement/procurement_workspace_screen.dart';
import '../features/vehicle_twin/vehicle_twin_screen.dart';
import '../features/workspace/workspace_selection_screen.dart';

abstract final class AppPaths {
  static const login = '/';
  static const workspace = '/workspace-select';
  static const missionControl = '/mission-control';
  static const opportunities = '/opportunities';
  static const pickList = '/pick-list';
  static const inventoryIntake = '/inventory/intake';

  static String vehicle(String vehicleCode) => '/vehicles/$vehicleCode';
  static String procurement(String opportunityId) =>
      '/procurement/$opportunityId';
  static String focusPoint(String vehicleId) => '/focus-point/$vehicleId';
}

final appRoutes = <RouteBase>[
  GoRoute(path: AppPaths.login, builder: (_, __) => const LoginScreen()),
  GoRoute(
    path: AppPaths.workspace,
    builder: (_, __) => const WorkspaceSelectionScreen(),
  ),
  GoRoute(
    path: AppPaths.missionControl,
    builder: (_, __) => const MissionControlScreen(),
  ),
  GoRoute(
    path: AppPaths.opportunities,
    builder: (_, __) => const OpportunityDiscoveryScreen(),
  ),
  GoRoute(
    path: '/vehicles/:vehicleCode',
    builder: (_, state) => VehicleTwinScreen(
      vehicleCode: state.pathParameters['vehicleCode']!,
    ),
  ),
  GoRoute(
    path: '/procurement/:opportunityId',
    builder: (_, state) => ProcurementWorkspaceScreen(
      opportunityId: state.pathParameters['opportunityId']!,
    ),
  ),
  GoRoute(path: AppPaths.pickList, builder: (_, __) => const PickListScreen()),
  GoRoute(
    path: '/focus-point/:vehicleId',
    builder: (_, state) => FocusPointScreen(
      vehicleId: state.pathParameters['vehicleId']!,
    ),
  ),
  GoRoute(
    path: AppPaths.inventoryIntake,
    builder: (_, __) => const InventoryIntakeScreen(),
  ),
];
