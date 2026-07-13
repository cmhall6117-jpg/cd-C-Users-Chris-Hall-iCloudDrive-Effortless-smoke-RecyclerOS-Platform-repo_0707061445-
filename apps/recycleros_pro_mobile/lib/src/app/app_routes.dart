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

final appRoutes = <RouteBase>[
  GoRoute(path: '/', builder: (_, __) => const LoginScreen()),
  GoRoute(path: '/workspace-select', builder: (_, __) => const WorkspaceSelectionScreen()),
  GoRoute(path: '/mission-control', builder: (_, __) => const MissionControlScreen()),
  GoRoute(path: '/opportunities', builder: (_, __) => const OpportunityDiscoveryScreen()),
  GoRoute(path: '/vehicles/:vehicleCode', builder: (_, __) => const VehicleTwinScreen()),
  GoRoute(path: '/procurement/:opportunityId', builder: (_, __) => const ProcurementWorkspaceScreen()),
  GoRoute(path: '/pick-list', builder: (_, __) => const PickListScreen()),
  GoRoute(path: '/focus-point/:vehicleId', builder: (_, __) => const FocusPointScreen()),
  GoRoute(path: '/inventory/intake', builder: (_, __) => const InventoryIntakeScreen()),
];
