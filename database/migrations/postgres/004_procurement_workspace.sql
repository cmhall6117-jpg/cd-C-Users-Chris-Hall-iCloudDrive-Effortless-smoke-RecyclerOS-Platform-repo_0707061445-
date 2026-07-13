CREATE TABLE IF NOT EXISTS procurement_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES opportunities(id),
    auction_access_type TEXT NOT NULL DEFAULT 'unknown',
    recommended_intent TEXT NOT NULL DEFAULT 'undecided',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS procurement_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    procurement_analysis_id UUID REFERENCES procurement_analyses(id),
    intent TEXT NOT NULL,
    projected_revenue NUMERIC(12,2) NOT NULL DEFAULT 0,
    projected_costs NUMERIC(12,2) NOT NULL DEFAULT 0,
    recommended_max_bid NUMERIC(12,2) NOT NULL DEFAULT 0,
    projected_net_profit NUMERIC(12,2) NOT NULL DEFAULT 0,
    projected_margin_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    confidence_score NUMERIC(5,2) NOT NULL DEFAULT 0
);
