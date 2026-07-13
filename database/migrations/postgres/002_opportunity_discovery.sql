ALTER TABLE opportunities
ADD COLUMN IF NOT EXISTS vin TEXT,
ADD COLUMN IF NOT EXISTS year INTEGER,
ADD COLUMN IF NOT EXISTS make TEXT,
ADD COLUMN IF NOT EXISTS model TEXT,
ADD COLUMN IF NOT EXISTS estimated_max_bid NUMERIC(12,2),
ADD COLUMN IF NOT EXISTS estimated_net_profit NUMERIC(12,2),
ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(5,2);

CREATE INDEX IF NOT EXISTS idx_opportunities_procurement_intent ON opportunities(procurement_intent);
CREATE INDEX IF NOT EXISTS idx_opportunities_source_type ON opportunities(source_type);
CREATE INDEX IF NOT EXISTS idx_opportunities_vin ON opportunities(vin);
