# Smoke Test Harness

## Purpose
Validate that the merged API starts and key scaffold endpoints respond.

## Usage
1. Start FastAPI:
   uvicorn src.main:app --reload

2. Run:
   python tools/smoke_tests/smoke_test_api.py

## Expected Result
The smoke test should report status codes for health, opportunities, dashboard, sync health, and audit endpoints.
