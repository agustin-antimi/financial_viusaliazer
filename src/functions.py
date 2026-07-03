import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional

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
        pd.DataFrame: Formatted DataFrame with required columns and timezone-naive dates.
    """
    if df is None or df.empty:
        return pd.DataFrame()
        
    try:
        # Create a copy to prevent modifying the original dataframe
        formatted_df = df.copy().reset_index()
        formatted_df.columns = formatted_df.columns.str.lower()
        
        if 'date' in formatted_df.columns:
            formatted_df = formatted_df.rename(columns={'date': 'time'})
        elif 'datetime' in formatted_df.columns:
            formatted_df = formatted_df.rename(columns={'datetime': 'time'})
            
        if 'time' in formatted_df.columns:
            formatted_df['time'] = pd.to_datetime(formatted_df['time']).dt.tz_localize(None)
        
        desired_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        final_columns = [col for col in desired_columns if col in formatted_df.columns]
        
        return formatted_df[final_columns]
        
    except Exception as e:
        print(f"Error formatting data for lightweight-charts: {e}")
        return pd.DataFrame()