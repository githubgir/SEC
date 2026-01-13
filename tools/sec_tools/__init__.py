"""
SEC ETF Holdings Parser

Tools for downloading and parsing SEC EDGAR N-PORT filings.
"""

from .etf_holdings_parser import (
    get_etf_holdings,
    get_etf_holdings_from_file,
    get_etf_holdings_from_url,
    parse_etf_holdings,
    download_edgar_xml,
    extract_isin_from_identifiers
)

from .edgar_bulk_downloader import (
    get_nport_filing_urls,
    download_and_save_all_nport_filings,
    get_filing_summary
)

__version__ = "1.0.0"

__all__ = [
    # Parser functions
    'get_etf_holdings',
    'get_etf_holdings_from_file',
    'get_etf_holdings_from_url',
    'parse_etf_holdings',
    'download_edgar_xml',
    'extract_isin_from_identifiers',
    # Bulk downloader functions
    'get_nport_filing_urls',
    'download_and_save_all_nport_filings',
    'get_filing_summary',
]
