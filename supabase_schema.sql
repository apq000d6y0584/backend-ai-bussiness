-- Supabase/PostgreSQL Database Schema for BI Engine
-- Converted from SQLite schema to Supabase-compatible PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ENUM TYPES
-- =====================================================

CREATE TYPE sentiment_label AS ENUM (
    'sangat_positif',
    'positif',
    'netral',
    'negatif',
    'sangat_negatif'
);

CREATE TYPE recommendation_priority AS ENUM (
    'tinggi',
    'sedang',
    'rendah'
);

-- =====================================================
-- STOCK DATA TABLE
-- Stores historical stock closing prices from Yahoo Finance
-- =====================================================

CREATE TABLE stock_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL,
    dates JSONB NOT NULL,  -- JSON array of dates
    closing_prices JSONB NOT NULL,  -- JSON array of prices
    current_price DOUBLE PRECISION,
    price_change DOUBLE PRECISION,
    price_change_percent DOUBLE PRECISION,
    average_price DOUBLE PRECISION,
    highest_price DOUBLE PRECISION,
    lowest_price DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for stock_data
CREATE INDEX idx_stock_data_ticker ON stock_data(ticker);
CREATE INDEX idx_stock_data_created_at ON stock_data(created_at DESC);

-- =====================================================
-- NEWS DATA TABLE
-- Stores scraped news headlines from CNBC or other sources
-- =====================================================

CREATE TABLE news_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source TEXT NOT NULL,
    headlines JSONB NOT NULL,  -- JSON array of headlines
    total_found INTEGER,
    relevant_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for news_data
CREATE INDEX idx_news_data_source ON news_data(source);
CREATE INDEX idx_news_data_created_at ON news_data(created_at DESC);

-- =====================================================
-- CACHE TABLE
-- Stores cached data to avoid rate limiting
-- =====================================================

CREATE TABLE cache (
    cache_key TEXT PRIMARY KEY,
    prefix TEXT NOT NULL,
    ticker TEXT,
    data JSONB NOT NULL,  -- JSON cached data
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for cache
CREATE INDEX idx_cache_prefix ON cache(prefix);
CREATE INDEX idx_cache_ticker ON cache(ticker);
CREATE INDEX idx_cache_timestamp ON cache(timestamp DESC);

-- =====================================================
-- MERGED DATA TABLE
-- Combined quantitative + qualitative data
-- =====================================================

CREATE TABLE merged_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL,
    quantitative_data JSONB NOT NULL,  -- Stock data from Yahoo Finance
    qualitative_data JSONB NOT NULL,  -- News/sentiment data
    merged_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for merged_data
CREATE INDEX idx_merged_data_ticker ON merged_data(ticker);
CREATE INDEX idx_merged_data_merged_at ON merged_data(merged_at DESC);

-- =====================================================
-- ANALYSIS TABLE
-- Complete market analysis results
-- =====================================================

CREATE TABLE analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merged_id UUID REFERENCES merged_data(id) ON DELETE CASCADE,
    executive_summary TEXT,
    quantitative_analysis JSONB NOT NULL,  -- Price trend analysis
    qualitative_analysis JSONB NOT NULL,  -- FinBERT sentiment analysis
    combined_analysis JSONB NOT NULL,  -- Combined results
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for analysis
CREATE INDEX idx_analysis_merged_id ON analysis(merged_id);
CREATE INDEX idx_analysis_analyzed_at ON analysis(analyzed_at DESC);

-- =====================================================
-- SENTIMENT SCORE TABLE
-- Final sentiment score (1-10 scale)
-- =====================================================

CREATE TABLE sentiment_score (
    score INTEGER PRIMARY KEY CHECK (score >= 1 AND score <= 10),
    label sentiment_label NOT NULL,
    quantitative_score INTEGER,
    finbert_score DOUBLE PRECISION,
    breakdown JSONB NOT NULL,  -- Score breakdown details
    interpretation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for sentiment_score
CREATE INDEX idx_sentiment_score_label ON sentiment_score(label);

-- =====================================================
-- RECOMMENDATIONS TABLE
-- Business recommendations
-- =====================================================

CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority recommendation_priority NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for recommendations
CREATE INDEX idx_recommendations_analysis_id ON recommendations(analysis_id);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);

-- =====================================================
-- TRIGGER FUNCTIONS FOR UPDATED_AT
-- Auto-update timestamps
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_stock_data_updated_at 
    BEFORE UPDATE ON stock_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_news_data_updated_at 
    BEFORE UPDATE ON news_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_merged_data_updated_at 
    BEFORE UPDATE ON merged_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_updated_at 
    BEFORE UPDATE ON analysis 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recommendations_updated_at 
    BEFORE UPDATE ON recommendations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SEED DATA FOR SENTIMENT_SCORE
-- Pre-populate sentiment score lookup table
-- =====================================================

INSERT INTO sentiment_score (score, label, quantitative_score, finbert_score, breakdown, interpretation) VALUES
(1, 'sangat_negatif', 1, 0.0, '{"price_score": 1, "sentiment_score": 1}', 'Sangat negatif - Hindari investasi'),
(2, 'sangat_negatif', 2, 0.25, '{"price_score": 2, "sentiment_score": 2.5}', 'Sangat negatif - Hindari investasi'),
(3, 'negatif', 3, 0.5, '{"price_score": 3, "sentiment_score": 5}', 'Negatif - Pertimbangkan dengan hati'),
(4, 'negatif', 4, 1.0, '{"price_score": 4, "sentiment_score": 10}', 'Negatif - Perlu konfirmasi lebih lanjut'),
(5, 'netral', 5, 1.5, '{"price_score": 5, "sentiment_score": 15}', 'Netral - Tunggu informasi lebih lanjut'),
(6, 'netral', 6, 2.0, '{"price_score": 6, "sentiment_score": 20}', 'Netral - Pertimbangkan pilihan lain'),
(7, 'positif', 7, 2.5, '{"price_score": 7, "sentiment_score": 25}', 'Positif - Berpotensi untuk investasi'),
(8, 'positif', 8, 3.0, '{"price_score": 8, "sentiment_score": 30}', 'Positif - Kondisi pasar baik'),
(9, 'sangat_positif', 9, 3.5, '{"price_score": 9, "sentiment_score": 35}', 'Sangat positif - Rekomendasi kuat untuk investasi'),
(10, 'sangat_positif', 10, 4.0, '{"price_score": 10, "sentiment_score": 40}', 'Sangat positif - Sangat direkomendasikan untuk investasi')
ON CONFLICT (score) DO NOTHING;

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- Enable RLS for all tables (Supabase best practice)
-- =====================================================

ALTER TABLE stock_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE news_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE merged_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_score ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow all for authenticated users)
-- Adjust these policies based on your auth requirements

CREATE POLICY "Allow all access to stock_data" ON stock_data
    FOR ALL USING (true);

CREATE POLICY "Allow all access to news_data" ON news_data
    FOR ALL USING (true);

CREATE POLICY "Allow all access to cache" ON cache
    FOR ALL USING (true);

CREATE POLICY "Allow all access to merged_data" ON merged_data
    FOR ALL USING (true);

CREATE POLICY "Allow all access to analysis" ON analysis
    FOR ALL USING (true);

CREATE POLICY "Allow all access to sentiment_score" ON sentiment_score
    FOR ALL USING (true);

CREATE POLICY "Allow all access to recommendations" ON recommendations
    FOR ALL USING (true);

-- =====================================================
-- FUNCTION: Get latest stock data by ticker
-- =====================================================

CREATE OR REPLACE FUNCTION get_latest_stock_data(p_ticker TEXT)
RETURNS TABLE (
    id UUID,
    ticker TEXT,
    current_price DOUBLE PRECISION,
    price_change DOUBLE PRECISION,
    price_change_percent DOUBLE PRECISION,
    average_price DOUBLE PRECISION,
    highest_price DOUBLE PRECISION,
    lowest_price DOUBLE PRECISION,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sd.id,
        sd.ticker,
        sd.current_price,
        sd.price_change,
        sd.price_change_percent,
        sd.average_price,
        sd.highest_price,
        sd.lowest_price,
        sd.created_at
    FROM stock_data sd
    WHERE sd.ticker = p_ticker
    ORDER BY sd.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Get latest news by source
-- =====================================================

CREATE OR REPLACE FUNCTION get_latest_news(p_source TEXT)
RETURNS TABLE (
    id UUID,
    source TEXT,
    headlines JSONB,
    total_found INTEGER,
    relevant_count INTEGER,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        nd.id,
        nd.source,
        nd.headlines,
        nd.total_found,
        nd.relevant_count,
        nd.created_at
    FROM news_data nd
    WHERE nd.source = p_source
    ORDER BY nd.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Get analysis with recommendations
-- =====================================================

CREATE OR REPLACE FUNCTION get_analysis_with_recommendations(p_analysis_id UUID)
RETURNS TABLE (
    analysis_id UUID,
    executive_summary TEXT,
    combined_analysis JSONB,
    recommendation_id UUID,
    title TEXT,
    description TEXT,
    priority TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.executive_summary,
        a.combined_analysis,
        r.id,
        r.title,
        r.description,
        r.priority::TEXT
    FROM analysis a
    LEFT JOIN recommendations r ON r.analysis_id = a.id
    WHERE a.id = p_analysis_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEW: Combined market analysis view
-- =====================================================

CREATE OR REPLACE VIEW market_analysis_summary AS
SELECT 
    md.ticker,
    sd.current_price,
    sd.price_change_percent,
    sd.average_price,
    a.executive_summary,
    a.combined_analysis,
    ss.label AS sentiment_label,
    ss.score AS sentiment_score,
    md.merged_at
FROM merged_data md
LEFT JOIN stock_data sd ON sd.ticker = md.ticker
LEFT JOIN analysis a ON a.merged_id = md.id
LEFT JOIN (
    SELECT DISTINCT ON (analysis_id)
        analysis_id,
        score,
        label
    FROM recommendations r
    JOIN sentiment_score ss ON 1=1
    ORDER BY analysis_id, r.created_at DESC
) ss ON ss.score IS NOT NULL
ORDER BY md.merged_at DESC;

-- =====================================================
-- FUNCTION: Delete old data (older than 24 hours)
-- Automatically cleans stock_data and analysis tables
-- =====================================================

CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete stock_data older than 24 hours
    DELETE FROM stock_data 
    WHERE created_at < NOW() - INTERVAL '24 hours';

    -- Delete analysis older than 24 hours
    DELETE FROM analysis 
    WHERE analyzed_at < NOW() - INTERVAL '24 hours';

    -- Also clean up related merged_data that has no analysis
    DELETE FROM merged_data 
    WHERE merged_at < NOW() - INTERVAL '24 hours'
    AND id NOT IN (SELECT merged_id FROM analysis WHERE merged_id IS NOT NULL);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Get cleanup stats
-- Shows how many rows would be deleted
-- =====================================================

CREATE OR REPLACE FUNCTION get_cleanup_stats()
RETURNS TABLE (
    table_name TEXT,
    rows_to_delete BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'stock_data'::TEXT, COUNT(*)::BIGINT
    FROM stock_data 
    WHERE created_at < NOW() - INTERVAL '24 hours'
    UNION ALL
    SELECT 'analysis'::TEXT, COUNT(*)::BIGINT
    FROM analysis 
    WHERE analyzed_at < NOW() - INTERVAL '24 hours'
    UNION ALL
    SELECT 'merged_data'::TEXT, COUNT(*)::BIGINT
    FROM merged_data 
    WHERE merged_at < NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- pg_cron: Schedule automatic cleanup every hour
-- Uncomment the following lines if pg_cron extension is enabled
-- =====================================================

-- SELECT cron.schedule(
--     'cleanup-old-data',
--     '0 * * * *',  -- Every hour at minute 0
--     'SELECT cleanup_old_data()'
-- );

-- To unschedule:
-- SELECT cron.unschedule('cleanup-old-data');

-- =====================================================
-- ALTERNATIVE: Manual cleanup trigger
-- Uncomment to enable automatic cleanup on INSERT/UPDATE
-- =====================================================

-- CREATE OR REPLACE FUNCTION auto_cleanup_on_activity()
-- RETURNS TRIGGER AS $$
-- DECLARE
--     old_count INTEGER;
-- BEGIN
--     -- Check if we have too many recent records, cleanup old ones
--     SELECT COUNT(*) INTO old_count FROM stock_data 
--     WHERE created_at < NOW() - INTERVAL '24 hours';
    
--     IF old_count > 100 THEN
--         PERFORM cleanup_old_data();
--     END IF;
    
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER trigger_auto_cleanup
--     AFTER INSERT OR UPDATE ON stock_data
--     FOR EACH STATEMENT EXECUTE FUNCTION auto_cleanup_on_activity();

-- =====================================================
-- VIEW: Current data retention status
-- =====================================================

CREATE OR REPLACE VIEW data_retention_status AS
SELECT 
    'stock_data' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') AS rows_last_24h,
    MIN(created_at) AS oldest_record,
    MAX(created_at) AS newest_record
FROM stock_data
UNION ALL
SELECT 
    'analysis' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE analyzed_at >= NOW() - INTERVAL '24 hours') AS rows_last_24h,
    MIN(analyzed_at) AS oldest_record,
    MAX(analyzed_at) AS newest_record
FROM analysis
UNION ALL
SELECT 
    'merged_data' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE merged_at >= NOW() - INTERVAL '24 hours') AS rows_last_24h,
    MIN(merged_at) AS oldest_record,
    MAX(merged_at) AS newest_record
FROM merged_data;

-- =====================================================
-- END OF SCHEMA
-- =====================================================
password: P0l1t3kn1k%40P0w3r4n93r