"""Fixed HTTP client for Swiggy MCP server using proper JSON-RPC protocol."""

import time
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

import httpx
from loguru import logger


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int, period: int = 60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def acquire(self):
        """Wait if necessary to stay within rate limit."""
        now = time.time()

        # Remove old calls outside the period
        self.calls = [call_time for call_time in self.calls if now - call_time < self.period]

        if len(self.calls) >= self.max_calls:
            # Wait until oldest call is outside the period
            sleep_time = self.period - (now - self.calls[0]) + 0.1
            logger.warning(f"Rate limit reached, sleeping for {sleep_time:.1f}s")
            time.sleep(sleep_time)
            self.calls = self.calls[1:]

        self.calls.append(time.time())


class MCPClient:
    """HTTP client for communicating with Swiggy Instamart MCP server using JSON-RPC."""

    def __init__(self, base_url: str, auth_manager, timeout: int = 30,
                 max_retries: int = 3, rate_limit: int = 100):
        self.base_url = base_url.rstrip("/")
        self.auth_manager = auth_manager
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = RateLimiter(max_calls=rate_limit, period=60)
        self.client = httpx.Client(timeout=timeout)
        self.request_id = 0
        self.initialized = False

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token."""
        token = self.auth_manager.get_valid_token()
        if not token:
            raise Exception("No valid authentication token available")

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

    def _next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    def _initialize(self):
        """Initialize MCP connection."""
        if self.initialized:
            return

        logger.debug("Initializing MCP connection")

        init_message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "swiggy-analyzer",
                    "version": "0.1.0"
                }
            }
        }

        response = self.client.post(
            self.base_url,
            json=init_message,
            headers=self._get_headers()
        )

        if response.status_code != 200:
            raise Exception(f"MCP initialization failed: {response.status_code}")

        result = response.json()
        if "error" in result:
            raise Exception(f"MCP error: {result['error']['message']}")

        self.initialized = True
        logger.debug("MCP connection initialized successfully")

    def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call an MCP tool using JSON-RPC protocol.

        Args:
            tool_name: Name of the MCP tool to call
            arguments: Tool arguments

        Returns:
            Tool response data

        Raises:
            Exception: If the call fails after retries
        """
        # Initialize connection if needed
        self._initialize()

        # Prepare JSON-RPC message
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            }
        }

        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                self.rate_limiter.acquire()

                # Make request
                logger.debug(f"Calling MCP tool: {tool_name} (attempt {attempt + 1}/{self.max_retries})")
                response = self.client.post(self.base_url, json=message, headers=self._get_headers())

                # Handle 401 - token expired
                if response.status_code == 401:
                    logger.warning("Token expired, attempting refresh")
                    self.initialized = False  # Reset initialization
                    if self.auth_manager.refresh_token():
                        continue
                    else:
                        raise Exception("Failed to refresh authentication token")

                # Handle 429 - rate limited
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited by server, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue

                # Handle other errors
                if response.status_code >= 400:
                    error_msg = f"MCP call failed: {response.status_code} - {response.text[:200]}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                # Success - parse JSON-RPC response
                result = response.json()

                if "error" in result:
                    error_msg = f"MCP error: {result['error'].get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                if "result" not in result:
                    raise Exception("Invalid MCP response: missing 'result' field")

                logger.debug(f"MCP tool {tool_name} completed successfully")
                return result["result"]

            except httpx.TimeoutException:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise Exception(f"MCP call timed out after {self.max_retries} attempts")
                time.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Request failed: {e} (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(2 ** attempt)

        raise Exception(f"MCP call failed after {self.max_retries} attempts")

    def close(self):
        """Close the HTTP client."""
        self.client.close()
