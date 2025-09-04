from datetime import datetime
from typing import List
import pandas as pd

from api.ebay_client import EbayClient

client: EbayClient | None = None  # the CLI or main() will inject a live client

def compare_regions(
    queries: List[str],
    regions: List[str],
    start: datetime,
    end: datetime,
    metric: str = "sales_volume"  # 'sales_volume' or 'avg_price'
) -> pd.DataFrame:
    """Compare product performance across multiple eBay marketplaces.

    Parameters
    ----------
    queries : list[str]
        Search terms (e.g., ["playstation 2", "xbox 360"]).
    regions : list[str]
        eBay marketplace IDs (e.g., ["EBAY_US", "EBAY_GB"]).
    start, end : datetime
        UTC date window for the comparison.
    metric : str, optional
        Which metric to compute: 'sales_volume' (default) counts units sold;
        'avg_price' returns mean sold price.

    Returns
    -------
    pd.DataFrame
        Index = queries, Columns = regions, Values = metric chosen.
    """
    if client is None:
        raise RuntimeError("compare_regions() needs an injected EbayClient instance")

    result = pd.DataFrame(index=queries, columns=regions, dtype=float)

    for region in regions:
        for query in queries:
            resp = client.search_sales(query, start, end, marketplace=region)
            rows = resp.get("itemSales", [])

            if metric == "sales_volume":
                value = sum(item.get("quantitySold", 1) for item in rows)
            elif metric == "avg_price":
                prices = [float(item["price"]["value"]) for item in rows if "price" in item and "value" in item["price"]]
                value = sum(prices) / len(prices) if prices else 0
            else:
                raise ValueError("Unsupported metric: choose 'sales_volume' or 'avg_price'")

            result.loc[query, region] = value

    return result
