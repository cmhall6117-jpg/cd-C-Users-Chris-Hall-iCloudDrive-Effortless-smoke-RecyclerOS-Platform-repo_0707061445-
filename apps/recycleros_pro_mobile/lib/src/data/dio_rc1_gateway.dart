import 'package:dio/dio.dart';
import 'package:recycleros_domain/recycleros_domain.dart';

import 'rc1_gateway.dart';

const rc1ApiBaseUrl = String.fromEnvironment(
  'RECYCLEROS_API_BASE_URL',
  defaultValue: 'http://127.0.0.1:8000',
);

class DioRc1Gateway implements Rc1Gateway {
  DioRc1Gateway({String baseUrl = rc1ApiBaseUrl, Dio? dio})
      : _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: baseUrl,
                connectTimeout: const Duration(seconds: 10),
                receiveTimeout: const Duration(seconds: 15),
                headers: const {'Accept': 'application/json'},
              ),
            );

  final Dio _dio;
  String? _accessToken;

  @override
  Future<AuthSession> signIn({
    required String email,
    required String password,
  }) async {
    final json = await _request(
      () => _dio.post<dynamic>(
        '/v1/auth/login',
        data: {'email': email, 'password': password},
      ),
    );
    _accessToken = json['access_token'] as String;
    return _authSession(json);
  }

  @override
  Future<Opportunity> createOpportunity(
    TenantScope tenant, {
    required String title,
    String? vin,
    int? year,
    String? make,
    String? model,
  }) async {
    final json = await _request(
      () => _dio.post<dynamic>(
        '/v1/opportunities',
        data: {
          'title': title,
          'source_type': 'manual',
          'procurement_intent': 'partOut',
          'vin': vin,
          'year': year,
          'make': make,
          'model': model,
          'estimated_max_bid': 3900.0,
          'estimated_net_profit': 3250.0,
          'confidence_score': 81.0,
        },
        options: _tenantOptions(tenant),
      ),
    );
    return _opportunity(json);
  }

  @override
  Future<Vehicle> createVehicle(
    TenantScope tenant, {
    required Opportunity opportunity,
  }) async {
    final json = await _request(
      () => _dio.post<dynamic>(
        '/v1/vehicles',
        data: {
          'opportunity_id': opportunity.opportunityId,
          'vin': opportunity.vin,
          'year': opportunity.year,
          'make': opportunity.make,
          'model': opportunity.model,
          'mileage': 126000,
        },
        options: _tenantOptions(tenant),
      ),
    );
    return _vehicle(json);
  }

  @override
  Future<List<ProcurementScenario>> getProcurementAnalysis(
    TenantScope tenant, {
    required String opportunityId,
  }) async {
    final json = await _request(
      () => _dio.get<dynamic>(
        '/v1/procurement/$opportunityId/analysis',
        options: _tenantOptions(tenant),
      ),
    );
    final scenarios = json['scenarios'] as List<dynamic>? ?? const [];
    return scenarios.map((item) => _scenario(_json(item))).toList();
  }

  @override
  Future<PickListItem> createPickListItem(
    TenantScope tenant, {
    required Vehicle vehicle,
  }) async {
    final json = await _request(
      () => _dio.post<dynamic>(
        '/v1/pick-list',
        data: {
          'vehicle_id': vehicle.vehicleId,
          'yard_name': 'Greenville Pull-A-Part',
          'yard_row': '12',
        },
        options: _tenantOptions(tenant),
      ),
    );
    return _pickListItem(json, vehicle);
  }

  @override
  Future<PickListItem> updatePickListAvailability(
    TenantScope tenant, {
    required PickListItem item,
    required String availabilityStatus,
  }) async {
    final json = await _request(
      () => _dio.patch<dynamic>(
        '/v1/pick-list/${item.pickListItemId}/availability',
        data: {'availability_status': availabilityStatus},
        options: _tenantOptions(tenant),
      ),
    );
    return _pickListItemFromExisting(json, item);
  }

  @override
  Future<HarvestSession> startFocusPoint(
    TenantScope tenant, {
    required String vehicleId,
  }) async {
    final json = await _request(
      () => _dio.post<dynamic>(
        '/v1/harvest/focus-point/start',
        queryParameters: {'vehicle_id': vehicleId},
        options: _tenantOptions(tenant),
      ),
    );
    return _harvestSession(json);
  }

  @override
  Future<HarvestSession> completeFocusPoint(
    TenantScope tenant, {
    required String harvestSessionId,
  }) async {
    final json = await _request(
      () => _dio.post<dynamic>(
        '/v1/harvest/focus-point/complete',
        queryParameters: {'harvest_session_id': harvestSessionId},
        options: _tenantOptions(tenant),
      ),
    );
    return _harvestSession(json);
  }

  @override
  Future<InventoryItem> createInventoryItem(
    TenantScope tenant, {
    required String partName,
    required String storageLocation,
    required PartCondition condition,
    required InventoryStatus status,
    String? sourceVehicleId,
    String? harvestSessionId,
  }) async {
    final json = await _request(
      () => _dio.post<dynamic>(
        '/v1/inventory',
        data: {
          'part_name': partName,
          'source_vehicle_id': sourceVehicleId,
          'harvest_session_id': harvestSessionId,
          'storage_location_id': storageLocation,
          'condition': condition.name,
          'status': status.name,
          'quantity': 1,
          'estimated_value': 225.0,
        },
        options: _tenantOptions(tenant),
      ),
    );
    return _inventoryItem(json);
  }

  Future<Map<String, dynamic>> _request(
    Future<Response<dynamic>> Function() send,
  ) async {
    try {
      final response = await send();
      return _json(response.data);
    } on DioException catch (error) {
      final data = error.response?.data;
      final detail = data is Map ? data['detail'] : null;
      throw Rc1GatewayException(
        detail is String ? detail : 'RecyclerOS API request failed.',
      );
    }
  }

  Options _tenantOptions(TenantScope tenant) {
    final accessToken = _accessToken;
    if (accessToken == null) {
      throw const Rc1GatewayException('Sign in before accessing RecyclerOS.');
    }
    return Options(
      headers: {
        ...tenant.headers,
        'Authorization': 'Bearer $accessToken',
      },
    );
  }

  static Map<String, dynamic> _json(dynamic value) {
    if (value is Map<String, dynamic>) {
      return value;
    }
    if (value is Map) {
      return Map<String, dynamic>.from(value);
    }
    throw const Rc1GatewayException('RecyclerOS API returned invalid data.');
  }

  static AuthSession _authSession(Map<String, dynamic> json) {
    final identity = _json(json['identity']);
    final memberships = identity['memberships'] as List<dynamic>? ?? const [];
    return AuthSession(
      userId: identity['user_id'] as String,
      email: identity['email'] as String,
      displayName: identity['display_name'] as String,
      expiresAt: DateTime.parse(json['expires_at'] as String),
      memberships: memberships.map((item) {
        final membership = _json(item);
        return TenantMembership(
          organizationId: membership['organization_id'] as String,
          organizationName: membership['organization_name'] as String,
          workspaceId: membership['workspace_id'] as String,
          workspaceName: membership['workspace_name'] as String,
          role: membership['role'] as String,
        );
      }).toList(),
    );
  }

  static Opportunity _opportunity(Map<String, dynamic> json) {
    final createdAt = DateTime.parse(json['created_at'] as String);
    return Opportunity(
      opportunityId: json['opportunity_id'] as String,
      opportunityCode: json['opportunity_code'] as String,
      title: json['title'] as String,
      source: OpportunitySource.values.byName(json['source_type'] as String),
      status: OpportunityStatus.values.byName(json['status'] as String),
      procurementIntent:
          ProcurementIntent.values.byName(json['procurement_intent'] as String),
      vin: json['vin'] as String?,
      year: json['year'] as int?,
      make: json['make'] as String?,
      model: json['model'] as String?,
      estimatedMaxBid: (json['estimated_max_bid'] as num?)?.toDouble(),
      estimatedNetProfit: (json['estimated_net_profit'] as num?)?.toDouble(),
      confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
      createdAt: createdAt,
      updatedAt: createdAt,
    );
  }

  static Vehicle _vehicle(Map<String, dynamic> json) {
    final createdAt = DateTime.parse(json['created_at'] as String);
    return Vehicle(
      vehicleId: json['vehicle_id'] as String,
      vehicleCode: json['vehicle_code'] as String,
      vin: json['vin'] as String?,
      year: json['year'] as int?,
      make: json['make'] as String?,
      model: json['model'] as String?,
      trim: json['trim'] as String?,
      engine: json['engine'] as String?,
      transmission: json['transmission'] as String?,
      drivetrain: json['drivetrain'] as String?,
      mileage: json['mileage'] as int?,
      lifecycleStatus: VehicleLifecycleStatus.values.byName(
        json['lifecycle_status'] as String,
      ),
      createdAt: createdAt,
      updatedAt: DateTime.parse(
        json['updated_at'] as String? ?? createdAt.toIso8601String(),
      ),
    );
  }

  static ProcurementScenario _scenario(Map<String, dynamic> json) {
    return ProcurementScenario(
      intent: ProcurementIntent.values.byName(json['intent'] as String),
      projectedRevenue: (json['projected_revenue'] as num).toDouble(),
      projectedCosts: (json['projected_costs'] as num).toDouble(),
      recommendedMaxBid: (json['recommended_max_bid'] as num).toDouble(),
      projectedNetProfit: (json['projected_net_profit'] as num).toDouble(),
      projectedMarginPercent:
          (json['projected_margin_percent'] as num).toDouble(),
      confidenceScore: (json['confidence_score'] as num).toDouble(),
    );
  }

  static PickListItem _pickListItem(
    Map<String, dynamic> json,
    Vehicle vehicle,
  ) {
    return PickListItem(
      pickListItemId: json['pick_list_item_id'] as String,
      vehicleId: json['vehicle_id'] as String,
      yardName: json['yard_name'] as String,
      row: json['yard_row'] as String? ?? '',
      year: vehicle.year ?? DateTime.now().year,
      make: vehicle.make ?? 'Unknown',
      model: vehicle.model ?? 'Vehicle',
      vin: vehicle.vin,
      availabilityStatus: json['availability_status'] as String,
    );
  }

  static PickListItem _pickListItemFromExisting(
    Map<String, dynamic> json,
    PickListItem item,
  ) {
    return PickListItem(
      pickListItemId: json['pick_list_item_id'] as String,
      vehicleId: json['vehicle_id'] as String,
      yardName: json['yard_name'] as String,
      row: json['yard_row'] as String? ?? item.row,
      year: item.year,
      make: item.make,
      model: item.model,
      vin: item.vin,
      availabilityStatus: json['availability_status'] as String,
    );
  }

  static HarvestSession _harvestSession(Map<String, dynamic> json) {
    return HarvestSession(
      harvestSessionId: json['harvest_session_id'] as String,
      vehicleId: json['vehicle_id'] as String,
      startedAt: DateTime.parse(json['started_at'] as String),
      endedAt: json['ended_at'] == null
          ? null
          : DateTime.parse(json['ended_at'] as String),
      status: json['status'] as String,
    );
  }

  static InventoryItem _inventoryItem(Map<String, dynamic> json) {
    return InventoryItem(
      inventoryItemId: json['inventory_item_id'] as String,
      inventoryCode: json['inventory_code'] as String,
      partName: json['part_name'] as String,
      sourceVehicleId: json['source_vehicle_id'] as String?,
      harvestSessionId: json['harvest_session_id'] as String?,
      storageLocationId: json['storage_location_id'] as String?,
      condition: PartCondition.values.byName(json['condition'] as String),
      status: InventoryStatus.values.byName(json['status'] as String),
      quantity: json['quantity'] as int,
      estimatedValue: (json['estimated_value'] as num?)?.toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}
