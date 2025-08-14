from typing import Optional, Dict, Any
import time

import httpx


class LinkdAPI:
    """
    A high-level client for interacting with the LinkdAPI service.
    
    This client provides:
    - Automatic retry mechanism for failed requests
    - Type-annotated methods for better IDE support
    - Connection pooling for improved performance
    - Comprehensive error handling
    - Both context manager and direct usage patterns
    
    Basic Usage:
    -----------
    There are two recommended ways to use this client:
    
    1. Context Manager (Recommended for most cases):
    ```python
    with LinkdAPI(api_key="your_api_key") as api:
        profile = api.get_profile_overview("ryanroslansky")
        print(profile)
    ```
    
    2. Direct Instantiation (When you need long-lived clients):
    ```python
    api = LinkdAPI(api_key="your_api_key")
    try:
        profile = api.get_profile_overview("ryanroslansky")
        print(profile)
    finally:
        api.close()
    ```
    
    Args:
        api_key (str): Your LinkdAPI authentication key. Get one at https://linkdapi.com/?p=signup
        base_url (str): Base URL for the API (default: "https://linkdapi.com")
        timeout (float): Request timeout in seconds (default: 30)
        max_retries (int): Maximum retry attempts for failed requests (default: 3)
        retry_delay (float): Initial delay between retries in seconds (default: 1)
                         Note: Delay increases exponentially with each retry
    
    Raises:
        httpx.HTTPStatusError: For 4xx/5xx responses after all retries
        httpx.RequestError: For network-related errors after all retries
    
    Example:
    ```python
    # Basic usage with context manager
    with LinkdAPI(api_key="your_key") as api:
        try:
            # Get profile data
            profile = api.get_profile_overview("ryanroslansky")
            if profile.get("success", False):
                print(f"Profile Name: {profile['data']['fullName']}")
            
        except httpx.HTTPStatusError as e:
            print(f"API Error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Network Error: {str(e)}")
    ```
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://linkdapi.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=100)
        )

    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for API requests."""
        return {
            "X-linkdapi-apikey": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "LinkdAPI-Python-Client/1.0"
        }

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional arguments for httpx request
            
        Returns:
            Parsed JSON response
            
        Raises:
            httpx.HTTPStatusError: For 4xx/5xx responses after retries
            httpx.RequestError: For network-related errors after retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise last_exception

    def __enter__(self):
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up on context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client explicitly."""
        if hasattr(self, 'client'):
            self.client.close()

    def __del__(self):
        """Clean up when instance is garbage collected."""
        self.close()

    # Profile Endpoints
    def get_profile_overview(self, username: str) -> dict:
        """
        Get basic profile information by username.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/overview
        
        Args:
            username (str): The LinkedIn username to look up
            
        Returns:
            dict: Profile overview data
        """
        return self._send_request("GET", "api/v1/profile/overview", {"username": username})
    
    def get_profile_details(self, urn: str) -> dict:
        """
        Get profile details information by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/details
        
        Args:
            urn (str): The LinkedIn URN (Uniform Resource Name) for the profile
            
        Returns:
            dict: Detailed profile information
        """
        return self._send_request("GET", "api/v1/profile/details", {"urn": urn})
    
    def get_contact_info(self, username: str) -> dict:
        """
        Get contact details for a profile by username.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/contact-info
        
        Args:
            username (str): The LinkedIn username to look up
            
        Returns:
            dict: Contact information including email, phone, and websites
        """
        return self._send_request("GET", "api/v1/profile/contact-info", {"username": username})
    
    def get_full_experience(self, urn: str) -> dict:
        """
        Get complete work experience by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/full-experience
        
        Args:
            urn (str): The LinkedIn URN for the profile
            
        Returns:
            dict: Complete work experience information
        """
        return self._send_request("GET", "api/v1/profile/full-experience", {"urn": urn})
    
    def get_certifications(self, urn: str) -> dict:
        """
        Get lists of professional certifications by URN.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/certifications
        
        Args:
            urn (str): The LinkedIn URN for the profile
            
        Returns:
            dict: Certification information
        """
        return self._send_request("GET", "api/v1/profile/certifications", {"urn": urn})
    
    def get_education(self, urn: str) -> dict:
        """
        Get full education information by URN.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/education
        
        Args:
            urn (str): The LinkedIn URN for the profile
            
        Returns:
            dict: Education history
        """
        return self._send_request("GET", "api/v1/profile/education", {"urn": urn})
    
    def get_skills(self, urn: str) -> dict:
        """
        Get profile skills by URN.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/skills
        
        Args:
            urn (str): The LinkedIn URN for the profile
            
        Returns:
            dict: Skills information
        """
        return self._send_request("GET", "api/v1/profile/skills", {"urn": urn})
    
    def get_social_matrix(self, username: str) -> dict:
        """
        Get social network metrics by username.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/social-matrix
        
        Args:
            username (str): The LinkedIn username to look up
            
        Returns:
            dict: Social metrics including connections and followers count
        """
        return self._send_request("GET", "api/v1/profile/social-matrix", {"username": username})
    
    def get_recommendations(self, urn: str) -> dict:
        """
        Get profile given and received recommendations by URN.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/recommendations
        
        Args:
            urn (str): The LinkedIn URN for the profile
            
        Returns:
            dict: Recommendations data
        """
        return self._send_request("GET", "api/v1/profile/recommendations", {"urn": urn})
    
    def get_similar_profiles(self, urn: str) -> dict:
        """
        Get similar profiles for a given profile using its URN.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/similar
        
        Args:
            urn (str): The LinkedIn URN for the profile
            
        Returns:
            dict: List of similar profiles
        """
        return self._send_request("GET", "api/v1/profile/similar", {"urn": urn})
    
    def get_profile_about(self, urn: str) -> dict:
        """
        Get about this profile such as last update and verification info.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/about
        
        Args:
            urn (str): The LinkedIn URN for the profile
            
        Returns:
            dict: Profile about information
        """
        return self._send_request("GET", "api/v1/profile/about", {"urn": urn})
    
    def get_profile_reactions(self, urn: str, cursor: str = "") -> dict:
        """
        Get all reactions for given profile by URN.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/reactions
        
        Args:
            urn (str): The LinkedIn URN for the profile
            cursor (str, optional): Pagination cursor
            
        Returns:
            dict: Reactions data with pagination information
        """
        params = {"urn": urn}
        if cursor:
            params["cursor"] = cursor
        return self._send_request("GET", "api/v1/profile/reactions", params)
    
    # Posts Endpoints
    def get_featured_posts(self, urn: str) -> dict:
        """
        Get all featured posts for a given profile using its URN.
        
        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/posts/featured
        
        Args:
            urn (str): The LinkedIn URN for the profile
            
        Returns:
            dict: List of featured posts
        """
        return self._send_request("GET", "api/v1/posts/featured", {"urn": urn})
    
    def get_all_posts(self, urn: str, cursor: str = "", start: int = 0) -> dict:
        """
        Retrieve all posts for a given profile URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/posts/all
        
        Args:
            urn (str): The LinkedIn URN of the profile.
            cursor (str, optional): Pagination cursor (default is empty).
            start (int, optional): Start index for pagination (default is 0).

        Returns:
            dict: List of posts with pagination info.
        """
        return self._send_request("GET", "api/v1/posts/all", {"urn": urn, "cursor": cursor, "start": start})

    def get_post_info(self, urn: str) -> dict:
        """
        Retrieve information about a specific post using its URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/posts/info
        
        Args:
            urn (str): The URN of the LinkedIn post.

        Returns:
            dict: Detailed post information.
        """
        return self._send_request("GET", "api/v1/posts/info", {"urn": urn})

    def get_post_comments(self, urn: str, start: int = 0, count: int = 10, cursor: str = "") -> dict:
        """
        Get comments for a specific LinkedIn post.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/posts/comments
        
        Args:
            urn (str): The URN of the post.
            start (int, optional): Starting index for pagination.
            count (int, optional): Number of comments to fetch per request.
            cursor (str, optional): Cursor for pagination (default is empty).

        Returns:
            dict: A list of comments and pagination metadata.
        """
        return self._send_request("GET", "api/v1/posts/comments", {"urn": urn, "start": start, "count": count, "cursor": cursor})

    def get_post_likes(self, urn: str, start: int = 0) -> dict:
        """
        Retrieve all users who liked or reacted to a given post.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/posts/likes
        
        Args:
            urn (str): The URN of the LinkedIn post.
            start (int, optional): Pagination start index (default is 0).

        Returns:
            dict: List of users who liked/reacted to the post.
        """
        return self._send_request("GET", "api/v1/posts/likes", {"urn": urn, "start": start})

    # Comments Endpoints
    def get_all_comments(self, urn: str, cursor: str = "") -> dict:
        """
        Retrieve all comments made by a profile using their URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/comments/all
        
        Args:
            urn (str): The LinkedIn profile URN.
            cursor (str, optional): Pagination cursor (default is empty).

        Returns:
            dict: List of comments made by the user.
        """
        return self._send_request("GET", "api/v1/comments/all", {"urn": urn, "cursor": cursor})

    def get_comment_likes(self, urns: str, start: int = 0) -> dict:
        """
        Get all users who reacted to one or more comment URNs.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/comments/likes
        
        Args:
            urns (str): Comma-separated URNs of comments.
            start (int, optional): Pagination start index (default is 0).

        Returns:
            dict: List of users who liked or reacted to the comments.
        """
        return self._send_request("GET", "api/v1/comments/likes", {"urn": urns, "start": start})

    # Service Status Endpoint
    def get_service_status(self) -> dict:
        return self._send_request("GET", "status/")
    
    def __del__(self):
        """Clean up the HTTP client when the instance is destroyed."""
        self.client.close()
