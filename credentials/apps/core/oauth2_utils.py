"""OAuth2 Service-to-Service Authentication Utilities."""

import logging
from django.conf import settings
from django.core.cache import cache
import requests

logger = logging.getLogger(__name__)

OAUTH2_TOKEN_CACHE_KEY = "oauth2_service_token"
OAUTH2_TOKEN_CACHE_TTL = 3300


def get_service_token():
    """
    Get inter-service JWT token using OAuth2 client credentials flow.
    
    Returns:
        str: Access token or None if retrieval fails.
    """
    cached_token = cache.get(OAUTH2_TOKEN_CACHE_KEY)
    if cached_token:
        logger.debug("Using cached OAuth2 token")
        return cached_token
    
    try:
        response = requests.post(
            settings.OAUTH2_SERVICE_TOKEN_URL,
            data={
                'grant_type': 'client_credentials',
                'client_id': settings.OAUTH2_SERVICE_CLIENT_ID,
                'client_secret': settings.OAUTH2_SERVICE_CLIENT_SECRET,
                'token_type': 'JWT',
            },
            timeout=5
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', OAUTH2_TOKEN_CACHE_TTL)
            
            cache.set(OAUTH2_TOKEN_CACHE_KEY, access_token, expires_in - 60)
            logger.info("Service token obtained successfully")
            return access_token
        else:
            logger.error(f"Failed to get service token: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error obtaining service token: {e}")
        return None


def get_oauth2_headers():
    """
    Get HTTP headers with OAuth2 JWT token.
    
    Returns:
        dict: Headers with Authorization JWT token.
    """
    token = get_service_token()
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'JWT {token}'
    
    return headers
