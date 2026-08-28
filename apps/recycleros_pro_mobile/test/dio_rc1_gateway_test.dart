import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:recycleros_domain/recycleros_domain.dart';
import 'package:recycleros_pro_mobile/src/data/dio_rc1_gateway.dart';
import 'package:recycleros_pro_mobile/src/data/rc1_gateway.dart';

void main() {
  test('sends tenant headers and maps a backend-created opportunity', () async {
    final capturedRequests = <RequestOptions>[];
    final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000'));
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          capturedRequests.add(options);
          if (options.path == '/v1/auth/login') {
            handler.resolve(
              Response<dynamic>(
                requestOptions: options,
                statusCode: 200,
                data: {
                  'access_token': 'opaque-session-token',
                  'token_type': 'bearer',
                  'expires_at': '2026-07-14T20:00:00Z',
                  'identity': {
                    'user_id': 'user-local',
                    'email': 'operator@effortlesssmoke.com',
                    'display_name': 'Local Operator',
                    'memberships': [
                      {
                        'organization_id': 'org-local',
                        'organization_name': 'Effortless Smoke, LLC',
                        'workspace_id': 'workspace-local',
                        'workspace_name': 'RecyclerOS Operations',
                        'role': 'operator',
                      },
                    ],
                  },
                },
              ),
            );
            return;
          }
          handler.resolve(
            Response<dynamic>(
              requestOptions: options,
              statusCode: 201,
              data: {
                'opportunity_id': 'opportunity-api-id',
                'opportunity_code': 'OPP-000001',
                'title': '2019 Ford F-150 auction lead',
                'source_type': 'manual',
                'status': 'discovered',
                'procurement_intent': 'partOut',
                'vin': '1FTFW1E50KFA00001',
                'year': 2019,
                'make': 'Ford',
                'model': 'F-150',
                'estimated_max_bid': 3900.0,
                'estimated_net_profit': 3250.0,
                'confidence_score': 81.0,
                'created_at': '2026-07-14T12:00:00Z',
              },
            ),
          );
        },
      ),
    );
    final gateway = DioRc1Gateway(dio: dio);

    final session = await gateway.signIn(
      email: 'operator@effortlesssmoke.com',
      password: 'local-rc1',
    );
    final opportunity = await gateway.createOpportunity(
      const TenantScope(
        organizationId: 'org-local',
        workspaceId: 'workspace-local',
      ),
      title: '2019 Ford F-150 auction lead',
      year: 2019,
      make: 'Ford',
      model: 'F-150',
    );

    final opportunityRequest = capturedRequests.last;
    expect(capturedRequests.first.path, '/v1/auth/login');
    expect(session.memberships.single.role, 'operator');
    expect(opportunityRequest.path, '/v1/opportunities');
    expect(
      opportunityRequest.headers['Authorization'],
      'Bearer opaque-session-token',
    );
    expect(opportunityRequest.headers['X-Organization-ID'], 'org-local');
    expect(opportunityRequest.headers['X-Workspace-ID'], 'workspace-local');
    expect(opportunityRequest.data['procurement_intent'], 'undecided');
    expect(opportunity.opportunityId, 'opportunity-api-id');
    expect(opportunity.opportunityCode, 'OPP-000001');
  });

  test('logout sends the bearer token and clears it after revocation', () async {
    final capturedRequests = <RequestOptions>[];
    final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000'));
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          capturedRequests.add(options);
          if (options.path == '/v1/auth/login') {
            handler.resolve(
              Response<dynamic>(
                requestOptions: options,
                statusCode: 200,
                data: {
                  'access_token': 'opaque-session-token',
                  'token_type': 'bearer',
                  'expires_at': '2026-07-14T20:00:00Z',
                  'identity': {
                    'user_id': 'user-local',
                    'email': 'operator@effortlesssmoke.com',
                    'display_name': 'Local Operator',
                    'memberships': [
                      {
                        'organization_id': 'org-local',
                        'organization_name': 'Effortless Smoke, LLC',
                        'workspace_id': 'workspace-local',
                        'workspace_name': 'RecyclerOS Operations',
                        'role': 'operator',
                      },
                    ],
                  },
                },
              ),
            );
            return;
          }
          handler.resolve(
            Response<dynamic>(requestOptions: options, statusCode: 204),
          );
        },
      ),
    );
    final gateway = DioRc1Gateway(dio: dio);

    await gateway.signIn(
      email: 'operator@effortlesssmoke.com',
      password: 'local-rc1',
    );
    await gateway.logout();

    final logoutRequest = capturedRequests.last;
    expect(logoutRequest.path, '/v1/auth/logout');
    expect(logoutRequest.method, 'POST');
    expect(
      logoutRequest.headers['Authorization'],
      'Bearer opaque-session-token',
    );
    await expectLater(
      gateway.logout(),
      throwsA(
        isA<Rc1GatewayException>().having(
          (error) => error.message,
          'message',
          'Sign in before logging out.',
        ),
      ),
    );
  });

  test('updates mileage and persists the selected procurement outcome', () async {
    final capturedRequests = <RequestOptions>[];
    final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000'));
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          capturedRequests.add(options);
          if (options.path == '/v1/auth/login') {
            handler.resolve(
              Response<dynamic>(
                requestOptions: options,
                statusCode: 200,
                data: {
                  'access_token': 'opaque-session-token',
                  'token_type': 'bearer',
                  'expires_at': '2026-07-14T20:00:00Z',
                  'identity': {
                    'user_id': 'user-local',
                    'email': 'operator@effortlesssmoke.com',
                    'display_name': 'Local Operator',
                    'memberships': [
                      {
                        'organization_id': 'org-local',
                        'organization_name': 'Effortless Smoke, LLC',
                        'workspace_id': 'workspace-local',
                        'workspace_name': 'RecyclerOS Operations',
                        'role': 'operator',
                      },
                    ],
                  },
                },
              ),
            );
            return;
          }
          if (options.path == '/v1/vehicles/VEH-000001/mileage') {
            handler.resolve(
              Response<dynamic>(
                requestOptions: options,
                statusCode: 200,
                data: {
                  'vehicle_id': 'vehicle-1',
                  'vehicle_code': 'VEH-000001',
                  'vin': null,
                  'year': 2014,
                  'make': 'Test Make',
                  'model': 'Test Model',
                  'trim': null,
                  'engine': null,
                  'transmission': null,
                  'drivetrain': null,
                  'mileage': 141500,
                  'lifecycle_status': 'discovered',
                  'created_at': '2026-07-14T12:00:00Z',
                  'updated_at': '2026-07-14T12:01:00Z',
                },
              ),
            );
            return;
          }
          handler.resolve(
            Response<dynamic>(
              requestOptions: options,
              statusCode: 200,
              data: {
                'opportunity_id': 'opportunity-1',
                'opportunity_code': 'OPP-000001',
                'title': 'Pilot vehicle',
                'source_type': 'manual',
                'status': 'converted',
                'procurement_intent': 'resale',
                'vin': null,
                'year': 2014,
                'make': 'Test Make',
                'model': 'Test Model',
                'estimated_max_bid': null,
                'estimated_net_profit': null,
                'confidence_score': null,
                'created_at': '2026-07-14T12:00:00Z',
              },
            ),
          );
        },
      ),
    );
    final gateway = DioRc1Gateway(dio: dio);
    const tenant = TenantScope(
      organizationId: 'org-local',
      workspaceId: 'workspace-local',
    );
    final timestamp = DateTime.utc(2026, 7, 14, 12);
    final vehicle = Vehicle(
      vehicleId: 'vehicle-1',
      vehicleCode: 'VEH-000001',
      year: 2014,
      make: 'Test Make',
      model: 'Test Model',
      lifecycleStatus: VehicleLifecycleStatus.discovered,
      createdAt: timestamp,
      updatedAt: timestamp,
    );
    final opportunity = Opportunity(
      opportunityId: 'opportunity-1',
      opportunityCode: 'OPP-000001',
      title: 'Pilot vehicle',
      source: OpportunitySource.manual,
      status: OpportunityStatus.converted,
      procurementIntent: ProcurementIntent.undecided,
      year: 2014,
      make: 'Test Make',
      model: 'Test Model',
      createdAt: timestamp,
      updatedAt: timestamp,
    );

    await gateway.signIn(
      email: 'operator@effortlesssmoke.com',
      password: 'local-rc1',
    );
    final updatedVehicle = await gateway.updateVehicleMileage(
      tenant,
      vehicle: vehicle,
      mileage: 141500,
    );
    final updatedOpportunity = await gateway.updateProcurementDecision(
      tenant,
      opportunity: opportunity,
      intent: ProcurementIntent.resale,
    );

    expect(updatedVehicle.mileage, 141500);
    expect(updatedOpportunity.procurementIntent, ProcurementIntent.resale);
    expect(capturedRequests[1].method, 'PATCH');
    expect(capturedRequests[1].data, {'mileage': 141500});
    expect(capturedRequests[2].method, 'PATCH');
    expect(capturedRequests[2].data, {'intent': 'resale'});
    for (final request in capturedRequests.skip(1)) {
      expect(request.headers['X-Organization-ID'], 'org-local');
      expect(request.headers['X-Workspace-ID'], 'workspace-local');
    }
  });
}
