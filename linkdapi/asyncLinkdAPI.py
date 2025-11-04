from typing import Optional, Dict, Any, List, Union
import asyncio

import httpx


class AsyncLinkdAPI:
    """
    An async high-level client for interacting with the LinkdAPI service.

    This async client provides the same functionality as LinkdAPI but with async/await support:
    - Automatic retry mechanism for failed requests
    - Type-annotated methods for better IDE support
    - Connection pooling for improved performance
    - Comprehensive error handling
    - Async context manager support

    Basic Usage:
    -----------
    The recommended way to use this client is with async context manager:

    ```python
    async with AsyncLinkdAPI(api_key="your_api_key") as api:
        profile = await api.get_profile_overview("ryanroslansky")
        print(profile)
    ```

    Or for long-lived clients:
    ```python
    api = AsyncLinkdAPI(api_key="your_api_key")
    try:
        profile = await api.get_profile_overview("ryanroslansky")
        print(profile)
    finally:
        await api.close()
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
    import asyncio

    async def main():
        async with AsyncLinkdAPI(api_key="your_key") as api:
            try:
                # Get profile data
                profile = await api.get_profile_overview("ryanroslansky")
                if profile.get("success", False):
                    print(f"Profile Name: {profile['data']['fullName']}")

            except httpx.HTTPStatusError as e:
                print(f"API Error: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                print(f"Network Error: {str(e)}")

    asyncio.run(main())
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
        self.client = httpx.AsyncClient(
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

    async def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send an async HTTP request with retry logic.

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
                response = await self.client.request(
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
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise last_exception

    async def __aenter__(self):
        """Support async context manager protocol."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up on async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client explicitly."""
        if hasattr(self, 'client'):
            await self.client.aclose()

    def __del__(self):
        """Clean up when instance is garbage collected."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except Exception:
            pass

    # Profile Endpoints
    async def get_profile_overview(self, username: str) -> dict:
        """
        Get basic profile information by username.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/overview

        Args:
            username (str): The LinkedIn username to look up

        Returns:
            dict: Profile overview data
        """
        return await self._send_request("GET", "api/v1/profile/overview", {"username": username})

    async def get_profile_details(self, urn: str) -> dict:
        """
        Get profile details information by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/details

        Args:
            urn (str): The LinkedIn URN (Uniform Resource Name) for the profile

        Returns:
            dict: Detailed profile information
        """
        return await self._send_request("GET", "api/v1/profile/details", {"urn": urn})

    async def get_contact_info(self, username: str) -> dict:
        """
        Get contact details for a profile by username.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/contact-info

        Args:
            username (str): The LinkedIn username to look up

        Returns:
            dict: Contact information including email, phone, and websites
        """
        return await self._send_request("GET", "api/v1/profile/contact-info", {"username": username})

    async def get_full_experience(self, urn: str) -> dict:
        """
        Get complete work experience by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/full-experience

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: Complete work experience information
        """
        return await self._send_request("GET", "api/v1/profile/full-experience", {"urn": urn})

    async def get_certifications(self, urn: str) -> dict:
        """
        Get lists of professional certifications by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/certifications

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: Certification information
        """
        return await self._send_request("GET", "api/v1/profile/certifications", {"urn": urn})

    async def get_education(self, urn: str) -> dict:
        """
        Get full education information by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/education

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: Education history
        """
        return await self._send_request("GET", "api/v1/profile/education", {"urn": urn})

    async def get_skills(self, urn: str) -> dict:
        """
        Get profile skills by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/skills

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: Skills information
        """
        return await self._send_request("GET", "api/v1/profile/skills", {"urn": urn})

    async def get_social_matrix(self, username: str) -> dict:
        """
        Get social network metrics by username.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/social-matrix

        Args:
            username (str): The LinkedIn username to look up

        Returns:
            dict: Social metrics including connections and followers count
        """
        return await self._send_request("GET", "api/v1/profile/social-matrix", {"username": username})

    async def get_recommendations(self, urn: str) -> dict:
        """
        Get profile given and received recommendations by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/recommendations

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: Recommendations data
        """
        return await self._send_request("GET", "api/v1/profile/recommendations", {"urn": urn})

    async def get_similar_profiles(self, urn: str) -> dict:
        """
        Get similar profiles for a given profile using its URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/similar

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: List of similar profiles
        """
        return await self._send_request("GET", "api/v1/profile/similar", {"urn": urn})

    async def get_profile_about(self, urn: str) -> dict:
        """
        Get about this profile such as last update and verification info.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/about

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: Profile about information
        """
        return await self._send_request("GET", "api/v1/profile/about", {"urn": urn})

    async def get_profile_reactions(self, urn: str, cursor: str = "") -> dict:
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
        return await self._send_request("GET", "api/v1/profile/reactions", params)

    async def get_profile_interests(self, urn: str) -> dict:
        """
        Get profile interests by URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/profile/interests

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: Profile interests information
        """
        return await self._send_request("GET", "api/v1/profile/interests", {"urn": urn})

    # Posts Endpoints
    async def get_featured_posts(self, urn: str) -> dict:
        """
        Get all featured posts for a given profile using its URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/posts/featured

        Args:
            urn (str): The LinkedIn URN for the profile

        Returns:
            dict: List of featured posts
        """
        return await self._send_request("GET", "api/v1/posts/featured", {"urn": urn})

    async def get_all_posts(self, urn: str, cursor: str = "", start: int = 0) -> dict:
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
        return await self._send_request("GET", "api/v1/posts/all", {"urn": urn, "cursor": cursor, "start": start})

    async def get_post_info(self, urn: str) -> dict:
        """
        Retrieve information about a specific post using its URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/posts/info

        Args:
            urn (str): The URN of the LinkedIn post.

        Returns:
            dict: Detailed post information.
        """
        return await self._send_request("GET", "api/v1/posts/info", {"urn": urn})

    async def get_post_comments(self, urn: str, start: int = 0, count: int = 10, cursor: str = "") -> dict:
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
        return await self._send_request("GET", "api/v1/posts/comments", {"urn": urn, "start": start, "count": count, "cursor": cursor})

    async def get_post_likes(self, urn: str, start: int = 0) -> dict:
        """
        Retrieve all users who liked or reacted to a given post.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/posts/likes

        Args:
            urn (str): The URN of the LinkedIn post.
            start (int, optional): Pagination start index (default is 0).

        Returns:
            dict: List of users who liked/reacted to the post.
        """
        return await self._send_request("GET", "api/v1/posts/likes", {"urn": urn, "start": start})

    # Comments Endpoints
    async def get_all_comments(self, urn: str, cursor: str = "") -> dict:
        """
        Retrieve all comments made by a profile using their URN.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/comments/all

        Args:
            urn (str): The LinkedIn profile URN.
            cursor (str, optional): Pagination cursor (default is empty).

        Returns:
            dict: List of comments made by the user.
        """
        return await self._send_request("GET", "api/v1/comments/all", {"urn": urn, "cursor": cursor})

    async def get_comment_likes(self, urns: str, start: int = 0) -> dict:
        """
        Get all users who reacted to one or more comment URNs.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/comments/likes

        Args:
            urns (str): Comma-separated URNs of comments.
            start (int, optional): Pagination start index (default is 0).

        Returns:
            dict: List of users who liked or reacted to the comments.
        """
        return await self._send_request("GET", "api/v1/comments/likes", {"urn": urns, "start": start})

    # Service Status Endpoint
    async def get_service_status(self) -> dict:
        return await self._send_request("GET", "status/")

    # Companies Endpoints
    async def company_name_lookup(self, query: str) -> dict:
        """
        Search companies by name.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/companies/name-lookup

        Args:
            query (str): The search query (can be 1 character or multiple)

        Returns:
            dict: List of matching companies
        """
        return await self._send_request("GET", "api/v1/companies/name-lookup", {"query": query})

    async def get_company_info(self, company_id: Optional[str] = None, name: Optional[str] = None) -> dict:
        """
        Get company details either by ID or name.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/companies/company/info

        Args:
            company_id (str, optional): Company ID
            name (str, optional): Company name

        Returns:
            dict: Company details information

        Raises:
            ValueError: If neither company_id nor name is provided
        """
        if not company_id and not name:
            raise ValueError("Either company_id or name must be provided")

        params = {}
        if company_id:
            params["id"] = company_id
        if name:
            params["name"] = name

        return await self._send_request("GET", "api/v1/companies/company/info", params)

    async def get_similar_companies(self, company_id: str) -> dict:
        """
        Get similar companies by ID.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/companies/company/similar

        Args:
            company_id (str): Company ID

        Returns:
            dict: List of similar companies
        """
        return await self._send_request("GET", "api/v1/companies/company/similar", {"id": company_id})

    async def get_company_employees_data(self, company_id: str) -> dict:
        """
        Get company employees data by ID.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/companies/company/employees-data

        Args:
            company_id (str): Company ID

        Returns:
            dict: Company employees data
        """
        return await self._send_request("GET", "api/v1/companies/company/employees-data", {"id": company_id})

    async def get_company_jobs(self, company_ids: Union[str, List[str]], start: int = 0) -> dict:
        """
        Get available job listings for given companies by ID.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/companies/jobs

        Args:
            company_ids (str or list): Company ID(s) - can be a single ID or list of IDs
            start (int, optional): Pagination start index (default is 0)

        Returns:
            dict: List of job listings for the specified companies
        """
        if isinstance(company_ids, list):
            company_ids = ",".join(company_ids)
        return await self._send_request("GET", "api/v1/companies/jobs", {"companyIDs": company_ids, "start": start})

    async def get_company_affiliated_pages(self, company_id: str) -> dict:
        """
        Get affiliated pages/subsidiaries of a company by ID.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/companies/company/affiliated-pages

        Args:
            company_id (str): Company ID

        Returns:
            dict: List of affiliated pages and subsidiaries
        """
        return await self._send_request("GET", "api/v1/companies/company/affiliated-pages", {"id": company_id})

    # Jobs Endpoints
    async def search_jobs(
        self,
        *,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        geo_id: Optional[str] = None,
        company_ids: Optional[Union[str, List[str]]] = None,
        job_types: Optional[Union[str, List[str]]] = None,
        experience: Optional[Union[str, List[str]]] = None,
        regions: Optional[Union[str, List[str]]] = None,
        time_posted: str = "any",
        salary: Optional[str] = None,
        work_arrangement: Optional[Union[str, List[str]]] = None,
        start: int = 0
    ) -> dict:
        """
        Search for jobs with various filters.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/jobs/search

        Args:
            keyword (str, optional): Job title, skills, or keywords
            location (str, optional): City, state, or region
            geo_id (str, optional): LinkedIn's internal geographic identifier
            company_ids (str or list, optional): Specific company LinkedIn IDs
            job_types (str or list, optional): Employment types (full_time, part_time, contract, temporary, internship, volunteer)
            experience (str or list, optional): Experience levels (internship, entry_level, associate, mid_senior, director)
            regions (str or list, optional): Specific region codes
            time_posted (str, optional): How recently posted (any, 24h, 1week, 1month)
            salary (str, optional): Minimum salary (any, 40k, 60k, 80k, 100k, 120k)
            work_arrangement (str or list, optional): Work arrangement (onsite, remote, hybrid)
            start (int, optional): Pagination start index

        Returns:
            dict: List of job search results
        """
        params = {"start": start}

        if keyword:
            params["keyword"] = keyword
        if location:
            params["location"] = location
        if geo_id:
            params["geoId"] = geo_id
        if company_ids:
            if isinstance(company_ids, list):
                params["companyIds"] = ",".join(company_ids)
            else:
                params["companyIds"] = company_ids
        if job_types:
            if isinstance(job_types, list):
                params["jobTypes"] = ",".join(job_types)
            else:
                params["jobTypes"] = job_types
        if experience:
            if isinstance(experience, list):
                params["experience"] = ",".join(experience)
            else:
                params["experience"] = experience
        if regions:
            if isinstance(regions, list):
                params["regions"] = ",".join(regions)
            else:
                params["regions"] = regions
        if time_posted:
            params["timePosted"] = time_posted
        if salary:
            params["salary"] = salary
        if work_arrangement:
            if isinstance(work_arrangement, list):
                params["workArrangement"] = ",".join(work_arrangement)
            else:
                params["workArrangement"] = work_arrangement

        return await self._send_request("GET", "api/v1/jobs/search", params)

    async def get_job_details(self, job_id: str) -> dict:
        """
        Get job details by job ID.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/jobs/job/details

        Args:
            job_id (str): Job ID (must be open and actively hiring)

        Returns:
            dict: Detailed job information
        """
        return await self._send_request("GET", "api/v1/jobs/job/details", {"jobId": job_id})

    async def get_similar_jobs(self, job_id: str) -> dict:
        """
        Get similar jobs by job ID.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/jobs/job/similar

        Args:
            job_id (str): Job ID

        Returns:
            dict: List of similar jobs
        """
        return await self._send_request("GET", "api/v1/jobs/job/similar", {"jobId": job_id})

    async def get_people_also_viewed_jobs(self, job_id: str) -> dict:
        """
        Get related jobs that people also viewed.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/jobs/job/people-also-viewed

        Args:
            job_id (str): Job ID

        Returns:
            dict: List of related jobs
        """
        return await self._send_request("GET", "api/v1/jobs/job/people-also-viewed", {"jobId": job_id})

    # Geos Lookup Endpoints
    async def geo_name_lookup(self, query: str) -> dict:
        """
        Search locations and get geo IDs.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/geos/name-lookup

        Args:
            query (str): The search query (can be 1 character or multiple)

        Returns:
            dict: List of matching locations with geo IDs
        """
        return await self._send_request("GET", "api/v1/geos/name-lookup", {"query": query})

    # Search Endpoints
    async def search_people(
        self,
        *,
        keyword: Optional[str] = None,
        start: int = 0,
        current_company: Optional[Union[str, List[str]]] = None,
        first_name: Optional[str] = None,
        geo_urn: Optional[Union[str, List[str]]] = None,
        industry: Optional[Union[str, List[str]]] = None,
        last_name: Optional[str] = None,
        profile_language: Optional[str] = None,
        past_company: Optional[Union[str, List[str]]] = None,
        school: Optional[Union[str, List[str]]] = None,
        service_category: Optional[str] = None,
        title: Optional[str] = None
    ) -> dict:
        """
        Search for people with various filters.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/search/people

        Args:
            keyword (str, optional): Search keyword (e.g., "software engineer")
            start (int, optional): Pagination start index (default is 0)
            current_company (str or list, optional): Current company IDs (comma-separated or list)
            first_name (str, optional): First name filter
            geo_urn (str or list, optional): Geographic URNs (comma-separated or list)
            industry (str or list, optional): Industry IDs (comma-separated or list)
            last_name (str, optional): Last name filter
            profile_language (str, optional): Profile language (e.g., "en" for English)
            past_company (str or list, optional): Past company IDs (comma-separated or list)
            school (str or list, optional): School IDs (comma-separated or list)
            service_category (str, optional): Service category ID
            title (str, optional): Job title (e.g., "founder")

        Returns:
            dict: List of people matching the search criteria
        """
        params = {"start": start}

        if keyword:
            params["keyword"] = keyword
        if current_company:
            if isinstance(current_company, list):
                params["currentCompany"] = ",".join(current_company)
            else:
                params["currentCompany"] = current_company
        if first_name:
            params["firstName"] = first_name
        if geo_urn:
            if isinstance(geo_urn, list):
                params["geoUrn"] = ",".join(geo_urn)
            else:
                params["geoUrn"] = geo_urn
        if industry:
            if isinstance(industry, list):
                params["industry"] = ",".join(industry)
            else:
                params["industry"] = industry
        if last_name:
            params["lastName"] = last_name
        if profile_language:
            params["profileLanguage"] = profile_language
        if past_company:
            if isinstance(past_company, list):
                params["pastCompany"] = ",".join(past_company)
            else:
                params["pastCompany"] = past_company
        if school:
            if isinstance(school, list):
                params["school"] = ",".join(school)
            else:
                params["school"] = school
        if service_category:
            params["serviceCategory"] = service_category
        if title:
            params["title"] = title

        return await self._send_request("GET", "api/v1/search/people", params)

    async def search_companies(
        self,
        *,
        keyword: Optional[str] = None,
        start: int = 0,
        geo_urn: Optional[Union[str, List[str]]] = None,
        company_size: Optional[Union[str, List[str]]] = None,
        has_jobs: Optional[bool] = None,
        industry: Optional[Union[str, List[str]]] = None
    ) -> dict:
        """
        Search for companies with various filters.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/search/companies

        Args:
            keyword (str, optional): Search keyword (e.g., "software")
            start (int, optional): Pagination start index (default is 0)
            geo_urn (str or list, optional): Geographic URNs (comma-separated or list)
            company_size (str or list, optional): Company sizes (e.g., "1-10", "11-50", "51-200")
            has_jobs (bool, optional): Filter companies with job listings
            industry (str or list, optional): Industry IDs (comma-separated or list)

        Returns:
            dict: List of companies matching the search criteria
        """
        params = {"start": start}

        if keyword:
            params["keyword"] = keyword
        if geo_urn:
            if isinstance(geo_urn, list):
                params["geoUrn"] = ",".join(geo_urn)
            else:
                params["geoUrn"] = geo_urn
        if company_size:
            if isinstance(company_size, list):
                params["companySize"] = ",".join(company_size)
            else:
                params["companySize"] = company_size
        if has_jobs is not None:
            params["hasJobs"] = str(has_jobs).lower()
        if industry:
            if isinstance(industry, list):
                params["industry"] = ",".join(industry)
            else:
                params["industry"] = industry

        return await self._send_request("GET", "api/v1/search/companies", params)

    async def search_services(
        self,
        *,
        keyword: Optional[str] = None,
        start: int = 0,
        geo_urn: Optional[Union[str, List[str]]] = None,
        profile_language: Optional[str] = None,
        service_category: Optional[Union[str, List[str]]] = None
    ) -> dict:
        """
        Search for services offered by LinkedIn members.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/search/services

        Args:
            keyword (str, optional): Search keyword (e.g., "software")
            start (int, optional): Pagination start index (default is 0)
            geo_urn (str or list, optional): Geographic URNs (comma-separated or list)
            profile_language (str, optional): Profile language (e.g., "en,ch")
            service_category (str or list, optional): Service category IDs (comma-separated or list)

        Returns:
            dict: List of services matching the search criteria
        """
        params = {"start": start}

        if keyword:
            params["keyword"] = keyword
        if geo_urn:
            if isinstance(geo_urn, list):
                params["geoUrn"] = ",".join(geo_urn)
            else:
                params["geoUrn"] = geo_urn
        if profile_language:
            params["profileLanguage"] = profile_language
        if service_category:
            if isinstance(service_category, list):
                params["serviceCategory"] = ",".join(service_category)
            else:
                params["serviceCategory"] = service_category

        return await self._send_request("GET", "api/v1/search/services", params)

    async def search_schools(self, keyword: Optional[str] = None, start: int = 0) -> dict:
        """
        Search for educational institutions/schools.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/search/schools

        Args:
            keyword (str, optional): Search keyword (e.g., "software")
            start (int, optional): Pagination start index (default is 0)

        Returns:
            dict: List of schools matching the search criteria
        """
        params = {"start": start}
        if keyword:
            params["keyword"] = keyword
        return await self._send_request("GET", "api/v1/search/schools", params)

    async def search_posts(
        self,
        *,
        keyword: Optional[str] = None,
        start: int = 10,
        author_company: Optional[str] = None,
        author_industry: Optional[str] = None,
        author_job_title: Optional[str] = None,
        content_type: Optional[str] = None,
        date_posted: Optional[str] = None,
        from_member: Optional[str] = None,
        from_organization: Optional[Union[str, List[str]]] = None,
        mentions_member: Optional[str] = None,
        mentions_organization: Optional[Union[str, List[str]]] = None,
        sort_by: str = "relevance"
    ) -> dict:
        """
        Search for LinkedIn posts with various filters.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/search/posts

        Args:
            keyword (str, optional): Search keyword (e.g., "google")
            start (int, optional): Pagination start index (default is 10)
            author_company (str, optional): Company ID of the post author
            author_industry (str, optional): Industry ID of the post author
            author_job_title (str, optional): Job title of the post author (e.g., "founder")
            content_type (str, optional): Content type (videos, photos, jobs, liveVideos, documents, collaborativeArticles)
            date_posted (str, optional): Date filter (past-24h, past-week, past-month, past-year)
            from_member (str, optional): Profile URN of the post author
            from_organization (str or list, optional): Company IDs (comma-separated or list)
            mentions_member (str, optional): Profile URN mentioned in posts
            mentions_organization (str or list, optional): Company IDs mentioned (comma-separated or list)
            sort_by (str, optional): Sort order (relevance, date_posted) - default is "relevance"

        Returns:
            dict: List of posts matching the search criteria
        """
        params = {"start": start, "sortBy": sort_by}

        if keyword:
            params["keyword"] = keyword
        if author_company:
            params["authorCompany"] = author_company
        if author_industry:
            params["authorIndustry"] = author_industry
        if author_job_title:
            params["authorJobTitle"] = author_job_title
        if content_type:
            params["contentType"] = content_type
        if date_posted:
            params["datePosted"] = date_posted
        if from_member:
            params["fromMember"] = from_member
        if from_organization:
            if isinstance(from_organization, list):
                params["fromOrganization"] = ",".join(from_organization)
            else:
                params["fromOrganization"] = from_organization
        if mentions_member:
            params["mentionsMember"] = mentions_member
        if mentions_organization:
            if isinstance(mentions_organization, list):
                params["mentionsOrganization"] = ",".join(mentions_organization)
            else:
                params["mentionsOrganization"] = mentions_organization

        return await self._send_request("GET", "api/v1/search/posts", params)

    # Skills & Titles Lookup Endpoints
    async def title_skills_lookup(self, query: str) -> dict:
        """
        Search for keywords and get relevant skills and titles with their IDs.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/g/title-skills-lookup

        Args:
            query (str): Search query

        Returns:
            dict: List of relevant skills and titles with IDs
        """
        return await self._send_request("GET", "api/v1/g/title-skills-lookup", {"query": query})

    async def services_lookup(self, query: str) -> dict:
        """
        Look up service categories and return matching services.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/g/services-lookup

        Args:
            query (str): Search query for services (e.g., "software")

        Returns:
            dict: List of matching service categories with IDs
        """
        return await self._send_request("GET", "api/v1/g/services-lookup", {"query": query})

    # Articles Endpoints
    async def get_all_articles(self, urn: str, start: int = 0) -> dict:
        """
        Get all articles published by a specific LinkedIn profile.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/articles/all

        Args:
            urn (str): The LinkedIn profile URN
            start (int, optional): Pagination start index (default is 0)

        Returns:
            dict: List of articles published by the profile
        """
        return await self._send_request("GET", "api/v1/articles/all", {"urn": urn, "start": start})

    async def get_article_info(self, url: str) -> dict:
        """
        Get detailed information about a specific LinkedIn article.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/articles/article/info

        Args:
            url (str): Full LinkedIn article URL (e.g., "https://www.linkedin.com/pulse/...")

        Returns:
            dict: Detailed article information
        """
        return await self._send_request("GET", "api/v1/articles/article/info", {"url": url})

    async def get_article_reactions(self, urn: str, start: int = 0) -> dict:
        """
        Get reactions (likes, comments, etc.) for a specific LinkedIn article.

        Documentation: https://linkdapi.com/docs?endpoint=/api/v1/articles/article/reactions

        Args:
            urn (str): Article/thread URN (obtained from get_article_info)
            start (int, optional): Pagination start index (default is 0)

        Returns:
            dict: Reactions data for the article
        """
        return await self._send_request("GET", "api/v1/articles/article/reactions", {"urn": urn, "start": start})
    