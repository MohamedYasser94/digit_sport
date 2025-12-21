no discount if yes #!/bin/bash
# Troubleshooting Commands for API Timeout Fixes
# Use these commands to diagnose and fix issues

# =============================================================================
# TEST AND VERIFY SETUP
# =============================================================================

# Test 1: Verify the API client module loads correctly
echo "=== Test 1: Import API Client ==="
python -c "
import django
django.setup()
from core.utils.api_client import get_api_client, APIClient
client = get_api_client()
print(f'✓ API Client initialized')
print(f'  Timeout: {client.timeout}s')
print(f'  Retries: {client.retries}')
print(f'  Circuit breakers: {len(client.circuit_breakers)}')
"

# Test 2: Check Django settings
echo -e "\n=== Test 2: Verify Django Settings ==="
python -c "
import django
django.setup()
from django.conf import settings
print(f'✓ API_REQUEST_TIMEOUT: {getattr(settings, \"API_REQUEST_TIMEOUT\", \"NOT SET\")}')
print(f'✓ API_REQUEST_RETRIES: {getattr(settings, \"API_REQUEST_RETRIES\", \"NOT SET\")}')
print(f'✓ API_BULK_OPERATION_TIMEOUT: {getattr(settings, \"API_BULK_OPERATION_TIMEOUT\", \"NOT SET\")}')
print(f'✓ SPORT_MONKS_TOKEN: {\"SET\" if getattr(settings, \"SPORT_MONKS_TOKEN\", None) else \"NOT SET\"}')
print(f'✓ SPORT_MONKS_URL: {getattr(settings, \"SPORT_MONKS_URL\", \"NOT SET\")}')
"

# Test 3: Run full test suite
echo -e "\n=== Test 3: Run Full Test Suite ==="
python test_api_client_fixes.py

# =============================================================================
# DIAGNOSTIC COMMANDS
# =============================================================================

# Check logs for API errors
echo -e "\n=== View Recent API Errors ==="
tail -50 debug.log | grep -E "ERROR|timeout|Circuit|failed"

# Monitor real-time API calls
echo -e "\n=== Monitor Real-time API Calls (Press Ctrl+C to stop) ==="
echo "Command: tail -f debug.log | grep -E 'GET|POST|API|Circuit'"
echo "Run this in a separate terminal while testing the endpoints"

# Check if requirements are installed
echo -e "\n=== Check Dependencies ==="
python -c "
import requests
import urllib3
print(f'✓ requests: {requests.__version__}')
print(f'✓ urllib3: {urllib3.__version__}')
"

# =============================================================================
# TEST API ENDPOINTS
# =============================================================================

# Test using curl
echo -e "\n=== Test SportMonks Players Endpoint ==="
echo "Command: curl -X POST http://localhost:8000/sport/monk/players/api/get/ \\"
echo "  -H \"Authorization: Bearer YOUR_TOKEN\" \\"
echo "  -H \"Content-Type: application/x-www-form-urlencoded\" \\"
echo "  -d \"sport=football\""

# Test using Python requests
echo -e "\n=== Test using Python (script) ==="
cat > test_api_endpoints.py << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

import requests
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Replace with actual test user credentials
USERNAME = 'admin'
PASSWORD = 'admin123'

# Get or create token
user = User.objects.get(username=USERNAME)
token, _ = Token.objects.get_or_create(user=user)

BASE_URL = 'http://localhost:8000'
HEADERS = {
    'Authorization': f'Bearer {token.key}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Test SportMonks endpoint
print("Testing SportMonks Players endpoint...")
response = requests.post(
    f'{BASE_URL}/sport/monk/players/api/get/',
    headers=HEADERS,
    data={'sport': 'football'},
    timeout=120
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test TransferMarket endpoint
print("\nTesting TransferMarket Players endpoint...")
response = requests.post(
    f'{BASE_URL}/sport/transfermarket/players/api/get/',
    headers=HEADERS,
    data={'sport': 'football'},
    timeout=120
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
EOF

echo "Run: python test_api_endpoints.py"

# =============================================================================
# DATABASE CHECKS
# =============================================================================

# Check player count before and after
echo -e "\n=== Check Database Stats ==="
python -c "
import django
django.setup()
from apps.sport.models import Players, Sport

try:
    football = Sport.objects.get(name='football')
    total = Players.objects.filter(sport=football).count()
    with_image = Players.objects.filter(sport=football, image_path__isnull=False).exclude(image_path='').count()
    with_market_value = Players.objects.filter(sport=football, current_market_value__isnull=False).count()

    print(f'✓ Total Players: {total}')
    print(f'✓ With Image: {with_image}')
    print(f'✓ With Market Value: {with_market_value}')
except Sport.DoesNotExist:
    print('✗ Football sport not found')
"

# =============================================================================
# CIRCUIT BREAKER STATUS
# =============================================================================

echo -e "\n=== Check Circuit Breaker Status ==="
python -c "
import django
django.setup()
from core.utils.api_client import get_api_client

client = get_api_client()
if client.circuit_breakers:
    for endpoint, breaker in client.circuit_breakers.items():
        print(f'{endpoint}:')
        print(f'  State: {breaker.state}')
        print(f'  Failures: {breaker.failure_count}')
        print(f'  Last failure: {breaker.last_failure_time}')
else:
    print('No circuit breakers initialized yet (endpoints not called)')
"

# =============================================================================
# CLEANUP AND RESET
# =============================================================================

# Clear debug.log if it gets too large
echo -e "\n=== Clear Debug Log ==="
echo "Command: rm debug.log; touch debug.log"
# Uncomment to execute:
# rm debug.log && touch debug.log

# Reset circuit breakers (if needed)
echo -e "\n=== Reset Circuit Breakers ==="
python -c "
import django
django.setup()
from core.utils.api_client import get_api_client

client = get_api_client()
client.circuit_breakers.clear()
print('✓ Circuit breakers cleared')
"

# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================

echo -e "\n=== Monitor API Performance ==="
echo "Add this to your code to track performance:"
cat > performance_monitor.py << 'EOF'
import time
import logging
from core.utils.api_client import get_api_client

logger = logging.getLogger(__name__)

client = get_api_client()

# Measure time
start = time.time()
data = client.get('https://api.example.com/data')
elapsed = time.time() - start

logger.info(f"API call took {elapsed:.2f}s, success: {data is not None}")

# Get circuit breaker status
breaker = client._get_circuit_breaker('api.example.com')
logger.info(f"Circuit breaker state: {breaker.state}, failures: {breaker.failure_count}")
EOF

echo "See: performance_monitor.py"

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

echo -e "\n=== Validate Configuration ==="
python << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from django.conf import settings

checks = [
    ('API_REQUEST_TIMEOUT', 15, lambda x: isinstance(x, int) and x > 0),
    ('API_REQUEST_RETRIES', 3, lambda x: isinstance(x, int) and x > 0),
    ('API_BULK_OPERATION_TIMEOUT', 30, lambda x: isinstance(x, int) and x > 0),
    ('SPORT_MONKS_TOKEN', None, lambda x: x is not None and isinstance(x, str)),
    ('SPORT_MONKS_URL', None, lambda x: x is not None and isinstance(x, str)),
]

print("Configuration Validation:")
print("=" * 50)

all_valid = True
for setting, default, validator in checks:
    value = getattr(settings, setting, default)

    if value is None:
        print(f"✗ {setting}: NOT SET")
        all_valid = False
    elif not validator(value):
        print(f"✗ {setting}: INVALID VALUE ({value})")
        all_valid = False
    else:
        print(f"✓ {setting}: OK ({value})")

print("=" * 50)
if all_valid:
    print("✓ All configurations valid!")
else:
    print("✗ Some configurations are invalid or missing")
    print("  Please check your .env file and Django settings")
EOF

# =============================================================================
# COMMON ISSUES AND FIXES
# =============================================================================

echo -e "\n=== Common Issues and Fixes ==="
cat << 'EOF'

Issue 1: Module not found error
  Solution: pip install -r requirements.txt
  Check: python -c "from core.utils.api_client import get_api_client"

Issue 2: Circuit breaker stuck in OPEN state
  Solution: Wait 60 seconds for recovery, or restart Django
  Check: tail -f debug.log | grep "Circuit breaker"

Issue 3: API returning 401 (Unauthorized)
  Solution: Check SPORT_MONKS_TOKEN in .env file
  Check: echo $SPORT_MONKS_TOKEN

Issue 4: TransferMarket API returning no results
  Solution: Check internet connectivity, try different player name
  Check: curl https://transfermarkt-api.fly.dev/players/search/messi

Issue 5: Timeouts still occurring
  Solution: Increase API_REQUEST_TIMEOUT in settings
  Check: grep API_REQUEST_TIMEOUT digit_sport/settings.py

Issue 6: Database errors when saving players
  Solution: Check Players model has required fields
  Check: python manage.py makemigrations && python manage.py migrate

EOF

echo -e "\n=== Setup Complete ==="
echo "See documentation:"
echo "  - API_FIXES_QUICK_START.md"
echo "  - API_TIMEOUT_FIX_DOCUMENTATION.md"
echo "  - BEFORE_AFTER_COMPARISON.md"

