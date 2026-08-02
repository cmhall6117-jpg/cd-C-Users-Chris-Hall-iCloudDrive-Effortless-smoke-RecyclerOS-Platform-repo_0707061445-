import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:recycleros_pro_mobile/src/data/dio_rc1_gateway.dart';
import 'package:recycleros_pro_mobile/src/data/rc1_gateway.dart';

void main() {
  test('sends tenant headers and maps a backend-created opportunity', () async {
    RequestOptions? capturedRequest;
    final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000'));
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          capturedRequest = options;
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

    expect(capturedRequest?.path, '/v1/opportunities');
    expect(capturedRequest?.headers['X-Organization-ID'], 'org-local');
    expect(capturedRequest?.headers['X-Workspace-ID'], 'workspace-local');
    expect(opportunity.opportunityId, 'opportunity-api-id');
    expect(opportunity.opportunityCode, 'OPP-000001');
  });
}
