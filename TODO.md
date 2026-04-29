# Implementation Plan: Remove StockQuery Usage from api_server.py

## Status: In Progress

**Steps:**
- [x] User approval obtained
- [x] Step 1: Remove unused StockQuery class from api_server.py
- [x] Step 2: Verify the file contents after edit
- [ ] Step 3: Test the API server
- [ ] Step 4: Complete task

**Plan Summary:**
Remove the complete unused `class StockQuery(BaseModel)` definition as it has zero usage in functions. All endpoints already use direct, stable Query parameters.

