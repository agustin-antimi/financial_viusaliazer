from config import CHART_COLORS
import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
from src.functions import (
    _init_ticker,
    _get_history,
    fetch_sp500_tickers,
    format_for_streamlit_charts,
)
import src.ui as ui

# --- Data Loading ---
@st.cache_data(ttl=3600, show_spinner=False)
def load_sp500_tickers() -> list[str]:
    """Cached wrapper for S&P 500 ticker fetching.

    Returns:
        A sorted list of S&P 500 ticker symbols.
    """
    return fetch_sp500_tickers()


@st.cache_data(ttl=300, show_spinner="Fetching market data...")
def load_ticker_data(ticker_name: str, period: str) -> list[dict]:
    """Fetches and formats historical data for chart rendering.

    Args:
        ticker_name: The stock ticker symbol.
        period: The time period to fetch.

    Returns:
        Formatted list of OHLCV records ready for chart rendering.
    """
    ticker = _init_ticker(ticker_name)
    df = _get_history(ticker, period=period)
    return format_for_streamlit_charts(df)


def build_chart_config(candle_data: list[dict]) -> list[dict]:
    """Builds the lightweight-charts configuration from formatted candle data.

    Args:
        candle_data: List of OHLC dictionaries.

    Returns:
        Chart configuration list ready for renderLightweightCharts.
    """
    return [
        {
            "chart": {
                "height": 500,
                "layout": {
                    "background": {"color": CHART_COLORS["background"]},
                    "textColor": CHART_COLORS["text"],
                },
                "grid": {
                    "vertLines": {"color": CHART_COLORS["grid"]},
                    "horzLines": {"color": CHART_COLORS["grid"]},
                },
                "crosshair": {"mode": 0},
                "timeScale": {
                    "borderColor": CHART_COLORS["border"],
                    "timeVisible": False,
                },
                "rightPriceScale": {
                    "borderColor": CHART_COLORS["border"],
                },
            },
            "series": [
                {
                    "type": "Candlestick",
                    "data": candle_data,
                    "options": {
                        "upColor": CHART_COLORS["up"],
                        "downColor": CHART_COLORS["down"],
                        "borderUpColor": CHART_COLORS["up"],
                        "borderDownColor": CHART_COLORS["down"],
                        "wickUpColor": CHART_COLORS["up"],
                        "wickDownColor": CHART_COLORS["down"],
                    },
                }
            ],
        }
    ]


def render_chart(ticker_name: str, period: str) -> None:
    """Fetches data and renders the candlestick chart.

    Args:
        ticker_name: The stock ticker symbol.
        period: The time period to display.
    """
    if not ticker_name:
        st.warning("⚠️ Please enter a valid ticker symbol.")
        return

    data = load_ticker_data(ticker_name, period)

    if not data:
        st.error(
            f"❌ No data found for **{ticker_name}**. "
            "Check the symbol and try again."
        )
        return

    chart_config = build_chart_config(data)
    renderLightweightCharts(chart_config, key=f"chart_{ticker_name}_{period}")


def render_header(ticker_name: str) -> None:
    """Renders the page header with the active ticker name.

    Args:
        ticker_name: The stock ticker symbol being displayed.
    """
    st.markdown(f"# 📊 {ticker_name}")
    st.caption("Interactive candlestick chart · Real-time market data")


def render_footer() -> None:
    """Renders the TradingView attribution footer (required by license)."""
    st.divider()
    st.markdown(
        '<div style="text-align: center; color: #6c757d; font-size: 0.85rem; '
        'padding: 0.5rem 0;">'
        "Charts powered by "
        '<a href="https://www.tradingview.com" target="_blank" '
        'style="color: #2962FF; text-decoration: none;">'
        "TradingView Lightweight Charts™</a>"
        "</div>",
        unsafe_allow_html=True,
    )


# --- Main ---
def main():
    """Entry point for the Streamlit application."""
    st.set_page_config(
        page_title="Financial Visualizer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    ticker_name, period = ui.render_sidebar()
    render_header(ticker_name)
    render_chart(ticker_name, period)
    render_footer()