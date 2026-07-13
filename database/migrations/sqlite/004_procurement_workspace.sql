CREATE TABLE IF NOT EXISTS procurement_analyses (
    id TEXT PRIMARY KEY,
    opportunity_id TEXT NOT NULL,
    auction_access_type TEXT NOT NULL DEFAULT 'unknown',
    recommended_intent TEXT NOT NULL DEFAULT 'undecided',
    created_at TEXT NOT NULL,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS procurement_scenarios (
    id TEXT PRIMARY KEY,
    procurement_analysis_id TEXT NOT NULL,
    intent TEXT NOT NULL,
    projected_revenue REAL NOT NULL DEFAULT 0,
    projected_costs REAL NOT NULL DEFAULT 0,
    recommended_max_bid REAL NOT NULL DEFAULT 0,
    projected_net_profit REAL NOT NULL DEFAULT 0,
    projected_margin_percent REAL NOT NULL DEFAULT 0,
    confidence_score REAL NOT NULL DEFAULT 0,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);
