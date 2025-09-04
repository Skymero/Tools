"""price_graph.py
Utility to quickly visualise price trends and save the resulting image.

This module exposes a single helper:

    plot_price_trend(df, title, filename=None)

which takes a DataFrame containing at least the columns `date_sold` (any
string/datetime convertible to pandas datetime) and `price` (numeric),
generates a simple line chart of price vs. date, saves it under
`output/graphs/` and returns the absolute path to the generated file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------------------
# Constants / Paths
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("output/graphs")
# Ensure the output directory exists so callers do not have to.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def plot_price_trend(df: pd.DataFrame, title: str, filename: Optional[str] | None = None) -> str:  # noqa: D401, WPS110
    """Generate and save a price-trend line graph.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain at least two columns: ``date_sold`` and ``price``.
    title : str
        Human-readable title (e.g. *PlayStation 5*). Will be displayed in
        the chart and also used to auto-generate the output filename when
        *filename* is *None*.
    filename : str | None, optional
        Custom filename **without** parent directory. The directory will
        always be ``output/graphs``. When *None* (default) the filename is
        generated from *title* by lower-casing and replacing spaces with
        underscores, suffixed with ``_price.png``.

    Returns
    -------
    str
        Absolute path to the saved image (PNG by default).

    Examples
    --------
    >>> import pandas as pd
    >>> from analytics.price_graph import plot_price_trend
    >>> df = pd.DataFrame({
    ...     "date_sold": ["2024-06-01", "2024-06-15", "2024-07-01"],
    ...     "price": [120, 110, 130],
    ... })
    >>> fp = plot_price_trend(df, "PlayStation 2")
    >>> print(fp)
    output/graphs/playstation_2_price.png
    """

    # -------------------------------------------------------------------
    # 1. Sanity checks & copy – keep original df untouched.
    # -------------------------------------------------------------------
    if not {"date_sold", "price"}.issubset(df.columns):
        raise ValueError("`df` must contain `date_sold` and `price` columns")

    data = df.copy()

    # -------------------------------------------------------------------
    # 2. Pre-process dates & ordering.
    # -------------------------------------------------------------------
    data["date_sold"] = pd.to_datetime(data["date_sold"], errors="coerce")
    data = data.sort_values("date_sold").dropna(subset=["date_sold", "price"])

    if data.empty:
        raise ValueError("`df` resulted in an empty frame after cleaning – nothing to plot.")

    # -------------------------------------------------------------------
    # 3. Figure creation.
    # -------------------------------------------------------------------
    plt.figure(figsize=(10, 5))
    plt.plot(data["date_sold"], data["price"], marker="o", linestyle="-")
    plt.title(f"Price Trend – {title}")
    plt.xlabel("Date Sold")
    plt.ylabel("Price (USD)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # -------------------------------------------------------------------
    # 4. Determine filename & save.
    # -------------------------------------------------------------------
    if filename is not None:
        out_name = filename
    else:
        slug = _slugify(title)
        out_name = f"{slug}_price.png"

    outfile: Path = OUTPUT_DIR / out_name
    plt.savefig(outfile, dpi=150)
    plt.close()

    return str(outfile.resolve())


# ---------------------------------------------------------------------------
# Helper functions (private)
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Very small helper for *good-enough* slugification.

    Lower-cases the string, strips leading/trailing whitespace, replaces
    any sequence of non-alphanumeric characters with a single underscore
    and collapses repeated underscores.
    """
    import re

    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return re.sub(r"_{2,}", "_", slug).strip("_")
