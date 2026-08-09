import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
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
    expect(opportunity.opportunityId, 'opportunity-api-id');
    expect(opportunity.opportunityCode, 'OPP-000001');
  });
}
