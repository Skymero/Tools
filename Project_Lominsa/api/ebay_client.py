"""
REASONING & DESIGN CHOICES
--------------------------
This module implements a high-level HTTP wrapper for the eBay Marketplace Insights API.

Key design goals:
1. **Separation of Concerns:**
   - Token management is delegated to EbayAuth, so this client never deals with credentials directly.
   - The client only requests tokens as needed and always uses valid, fresh tokens for API calls.
2. **Usability:**
   - The public interface (`search_sales`) is simple: you provide a query and date range, and get all sold items as a list of dicts.
   - Pagination is handled transparently, so users never have to deal with offsets or page sizes.
   - Dates can be provided as strings or `datetime` objects for flexibility.
3. **Robustness:**
   - Raises clear exceptions (`ApiError`) for non-200 responses, so error handling is explicit.
   - All HTTP requests have sensible timeouts.
   - All returned data is parsed JSON (never raw text).
4. **Security:**
   - No credentials or tokens are stored in this file; only a runtime token is used per request.
   - Only the minimum required headers are sent.


How and When to Use These Objects:
------------------------------------------------------
Suppose you want to get a list of items that have recently sold on eBay, but you don't want to worry about how to log in, how to get a token, or how to deal with multiple pages of results. This file gives you a simple way to do that! You just create an EbayAuth object (which handles all the login/token stuff for you), then create an EbayClient object using that EbayAuth. After that, you can call the search_sales function to get all the data you want as a normal Python list—no need to deal with the details of HTTP requests, tokens, or eBay's complicated API.

When should you use this? Any time you want to get sold-item data from eBay for analysis, reporting, or automation. This is the only thing you need to import for most eBay data tasks in this project.

Example: Calling a Function from This File (step-by-step)
---------------------------------------------------------
Let's say you want to find all PlayStation 2 consoles sold in the last week. Here's how you would do it, even if you've never used classes in Python before:

```python
from auth.ebay_auth import EbayAuth  # This handles the login/token
from api.ebay_client import EbayClient  # This is the main client
from datetime import datetime, timedelta  # For working with dates

# Step 1: Create an EbayAuth object (this reads your credentials from .env)
auth = EbayAuth()

# Step 2: Create an EbayClient object, passing in your auth object
client = EbayClient(auth)

# Step 3: Call the search_sales() function to get sold items
# We'll look for "playstation 2" sold in the last 7 days
results = client.search_sales(
    query="playstation 2",
    start=datetime.utcnow() - timedelta(days=7),  # 7 days ago
    end=datetime.utcnow()  # now
)

# Step 4: Print how many results we got
print(f"Found {len(results)} sold items!")
```

You don't need to know how the token works, or how to build the URL—the client handles it all for you!

 This approach makes it easy to build analytics and automation on top of eBay's API without exposing sensitive logic or requiring users to understand OAuth2 or pagination.
"""

from datetime import datetime  # Import datetime for date handling
from typing import Union, List, Dict  # Import type hints for function signatures
import requests  # Import requests for HTTP communication
from auth.ebay_auth import EbayAuth  # Import EbayAuth for OAuth2 token management

class ApiError(Exception):  # Define a custom exception for API errors
    """Raised when eBay API returns non‑200"""
    pass  # No extra logic needed; used for clarity in error handling

class EbayClient:
    BASE = "https://api.ebay.com/buy/marketplace_insights/v1_beta"  # Base URL for eBay Marketplace Insights API

    def __init__(self, auth: EbayAuth):  # Constructor expects an EbayAuth instance
        """
        Parameters
        ----------
        auth : EbayAuth
            An EbayAuth instance that manages OAuth2 tokens.
        """
        self.auth = auth  # Store the auth object for token retrieval

    def _request(self, endpoint: str, params: dict) -> dict:
        """
        Internal helper for GET requests with bearer token.
        Raises ApiError on non-200.
        """
        # Build the HTTP headers with the current OAuth2 bearer token
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}  # Always get a fresh token
        # Compose the full URL and send the GET request with params and headers
        resp    = requests.get(f"{self.BASE}{endpoint}", params=params, headers=headers, timeout=30)
        # If the response is not HTTP 200 OK, raise a custom ApiError with the response body
        if resp.status_code != 200:
            raise ApiError(resp.text)
        # Otherwise, parse and return the JSON response as a Python dict
        return resp.json()

    def search_sales(
        self,
        query: str,
        start: Union[str, datetime],
        end:   Union[str, datetime],
        marketplace: str = "EBAY_US"
    ) -> List[Dict]:
        """
        Search for sold items on eBay within a date range and query.
        Handles pagination and returns all results as a list of dicts.
        
        Parameters
        ----------
        query : str
            Search query string (keywords)
        start : str or datetime
            Start date/time (ISO-8601 or datetime)
        end : str or datetime
            End date/time (ISO-8601 or datetime)
        marketplace : str
            eBay marketplace ID (default: 'EBAY_US')

        Returns
        -------
        List[dict]
            List of sold item records (may be empty)
        """
        # If start is a datetime object, convert to ISO-8601 string as required by eBay API
        if isinstance(start, datetime):
            start = start.strftime("%Y-%m-%dT%H:%M:%SZ")  # Format: 2023-01-01T00:00:00Z
        # If end is a datetime object, convert to ISO-8601 string
        if isinstance(end, datetime):
            end   = end.strftime("%Y-%m-%dT%H:%M:%SZ")

        items = []        # List to collect all sold items
        page = 0          # Track pagination offset
        BATCH = 200       # eBay API max limit per page
        while True:       # Loop until no more pages
            params = {
                "q"     : query,  # Search keywords
                "filter": f"marketplaceIds:{marketplace},soldDate:[{start}..{end}]",  # Marketplace and date filter
                "limit" : BATCH,  # Max results per page
                "offset": page * BATCH  # Offset for pagination
            }
            # Make the API request for this page
            chunk = self._request("/item_sales/search", params)
            # Add all returned items to our list
            items.extend(chunk.get("itemSales", []))
            # If fewer than BATCH results, we've reached the last page
            if len(chunk.get("itemSales", [])) < BATCH:
                break  # Exit loop: no more data
            page += 1  # Otherwise, increment page and continue
        return items  # Return all collected sold items as a list
