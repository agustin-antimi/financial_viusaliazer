import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional, List, Union
from lightweight_charts import Chart, JupyterChart

def _init_ticker(ticker_name: str) -> yf.Ticker:
    """Initializes a yfinance Ticker object.
    
    Args:
        ticker_name (str): The symbol of the ticker (e.g., 'AAPL').
        
    Returns:
        yf.Ticker: The initialized Ticker object.
    """
    return yf.Ticker(ticker_name)

def _validate_dates(start: Optional[str], end: Optional[str]) -> bool:
    """Validates that dates are in YYYY-MM-DD format and start <= end.
    
    Args:
        start (Optional[str]): Start date string.
        end (Optional[str]): End date string.
        
    Returns:
        bool: True if dates are valid or omitted, False otherwise.
    """
    if not start or not end:
        return True
        
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        
        if start_date > end_date:
            print(f"Warning: 'start' date ({start}) cannot be greater than 'end' date ({end}).")
            return False
            
        return True
    except ValueError:
        print("Warning: Invalid date format. Use 'YYYY-MM-DD' (e.g., '2023-01-01').")
        return False

def _get_history(
    ticker: yf.Ticker,
    period: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Fetches historical price data from yfinance.
    
    Args:
        ticker (yf.Ticker): The Ticker object to fetch data for.
        period (Optional[str]): The time period to fetch (e.g., '1y', '1mo').
        start (Optional[str]): Start date in YYYY-MM-DD format.
        end (Optional[str]): End date in YYYY-MM-DD format.
        
    Returns:
        pd.DataFrame: Raw historical data or empty DataFrame on failure.
    """
    if not _validate_dates(start, end):
        return pd.DataFrame()
        
    kwargs = {}
    if start:
        kwargs['start'] = start
    if end:
        kwargs['end'] = end
        
    if period and not start:
        kwargs['period'] = period
        
    if not kwargs:
        kwargs['period'] = "1y"
        
    try:
        df = ticker.history(**kwargs)
    except Exception as e:
        print(f"Error fetching data from yfinance: {e}")
        return pd.DataFrame()
        
    if df is None or df.empty:
        print("Warning: yfinance returned no data for the requested parameters.")
        return pd.DataFrame()
    
    return df

def _format_for_lightweight_charts(df: pd.DataFrame) -> pd.DataFrame:
    """Formats a yfinance DataFrame for lightweight-charts compatibility.
    
    Args:
        df (pd.DataFrame): Raw historical data from yfinance.
        
    Returns:
        pd.DataFrame: Formatted DataFrame with required columns and ns resolution.
    """
    if df is None or df.empty:
        return pd.DataFrame()
        
    try:
        formatted_df = df.copy().reset_index()
        
        # Flatten MultiIndex columns if they exist (common in newer yfinance versions)
        if isinstance(formatted_df.columns, pd.MultiIndex):
            formatted_df.columns = formatted_df.columns.get_level_values(0)
            
        formatted_df.columns = formatted_df.columns.str.lower()
        
        if 'date' in formatted_df.columns:
            formatted_df = formatted_df.rename(columns={'date': 'time'})
        elif 'datetime' in formatted_df.columns:
            formatted_df = formatted_df.rename(columns={'datetime': 'time'})
            
        if 'time' in formatted_df.columns:
            # BUGFIX: Force resolution to nanoseconds [ns] to prevent the 
            # timestamp scaling bug in lightweight-charts-python with pandas 2.0+
            formatted_df['time'] = (
                pd.to_datetime(formatted_df['time'])
                .dt.tz_localize(None)
                .astype('datetime64[ns]')
            )
        
        desired_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        final_columns = [col for col in desired_columns if col in formatted_df.columns]
        
        return formatted_df[final_columns]
        
    except Exception as e:
        print(f"Error formatting data for lightweight-charts: {e}")
        return pd.DataFrame()
    

def fetch_sp500_tickers() -> List[str]:
    """Fetches the list of S&P 500 ticker symbols from Wikipedia.
    
    Bypasses the 403 Forbidden error by providing a standard browser 
    User-Agent header.
    Returns:
        List[str]: A list containing the ticker symbols of the S&P 500 companies.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    # We define a User-Agent that looks like a normal Google Chrome browser
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Pass the headers using storage_options
    tables = pd.read_html(url, storage_options=custom_headers)
    
    # The first table on the page is the S&P 500 constituents table
    sp500_table = tables[0]
    
    # Extract the 'Symbol' column
    tickers = sp500_table['Symbol'].tolist()
    
    # Clean up tickers (e.g., BRK.B to BRK-B) for yfinance compatibility
    clean_tickers = [ticker.replace('.', '-') for ticker in tickers]
    
    return clean_tickers


def create_candlestick_chart(
    ticker_name: str,
    period: Optional[str] = "1y",
    start: Optional[str] = None,
    end: Optional[str] = None,
    in_jupyter: bool = False,
) -> Union[Chart, JupyterChart, None]:
    """Creates and configures an interactive candlestick chart for a given ticker.
    
    This function orchestrates fetching data, formatting it, and initializing
    the lightweight-charts object with premium aesthetics. It does not display 
    the chart automatically, allowing further customization by the caller.
    
    Args:
        ticker_name (str): The stock ticker symbol (e.g., 'AAPL').
        period (Optional[str]): The time period to fetch (e.g., '1y', '1mo'). Defaults to "1y".
        start (Optional[str]): Start date in YYYY-MM-DD format.
        end (Optional[str]): End date in YYYY-MM-DD format.
        in_jupyter (bool): If True, returns a JupyterChart instead of a standard Chart.
        
    Returns:
        Union[Chart, JupyterChart, None]: The configured chart object, or None if data fetching fails.
    """
    ticker = _init_ticker(ticker_name)
    df_raw = _get_history(ticker, period=period, start=start, end=end)
    
    if df_raw.empty:
        print(f"Cannot create chart for {ticker_name}: No data available.")
        return None
        
    df_formatted = _format_for_lightweight_charts(df_raw)
    
    if df_formatted.empty:
        print(f"Cannot create chart for {ticker_name}: Error formatting data.")
        return None
        
    # Instantiate the correct Chart object based on the environment
    chart = JupyterChart() if in_jupyter else Chart()
    
    # Premium visual customization
    chart.layout(background_color='#131722', text_color='#d1d4dc')
    chart.candle_style(
        up_color='#26a69a', down_color='#ef5350',
        border_up_color='#26a69a', border_down_color='#ef5350',
        wick_up_color='#26a69a', wick_down_color='#ef5350'
    )
    chart.volume_config(scale_margin_top=0.8, scale_margin_bottom=0.0)
    
    # Set the formatted data
    chart.set(df_formatted)
    
    return chart