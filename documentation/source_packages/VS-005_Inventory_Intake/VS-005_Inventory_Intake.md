# VS-005 Inventory Intake & Management

Capabilities:
- CAP-501 Inventory Management
- CAP-006 Asset Engine Support

Workflows:
- WFL-006 Inventory Intake
- WFL-007 Cycle Count & Adjustment

Events:
- EVT-010 Inventory Created
- EVT-011 Inventory Adjusted

Objects:
- Part
- Inventory Item
- Storage Location
- Business Event
- Harvest Session

Acceptance Criteria:
1. User can create inventory from harvested part.
2. Inventory item includes part name, source vehicle, condition, quantity, and storage location.
3. Inventory status supports available, reserved, listed, sold, returned, scrapped, and lost.
4. Inventory item can be stored offline and queued for sync.
5. Inventory adjustment creates a business event.
