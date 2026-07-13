-- SQLite migration note:
-- SQLite ALTER TABLE supports adding one column per statement.

ALTER TABLE opportunities ADD COLUMN vin TEXT;
ALTER TABLE opportunities ADD COLUMN year INTEGER;
ALTER TABLE opportunities ADD COLUMN make TEXT;
ALTER TABLE opportunities ADD COLUMN model TEXT;
ALTER TABLE opportunities ADD COLUMN estimated_max_bid REAL;
ALTER TABLE opportunities ADD COLUMN estimated_net_profit REAL;
ALTER TABLE opportunities ADD COLUMN confidence_score REAL;

CREATE INDEX IF NOT EXISTS idx_opportunities_procurement_intent ON opportunities(procurement_intent);
CREATE INDEX IF NOT EXISTS idx_opportunities_source_type ON opportunities(source_type);
CREATE INDEX IF NOT EXISTS idx_opportunities_vin ON opportunities(vin);
