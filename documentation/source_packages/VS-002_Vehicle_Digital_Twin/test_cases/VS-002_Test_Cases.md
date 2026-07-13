# VS-002 Vehicle Digital Twin Test Cases

## TC-001 Create Vehicle
Given a user creates or links a vehicle  
When vehicle data is saved  
Then a Vehicle record is created with lifecycle status discovered.

## TC-002 View Vehicle Twin
Given a vehicle exists  
When the user opens the Vehicle Digital Twin screen  
Then the vehicle profile and lifecycle status are displayed.

## TC-003 Timeline Display
Given vehicle-related events exist  
When the user opens the timeline  
Then business events are displayed in chronological order.

## TC-004 Offline Vehicle Access
Given vehicle data exists locally  
When the device is offline  
Then the user can view the Vehicle Digital Twin.
