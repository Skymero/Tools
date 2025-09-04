"""Unit tests for analytics.price_graph.plot_price_trend."""

from pathlib import Path

import pandas as pd

from analytics.price_graph import plot_price_trend


def test_plot_price_trend(tmp_path: Path) -> None:  # type: ignore[valid-type]
    """Ensure the helper saves a file and returns its path."""
    # Patch OUTPUT_DIR to a temp dir to avoid polluting repo during test
    from importlib import reload
    import analytics.price_graph as pg

    pg.OUTPUT_DIR = tmp_path / "graphs"
    pg.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reload(pg)  # ensure module picks up new OUTPUT_DIR if needed

    df = pd.DataFrame(
        {
            "date_sold": [
                "2025-01-01",
                "2025-01-05",
                "2025-01-10",
                "2025-01-20",
                "2025-02-01",
            ],
            "price": [100, 90, 95, 97, 92],
        }
    )

    file_path = pg.plot_price_trend(df, "Nintendo Switch", filename="switch_test.png")

    saved = Path(file_path)
    assert saved.exists()
    assert saved.suffix == ".png"
    assert len(str(file_path)) > 0
