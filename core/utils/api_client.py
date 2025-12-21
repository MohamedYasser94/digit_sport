"""
Robust API Client with timeout, retries, and error handling
"""
import time
import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_TIMEOUT = 15  # seconds
BULK_OPERATION_TIMEOUT = 30  # seconds
DEFAULT_RETRIES = 3
BACKOFF_FACTOR = 0.5  # exponential backoff multiplier


class CircuitBreaker:
    """Simple circuit breaker to prevent cascading failures"""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        self.state = 'closed'

    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")

    def is_available(self) -> bool:
        """Check if circuit is available for requests"""
        if self.state == 'closed':
            return True

        if self.state == 'open':
            # Try to transition to half-open after timeout
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
                self.failure_count = 0
                logger.info("Circuit breaker HALF-OPEN, retrying...")
                return True
            return False

        # half-open: allow single request
        return True


class APIClient:
    """
    Robust API client with:
    - Request timeouts
    - Exponential backoff retries
    - Connection pooling
    - Circuit breaker pattern
    - Comprehensive error handling
    """

    def __init__(self,
                 timeout: int = DEFAULT_TIMEOUT,
                 retries: int = DEFAULT_RETRIES,
                 backoff_factor: float = BACKOFF_FACTOR):
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.session = self._create_session()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def _create_session(self) -> requests.Session:
        """Create a requests session with connection pooling and retry strategy"""
        session = requests.Session()

        # Create retry strategy
        retry_strategy = Retry(
            total=self.retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        # Mount adapter with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_circuit_breaker(self, endpoint: str) -> CircuitBreaker:
        """Get or create circuit breaker for endpoint"""
        if endpoint not in self.circuit_breakers:
            self.circuit_breakers[endpoint] = CircuitBreaker()
        return self.circuit_breakers[endpoint]

    def get(self,
            url: str,
            headers: Optional[Dict] = None,
            params: Optional[Dict] = None,
            timeout: Optional[int] = None,
            **kwargs) -> Optional[Dict[str, Any]]:
        """
        Make a GET request with retry logic and circuit breaker

        Args:
            url: Request URL
            headers: Optional headers dict
            params: Optional query parameters
            timeout: Optional timeout override (defaults to self.timeout)
            **kwargs: Additional requests arguments

        Returns:
            Response JSON or None on failure
        """
        endpoint = self._extract_endpoint(url)
        circuit_breaker = self._get_circuit_breaker(endpoint)

        # Check circuit breaker
        if not circuit_breaker.is_available():
            logger.error(f"Circuit breaker OPEN for {endpoint}, request blocked")
            return None

        timeout = timeout or self.timeout

        for attempt in range(1, self.retries + 1):
            try:
                logger.debug(f"GET {url} (attempt {attempt}/{self.retries})")

                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=timeout,
                    **kwargs
                )

                # Check response status
                if response.status_code == 200:
                    circuit_breaker.record_success()
                    try:
                        return response.json()
                    except ValueError as e:
                        logger.error(f"Failed to parse JSON from {url}: {e}")
                        return None

                elif response.status_code in [429, 500, 502, 503, 504]:
                    # Rate limit or server error - retry
                    wait_time = self._calculate_backoff(attempt)
                    logger.warning(f"API returned {response.status_code}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                else:
                    # Other error
                    logger.error(f"API returned {response.status_code}: {response.text[:200]}")
                    circuit_breaker.record_failure()
                    return None

            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on {url} (attempt {attempt}/{self.retries}): {e}")
                if attempt < self.retries:
                    wait_time = self._calculate_backoff(attempt)
                    time.sleep(wait_time)
                    continue
                circuit_breaker.record_failure()
                return None

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on {url} (attempt {attempt}/{self.retries}): {e}")
                if attempt < self.retries:
                    wait_time = self._calculate_backoff(attempt)
                    time.sleep(wait_time)
                    continue
                circuit_breaker.record_failure()
                return None

            except Exception as e:
                logger.error(f"Unexpected error on {url}: {type(e).__name__}: {e}")
                circuit_breaker.record_failure()
                return None

        circuit_breaker.record_failure()
        return None

    def post(self,
             url: str,
             data: Optional[Dict] = None,
             json_data: Optional[Dict] = None,
             headers: Optional[Dict] = None,
             timeout: Optional[int] = None,
             **kwargs) -> Optional[Dict[str, Any]]:
        """
        Make a POST request with retry logic

        Args:
            url: Request URL
            data: Form data
            json_data: JSON body
            headers: Optional headers dict
            timeout: Optional timeout override
            **kwargs: Additional requests arguments

        Returns:
            Response JSON or None on failure
        """
        timeout = timeout or self.timeout

        for attempt in range(1, self.retries + 1):
            try:
                logger.debug(f"POST {url} (attempt {attempt}/{self.retries})")

                response = self.session.post(
                    url,
                    data=data,
                    json=json_data,
                    headers=headers,
                    timeout=timeout,
                    **kwargs
                )

                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError as e:
                        logger.error(f"Failed to parse JSON from {url}: {e}")
                        return None

                elif response.status_code in [429, 500, 502, 503, 504]:
                    wait_time = self._calculate_backoff(attempt)
                    logger.warning(f"API returned {response.status_code}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                else:
                    logger.error(f"API returned {response.status_code}: {response.text[:200]}")
                    return None

            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on {url} (attempt {attempt}/{self.retries}): {e}")
                if attempt < self.retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                return None

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on {url} (attempt {attempt}/{self.retries}): {e}")
                if attempt < self.retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                return None

            except Exception as e:
                logger.error(f"Unexpected error on {url}: {type(e).__name__}: {e}")
                return None

        return None

    @staticmethod
    def _extract_endpoint(url: str) -> str:
        """Extract endpoint domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return f"{parsed.netloc}{parsed.path.split('?')[0]}"
        except:
            return url

    @staticmethod
    def _calculate_backoff(attempt: int, factor: float = BACKOFF_FACTOR) -> float:
        """Calculate exponential backoff time"""
        return min((2 ** (attempt - 1)) * factor, 30)  # Cap at 30 seconds


# Create a singleton instance
_api_client = None


def get_api_client() -> APIClient:
    """Get or create the singleton API client"""
    global _api_client
    if _api_client is None:
        _api_client = APIClient(
            timeout=getattr(settings, 'API_REQUEST_TIMEOUT', DEFAULT_TIMEOUT),
            retries=getattr(settings, 'API_REQUEST_RETRIES', DEFAULT_RETRIES)
        )
    return _api_client

