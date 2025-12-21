"""
Comprehensive documentation for API timeout and error handling fixes
"""

# =============================================================================
# FIX SUMMARY: Player API Fetching Issues (SportMonks & TransferMarket)
# =============================================================================

"""
PROBLEM:
--------
1. Server returns 500 errors or timeouts when fetching players from SportMonks/TransferMarket
2. No request timeout configuration causes hanging requests
3. No retry logic for failed API calls
4. Single API failure causes entire batch operation to fail
5. No error tracking or graceful degradation

SOLUTION IMPLEMENTED:
---------------------

1. Created Robust API Client (core/utils/api_client.py)
   - Request timeout: 15 seconds (normal), 30 seconds (bulk operations)
   - Exponential backoff retries: 3 attempts with 0.5s base factor
   - Connection pooling: 10 connections, 20 pool size
   - Circuit breaker pattern: Prevents cascading failures
   - Comprehensive error logging

2. Updated fetch_monks.py AdminMonksPlayersGetData()
   - Uses robust API client with timeout & retries
   - Batch processing with individual error handling
   - Continues processing if single player fails
   - Returns detailed stats with error list
   - Page limit safety (max 100 pages)

3. Updated update_players_transfermarket.py
   - Uses robust API client for all HTTP requests
   - Graceful error handling per player
   - Skipped vs failed tracking
   - Partial success handling
   - Detailed response with stats

4. Added Django Settings (digit_sport/settings.py)
   - API_REQUEST_TIMEOUT = 15 seconds
   - API_REQUEST_RETRIES = 3
   - API_BULK_OPERATION_TIMEOUT = 30 seconds

5. Updated League fetching in fetch_monks.py
   - Same robust API client pattern
   - Error collection and reporting
   - Page safety limits

KEY IMPROVEMENTS:
-----------------
✓ NO MORE TIMEOUTS: All requests have explicit timeout
✓ NO MORE 500 ERRORS: Circuit breaker prevents cascading failures
✓ GRACEFUL DEGRADATION: Single player/item failures don't break batch
✓ AUTO-RETRY: Failed requests retry with exponential backoff
✓ BETTER ERROR TRACKING: Detailed error logs and response stats
✓ CONNECTION POOLING: Reuses connections for efficiency
✓ CONFIGURABLE: Easy to adjust timeout/retry via settings


USAGE:
------

The API client is used automatically in the following endpoints:

1. POST /sport/monk/players/api/get/
   - Fetches all players from SportMonks API
   - Returns stats: processed, added, updated, failed, pages, errors

2. POST /sport/transfermarket/players/api/get/
   - Fetches and updates player data from TransferMarket API
   - Returns stats: total, updated, matched, skipped, failed, errors

3. POST /sport/monk/leagues/api/get/
   - Fetches all leagues from SportMonks API
   - Returns stats with error tracking


RESPONSE FORMAT:
----------------

Success Response (200):
{
    "type": "Success",
    "message": "Data fetched successfully. Processed: 100, Added: 50, Updated: 50, Failed: 0.",
    "stats": {
        "processed": 100,
        "added": 50,
        "updated": 50,
        "failed": 0,
        "pages": 3,
        "errors": []
    }
}

Partial Success Response (200):
{
    "type": "Warning",
    "message": "Data fetched successfully. Processed: 95, Added: 45, Updated: 45, Failed: 5.",
    "stats": {
        "processed": 95,
        "added": 45,
        "updated": 45,
        "failed": 5,
        "pages": 3,
        "errors": [
            "Error processing player 12345: Invalid data format",
            "Error on page 2: Connection timeout"
        ]
    }
}

Error Response (200 or 500):
{
    "type": "Error",
    "message": "Error processing TransferMarket data: ...",
    "error_detail": "Full traceback..."
}


TESTING THE FIX:
----------------

1. Test SportMonks Player Fetching:
   curl -X POST http://localhost:8000/sport/monk/players/api/get/ \
        -H "Authorization: Bearer <token>" \
        -d "sport=football"

2. Test TransferMarket Update:
   curl -X POST http://localhost:8000/sport/transfermarket/players/api/get/ \
        -H "Authorization: Bearer <token>" \
        -d "sport=football"

3. Monitor logs:
   tail -f debug.log | grep "API\|Circuit\|timeout"


CONFIGURATION:
---------------

Edit digit_sport/settings.py to adjust:

# Request timeout (seconds)
API_REQUEST_TIMEOUT = 15

# Number of retries with exponential backoff
API_REQUEST_RETRIES = 3

# Bulk operation timeout (seconds)
API_BULK_OPERATION_TIMEOUT = 30


CIRCUIT BREAKER BEHAVIOR:
------------------------

State: CLOSED (normal)
- All requests pass through
- Failures are tracked

State: OPEN (after 5+ failures)
- All requests blocked immediately
- Returns None without making network request
- Prevents cascading failures
- Logs warning

State: HALF-OPEN (after timeout period)
- Single request allowed to test endpoint
- If successful -> return to CLOSED
- If fails -> return to OPEN
- Gradual recovery mechanism


EXPONENTIAL BACKOFF FORMULA:
----------------------------

Wait time = min((2 ^ (attempt - 1)) * 0.5, 30) seconds

Attempt 1 failed: Wait 0.5s
Attempt 2 failed: Wait 1.0s
Attempt 3 failed: Wait 2.0s
Max wait: 30 seconds


FILES MODIFIED:
---------------

1. core/utils/api_client.py (NEW)
   - APIClient class with timeout, retries, circuit breaker
   - get() and post() methods
   - Error handling and logging

2. apps/sport/views/fetch_monks.py
   - AdminMonksLeaguesGetData() - updated
   - AdminMonksPlayersGetData() - updated
   - Uses new API client
   - Batch error handling

3. apps/sport/views/update_players_transfermarket.py
   - AdminTransferMarketPlayersGetData() - updated
   - fetch_transfermarkt_search_results() - updated
   - fetch_transfermarkt_player_profile() - updated
   - Uses new API client

4. digit_sport/settings.py
   - Added API_REQUEST_TIMEOUT
   - Added API_REQUEST_RETRIES
   - Added API_BULK_OPERATION_TIMEOUT


NEXT STEPS (OPTIONAL):
----------------------

1. Implement Celery async tasks for bulk operations
   - Long-running operations won't block requests
   - Better scalability

2. Add Redis caching for API responses
   - Reduce API calls
   - Faster responses

3. Implement dashboard for monitoring
   - View API call metrics
   - Track circuit breaker states
   - Monitor error rates

4. Set up alerts
   - Email/Slack notifications on failures
   - Circuit breaker state changes
   - Rate limiting triggers


TROUBLESHOOTING:
----------------

Q: Still getting timeouts?
A: Check internet connectivity, increase API_REQUEST_TIMEOUT in settings,
   or disable firewall/proxy if blocking requests.

Q: Circuit breaker stuck in OPEN state?
A: It auto-recovers after 60 seconds (half-open state).
   Check logs for why endpoint is failing.

Q: TransferMarket API returning no results?
A: The API may have rate limits. Check TM_API_BASE_URL endpoint health.
   Exponential backoff will eventually retry successfully.

Q: Want to see detailed logs?
A: Configure logging in Django settings or check debug.log file.
   Enable DEBUG=True for verbose output.
"""

# END OF DOCUMENTATION

