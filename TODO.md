# TODO - BI Engine Fixes

## Current Issues

### 1. Supabase "proxy" Error (HIGH PRIORITY)
- **Error:** `Client.__init__() got an unexpected keyword argument 'proxy'`
- **Cause:** Environment variables (HTTP_PROXY, https_proxy) or supabase client version issue
- **Impact:** Non-critical - main analysis completes, but Supabase save fails

## Fix Plan

### Step 1: Fix Supabase Connection
- [x] Analyze error source
- [x] Modify `save_to_supabase()` to filter proxy kwargs
- [x] Add robust error handling
- [x] Make Supabase save truly non-blocking

### Step 2: Test the Fix
- [x] Run API server
- [x] Test with ticker=NVDA
- [x] Verify no proxy error

## Completion Criteria
- Main analysis completes successfully
- Supabase save error is caught and handled gracefully
- No crash if Supabase credentials missing
