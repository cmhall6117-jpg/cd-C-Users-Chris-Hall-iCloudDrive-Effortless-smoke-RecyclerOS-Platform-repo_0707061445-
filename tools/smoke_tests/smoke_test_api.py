import requests

BASE_URL = "http://127.0.0.1:8000"

ENDPOINTS = [
    "/v1/health",
    "/v1/opportunities",
    "/v1/dashboard/mission-control",
    "/v1/sync-health/summary",
    "/v1/audit/events",
]

def main():
    failed = []
    for endpoint in ENDPOINTS:
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, timeout=5)
            print(endpoint, response.status_code)
            if response.status_code >= 400:
                failed.append(endpoint)
        except Exception as exc:
            print(endpoint, "ERROR", exc)
            failed.append(endpoint)

    if failed:
        raise SystemExit(f"Smoke test failed: {failed}")

    print("Smoke test passed.")

if __name__ == "__main__":
    main()
