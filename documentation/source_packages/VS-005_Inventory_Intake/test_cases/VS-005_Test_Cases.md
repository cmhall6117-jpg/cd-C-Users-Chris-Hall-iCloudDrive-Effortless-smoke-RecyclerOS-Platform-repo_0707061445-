# VS-005 Inventory Intake Test Cases

TC-001 Create Inventory Item:
Given harvested part data exists, when user creates inventory, then inventory item is saved with condition, status, and quantity.

TC-002 Storage Location:
Given user scans or enters location, when inventory is saved, then storage location is linked.

TC-003 Quantity Validation:
Given quantity is entered, when quantity is negative, then save is blocked.

TC-004 Offline Save:
Given device is offline, when inventory is created, then record is saved locally with sync_status pending.

TC-005 Inventory Event:
Given inventory item is created, then EVT-010 Inventory Created is recorded.
