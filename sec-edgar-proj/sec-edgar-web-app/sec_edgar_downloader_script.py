from sec_edgar_downloader import Downloader

def scrape_filings(ticker, username, email):
    """
    Download 10-K filings for a given ticker symbol from the SEC EDGAR database.

    Args:
    - ticker (str): The ticker symbol of the company to download filings for.
    - username (str): The username to use for the SEC EDGAR downloader.
    - email (str): The email address to use for the SEC EDGAR downloader.

    Returns:
    - None
    """
    dl = Downloader(username, email)
    dl.get("10-K", ticker, after="1994-12-31", before="2024-01-01")