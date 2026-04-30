# TODO: Add save_to_supabase to BIEngine

## Plan

- [x] 1. Update requirements.txt - add supabase library
- [x] 2. Add save_to_supabase method to BIEngine class in bi_engine.py
- [x] 3. Update run() method to call save_to_supabase() after generating final_result

## Implementation Details

1. **requirements.txt**: Add `supabase>=2.0.0` for supabase-py library

2. **bi_engine.py - save_to_supabase method**:
   - Reads SUPABASE_URL and SUPABASE_KEY from os.environ
   - Uses supabase-py client
   - Implements delete-before-insert strategy to prevent database bloat
   - Saves data to multiple tables based on supabase_schema.sql:
     - stock_data: ticker, dates, closing_prices, current_price, price_change, etc.
     - news_data: source, headlines, total_found, relevant_count
     - merged_data: ticker, quantitative_data, qualitative_data
     - sentiment_score: score, label, breakdown
     - recommendations: title, description, priority

3. **bi_engine.py - run() method**: Call save_to_supabase() after generating final_result

