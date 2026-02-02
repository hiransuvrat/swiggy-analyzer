"""OAuth PKCE authentication manager for Swiggy MCP."""

import hashlib
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse
from typing import Optional, Dict
import threading

from authlib.integrations.requests_client import OAuth2Session
from loguru import logger

from .token_store import TokenStore


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    auth_code = None
    error = None

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        query = parse_qs(urlparse(self.path).query)

        if "code" in query:
            CallbackHandler.auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <script>window.close();</script>
                </body>
                </html>
            """)
        elif "error" in query:
            CallbackHandler.error = query["error"][0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>Error: {CallbackHandler.error}</p>
                </body>
                </html>
            """.encode())
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class OAuthManager:
    """Manages OAuth PKCE authentication flow."""

    SERVICE_NAME = "swiggy-instamart"
    AUTH_URL = "https://mcp.swiggy.com/auth/authorize"
    TOKEN_URL = "https://mcp.swiggy.com/auth/token"
    REDIRECT_URI = "http://localhost:3118/callback"
    CLIENT_ID = "swiggy-analyzer"  # This should be obtained from Swiggy
    SCOPES = ["read:orders", "write:basket"]

    def __init__(self, token_store: TokenStore):
        self.token_store = token_store

    def _generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge."""
        # Generate random code verifier (43-128 characters)
        code_verifier = secrets.token_urlsafe(64)

        # Generate code challenge (SHA256 hash of verifier)
        code_challenge = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = secrets.token_urlsafe(43)  # Base64 URL-safe encoding

        return code_verifier, code_challenge

    def _start_callback_server(self, port: int = 3118) -> HTTPServer:
        """Start local HTTP server for OAuth callback."""
        server = HTTPServer(("localhost", port), CallbackHandler)
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        return server

    def initiate_auth_flow(self) -> bool:
        """
        Initiate OAuth PKCE authentication flow.

        Returns:
            bool: True if authentication successful, False otherwise.
        """
        logger.info("Starting OAuth PKCE authentication flow")

        # Generate PKCE pair
        code_verifier, code_challenge = self._generate_pkce_pair()

        # Build authorization URL
        auth_params = {
            "client_id": self.CLIENT_ID,
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "scope": " ".join(self.SCOPES),
        }

        auth_url = f"{self.AUTH_URL}?{urlencode(auth_params)}"

        # Start callback server
        logger.info("Starting callback server on port 3118")
        CallbackHandler.auth_code = None
        CallbackHandler.error = None
        server = self._start_callback_server()

        # Open browser
        logger.info("Opening browser for authentication")
        print(f"\nOpening browser for authentication...")
        print(f"If browser doesn't open, visit: {auth_url}\n")
        webbrowser.open(auth_url)

        # Wait for callback
        print("Waiting for authentication callback...")
        server.handle_request()

        # Check result
        if CallbackHandler.error:
            logger.error(f"Authentication failed: {CallbackHandler.error}")
            return False

        if not CallbackHandler.auth_code:
            logger.error("No authorization code received")
            return False

        # Exchange code for tokens
        logger.info("Exchanging authorization code for tokens")
        return self._exchange_code_for_tokens(CallbackHandler.auth_code, code_verifier)

    def _exchange_code_for_tokens(self, auth_code: str, code_verifier: str) -> bool:
        """Exchange authorization code for access and refresh tokens."""
        token_params = {
            "client_id": self.CLIENT_ID,
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.REDIRECT_URI,
            "code_verifier": code_verifier,
        }

        try:
            session = OAuth2Session(client_id=self.CLIENT_ID)
            token = session.fetch_token(
                self.TOKEN_URL,
                grant_type="authorization_code",
                code=auth_code,
                code_verifier=code_verifier,
            )

            # Save tokens
            self.token_store.save_token(
                service=self.SERVICE_NAME,
                access_token=token["access_token"],
                refresh_token=token.get("refresh_token"),
                expires_in=token.get("expires_in"),
                token_type=token.get("token_type", "Bearer"),
            )

            logger.info("Successfully obtained and saved tokens")
            return True

        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            return False

    def refresh_token(self) -> bool:
        """Refresh access token using refresh token."""
        token_data = self.token_store.get_token(self.SERVICE_NAME)
        if not token_data or not token_data.get("refresh_token"):
            logger.error("No refresh token available")
            return False

        try:
            session = OAuth2Session(client_id=self.CLIENT_ID)
            token = session.refresh_token(
                self.TOKEN_URL,
                refresh_token=token_data["refresh_token"],
            )

            # Save new tokens
            self.token_store.save_token(
                service=self.SERVICE_NAME,
                access_token=token["access_token"],
                refresh_token=token.get("refresh_token", token_data["refresh_token"]),
                expires_in=token.get("expires_in"),
                token_type=token.get("token_type", "Bearer"),
            )

            logger.info("Successfully refreshed access token")
            return True

        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return False

    def get_valid_token(self) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            str: Valid access token or None if authentication required.
        """
        if self.token_store.is_token_valid(self.SERVICE_NAME):
            token_data = self.token_store.get_token(self.SERVICE_NAME)
            return token_data["access_token"]

        # Try to refresh
        if self.refresh_token():
            token_data = self.token_store.get_token(self.SERVICE_NAME)
            return token_data["access_token"]

        logger.warning("No valid token available, authentication required")
        return None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.token_store.is_token_valid(self.SERVICE_NAME)

    def logout(self):
        """Remove stored tokens."""
        self.token_store.delete_token(self.SERVICE_NAME)
        logger.info("Logged out successfully")
