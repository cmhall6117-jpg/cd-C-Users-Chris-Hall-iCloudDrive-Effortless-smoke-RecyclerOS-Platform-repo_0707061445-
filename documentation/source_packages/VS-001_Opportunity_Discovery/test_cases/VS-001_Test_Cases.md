# VS-001 Opportunity Discovery Test Cases

## TC-001 Create Manual Opportunity
Given the user opens Opportunity Discovery  
When the user enters a title and selects source type manual  
Then the system saves an opportunity locally and creates EVT-001.

## TC-002 Assign Procurement Intent
Given an opportunity exists  
When the user selects resale, personal use, or part-out  
Then the system records procurement intent and creates EVT-003.

## TC-003 Offline Save
Given the device is offline  
When the user saves an opportunity  
Then the opportunity is saved locally and added to sync_queue.

## TC-004 API Create Opportunity
Given the backend API is running  
When POST /v1/opportunities is called  
Then the API returns opportunity metadata and event_created.
