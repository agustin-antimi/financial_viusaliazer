import streamlit as st
from config import CHART_COLORS, DEFAULT_PERIOD_INDEX, DEFAULT_TICKER, PERIODS
import page_funcitons as fg

def render_sidebar() -> tuple[str, str]:
    """Renders sidebar controls for ticker and period selection.

    Returns:
        A tuple of (ticker_name, period).
    """
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.divider()

        input_mode = st.radio(
            "Ticker source",
            ["S&P 500", "Custom"],
            horizontal=True,
            help="S&P 500 shows a searchable dropdown. Custom lets you type any symbol.",
        )

        if input_mode == "S&P 500":
            sp500 = fg.load_sp500_tickers()
            default_idx = (
                sp500.index(DEFAULT_TICKER) if DEFAULT_TICKER in sp500 else 0
            )
            ticker_name = st.selectbox(
                "Select ticker",
                sp500,
                index=default_idx,
                placeholder="Type to search...",
            )
        else:
            ticker_name = (
                st.text_input(
                    "Enter ticker symbol",
                    value=DEFAULT_TICKER,
                    max_chars=10,
                    placeholder="e.g. TSLA, BTC-USD, AMZN",
                )
                .upper()
                .strip()
            )

        st.divider()

        period = st.selectbox("Period", PERIODS, index=DEFAULT_PERIOD_INDEX)

        st.divider()
        st.caption(
            "Data provided by [Yahoo Finance](https://finance.yahoo.com). "
            "May be delayed."
        )

        return ticker_name, period