"""
ETF Holdings Parser for SEC EDGAR XML Files

This module provides functionality to download and parse ETF holdings
from SEC EDGAR N-PORT XML filings.

The parser extracts constituents/positions from ETF funds and returns
them as a pandas DataFrame. It handles nested XML structures and correctly
extracts identifiers like ISIN, CUSIP, and LEI.

Usage:
    # From URL
    df = get_etf_holdings_from_url(url)

    # From local file
    df = get_etf_holdings_from_file(filepath)
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Union
from pathlib import Path
from io import StringIO
import os


def download_edgar_xml(url: str) -> str:
    """
    Download XML file from SEC EDGAR with appropriate headers.

    SEC requires proper User-Agent headers to prevent abuse.
    Replace 'research@example.com' with your actual email.

    Args:
        url: The SEC EDGAR URL to download

    Returns:
        XML content as string

    Raises:
        requests.HTTPError: If download fails
        requests.ProxyError: If proxy blocks the request
    """
    headers = {
        'User-Agent': 'ETF Holdings Parser research@example.com',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def extract_isin_from_identifiers(identifiers_elem) -> Optional[str]:
    """
    Extract ISIN from nested identifier elements.

    N-PORT XML files typically have a structure like:
    <identifiers>
        <identifier>
            <identifierType>ISIN</identifierType>
            <identifierValue>US1234567890</identifierValue>
        </identifier>
        <identifier>
            <identifierType>Ticker</identifierType>
            <identifierValue>ABC</identifierValue>
        </identifier>
    </identifiers>

    This function searches through all identifier elements to find
    the one with type="ISIN" and extracts its value.

    Args:
        identifiers_elem: XML element containing identifiers

    Returns:
        ISIN code if found, None otherwise
    """
    if identifiers_elem is None:
        return None

    # Search for ISIN in nested structure using wildcard namespace
    for identifier in identifiers_elem:
        # Look for identifier type and value (namespace-agnostic)
        id_type = identifier.find('.//{*}identifierType')
        id_value = identifier.find('.//{*}identifierValue')

        if id_type is not None and id_value is not None:
            if id_type.text and id_type.text.strip().upper() == 'ISIN':
                return id_value.text.strip() if id_value.text else None

        # Also check direct child elements (some formats use this)
        for child in identifier:
            tag = child.tag.split('}')[-1]  # Remove namespace
            if tag == 'isin' and child.text:
                return child.text.strip()

    return None


def parse_etf_holdings(xml_content: str) -> pd.DataFrame:
    """
    Parse ETF holdings from SEC N-PORT XML content.

    Args:
        xml_content: XML content as string

    Returns:
        DataFrame with ETF holdings/positions
    """
    # Parse XML
    root = ET.fromstring(xml_content)

    # Find namespace
    namespace = {}
    if root.tag.startswith('{'):
        ns = root.tag.split('}')[0].strip('{')
        namespace = {'ns': ns}

    holdings = []

    # Find all investment positions
    # N-PORT format typically has invstOrSec elements
    for inv in root.findall('.//{*}invstOrSec', namespace):
        holding = {}

        # Basic security info
        name_elem = inv.find('.//{*}name')
        if name_elem is not None:
            holding['name'] = name_elem.text

        # Title
        title_elem = inv.find('.//{*}title')
        if title_elem is not None:
            holding['title'] = title_elem.text

        # CUSIP
        cusip_elem = inv.find('.//{*}cusip')
        if cusip_elem is not None:
            holding['cusip'] = cusip_elem.text

        # ISIN from identifiers
        identifiers_elem = inv.find('.//{*}identifiers')
        holding['isin'] = extract_isin_from_identifiers(identifiers_elem)

        # Alternative: check for ISIN directly
        if not holding.get('isin'):
            isin_elem = inv.find('.//{*}isin')
            if isin_elem is not None:
                holding['isin'] = isin_elem.text

        # LEI
        lei_elem = inv.find('.//{*}lei')
        if lei_elem is not None:
            holding['lei'] = lei_elem.text

        # Balance/shares
        balance_elem = inv.find('.//{*}balance')
        if balance_elem is not None:
            holding['balance'] = balance_elem.text

        # Units
        units_elem = inv.find('.//{*}units')
        if units_elem is not None:
            holding['units'] = units_elem.text

        # Value
        value_elem = inv.find('.//{*}valUSD')
        if value_elem is not None:
            holding['value_usd'] = float(value_elem.text)

        # Percentage
        pct_elem = inv.find('.//{*}pctVal')
        if pct_elem is not None:
            holding['pct_value'] = float(pct_elem.text)

        # Currency
        currency_elem = inv.find('.//{*}curCd')
        if currency_elem is not None:
            holding['currency'] = currency_elem.text

        # Asset category
        asset_cat_elem = inv.find('.//{*}assetCat')
        if asset_cat_elem is not None:
            holding['asset_category'] = asset_cat_elem.text

        # Issuer category
        issuer_cat_elem = inv.find('.//{*}issuerCat')
        if issuer_cat_elem is not None:
            holding['issuer_category'] = issuer_cat_elem.text

        # Country
        country_elem = inv.find('.//{*}invCountry')
        if country_elem is not None:
            holding['country'] = country_elem.text

        holdings.append(holding)

    # Convert to DataFrame
    df = pd.DataFrame(holdings)

    return df


def get_etf_holdings_from_file(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Parse ETF holdings from local XML file.

    Args:
        filepath: Path to local N-PORT XML file

    Returns:
        DataFrame with ETF holdings

    Example:
        >>> df = get_etf_holdings_from_file('primary_doc.xml')
        >>> print(df.head())
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    df = parse_etf_holdings(xml_content)
    return df


def get_etf_holdings_from_url(url: str) -> pd.DataFrame:
    """
    Download and parse ETF holdings from SEC EDGAR URL.

    Args:
        url: SEC EDGAR URL for N-PORT XML filing

    Returns:
        DataFrame with ETF holdings

    Example:
        >>> url = "https://www.sec.gov/Archives/edgar/data/1432353/000175272424075322/primary_doc.xml"
        >>> df = get_etf_holdings_from_url(url)
        >>> print(df.head())

    Note:
        SEC.gov may require proper User-Agent headers and may block
        automated requests. If you encounter issues, download the
        file manually and use get_etf_holdings_from_file() instead.
    """
    xml_content = download_edgar_xml(url)
    df = parse_etf_holdings(xml_content)
    return df


def get_etf_holdings(source: Union[str, Path]) -> pd.DataFrame:
    """
    Universal function to parse ETF holdings from URL, file path, or XML string.

    This function automatically detects the source type and processes accordingly:
    - If source starts with 'http://' or 'https://', treats as URL
    - If source is a path to an existing file, reads the file
    - Otherwise, treats as XML string content

    Args:
        source: URL string, file path, or XML string content

    Returns:
        DataFrame with ETF holdings including name, ISIN, value_usd, pct_value, etc.

    Examples:
        >>> # From URL
        >>> df = get_etf_holdings("https://www.sec.gov/Archives/edgar/data/.../primary_doc.xml")

        >>> # From file path
        >>> df = get_etf_holdings("primary_doc.xml")
        >>> df = get_etf_holdings("/path/to/primary_doc.xml")

        >>> # From XML string
        >>> xml_content = "<?xml version='1.0'?>..."
        >>> df = get_etf_holdings(xml_content)

    Raises:
        requests.HTTPError: If URL download fails
        FileNotFoundError: If file path doesn't exist
        ET.ParseError: If XML content is malformed
    """
    source_str = str(source)

    # Check if it's a URL
    if source_str.startswith('http://') or source_str.startswith('https://'):
        xml_content = download_edgar_xml(source_str)
    # Check if it's a file path
    elif os.path.exists(source_str):
        with open(source_str, 'r', encoding='utf-8') as f:
            xml_content = f.read()
    # Treat as XML string
    else:
        xml_content = source_str

    # Parse and return DataFrame
    df = parse_etf_holdings(xml_content)
    return df


if __name__ == "__main__":
    # Test with provided URL
    test_url = "https://www.sec.gov/Archives/edgar/data/1432353/000175272424075322/primary_doc.xml"

    print("Downloading and parsing ETF holdings...")
    df = get_etf_holdings_from_url(test_url)

    print(f"\nFound {len(df)} holdings")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few holdings:")
    print(df.head())

    # Show ISIN coverage
    isin_count = df['isin'].notna().sum()
    print(f"\nISIN coverage: {isin_count}/{len(df)} ({100*isin_count/len(df):.1f}%)")
