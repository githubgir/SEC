"""
EDGAR N-PORT Bulk Downloader

Functions to download historical N-PORT filings for a given fund and
export holdings data to CSV files.
"""

import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from .etf_holdings_parser import get_etf_holdings


def get_nport_filing_urls(cik: str, user_agent: str = "ETF Parser research@example.com") -> List[Dict[str, str]]:
    """
    Get all N-PORT filing URLs for a given CIK.

    Uses the SEC EDGAR submissions API to find all N-PORT filings.

    Args:
        cik: Company CIK number (can be with or without leading zeros)
        user_agent: User-Agent string with email for SEC compliance

    Returns:
        List of dictionaries containing filing information:
        [
            {
                'filing_date': '2024-01-31',
                'accession_number': '0001234567-24-000001',
                'primary_doc_url': 'https://www.sec.gov/.../primary_doc.xml'
            },
            ...
        ]

    Example:
        >>> urls = get_nport_filing_urls('1432353')
        >>> print(f"Found {len(urls)} N-PORT filings")
    """
    # Normalize CIK to 10 digits with leading zeros
    cik_padded = cik.zfill(10)

    # SEC EDGAR submissions API
    submissions_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

    headers = {
        'User-Agent': user_agent,
        'Accept-Encoding': 'gzip, deflate'
    }

    print(f"Fetching filings for CIK {cik_padded}...")
    response = requests.get(submissions_url, headers=headers)
    response.raise_for_status()

    data = response.json()

    # Extract recent filings
    filings = data.get('filings', {}).get('recent', {})

    filing_urls = []

    # Iterate through filings to find N-PORT forms
    for i in range(len(filings.get('form', []))):
        form_type = filings['form'][i]

        # Look for N-PORT filings (N-PORT-P is the public version)
        if form_type in ['NPORT-P', 'NPORT-EX']:
            filing_date = filings['filingDate'][i]
            accession_number = filings['accessionNumber'][i]
            primary_document = filings['primaryDocument'][i]

            # Remove dashes from accession number for URL
            accession_no_dashes = accession_number.replace('-', '')

            # Construct primary document URL
            primary_doc_url = (
                f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primary_document}"
            )

            filing_urls.append({
                'filing_date': filing_date,
                'accession_number': accession_number,
                'form_type': form_type,
                'primary_doc_url': primary_doc_url
            })

    # Sort by filing date (most recent first)
    filing_urls.sort(key=lambda x: x['filing_date'], reverse=True)

    print(f"✓ Found {len(filing_urls)} N-PORT filings")

    return filing_urls


def download_and_save_all_nport_filings(
    cik: str,
    output_dir: str = "nport_data",
    delay_seconds: float = 0.1,
    user_agent: str = "ETF Parser research@example.com"
) -> pd.DataFrame:
    """
    Download all N-PORT filings for a CIK and save to CSV files.

    Creates:
    - Individual CSV files for each filing date: {output_dir}/holdings_{date}.csv
    - Combined CSV with all holdings: {output_dir}/holdings_combined.csv

    Args:
        cik: Company CIK number
        output_dir: Directory to save CSV files
        delay_seconds: Delay between requests to respect SEC rate limits
        user_agent: User-Agent string with email for SEC compliance

    Returns:
        Combined DataFrame with all holdings and an additional 'filing_date' column

    Example:
        >>> df = download_and_save_all_nport_filings('1432353')
        >>> print(df[['filing_date', 'name', 'isin', 'value_usd']].head())
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Get all filing URLs
    filing_urls = get_nport_filing_urls(cik, user_agent)

    if not filing_urls:
        print("No N-PORT filings found")
        return pd.DataFrame()

    all_holdings = []

    headers = {
        'User-Agent': user_agent,
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }

    print(f"\nDownloading and parsing {len(filing_urls)} N-PORT filings...")
    print("=" * 80)

    for i, filing_info in enumerate(filing_urls, 1):
        filing_date = filing_info['filing_date']
        url = filing_info['primary_doc_url']

        try:
            print(f"\n[{i}/{len(filing_urls)}] {filing_date}")
            print(f"  URL: {url}")

            # Download XML
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            xml_content = response.text

            # Parse holdings
            df = get_etf_holdings(xml_content)

            if len(df) == 0:
                print(f"  ⚠ No holdings found")
                continue

            # Add filing date column
            df['filing_date'] = filing_date

            # Save individual CSV
            csv_filename = output_path / f"holdings_{filing_date}.csv"
            df.to_csv(csv_filename, index=False)

            print(f"  ✓ Found {len(df)} holdings")
            print(f"  ✓ Saved to {csv_filename}")

            # Add to combined list
            all_holdings.append(df)

            # Respect SEC rate limits (10 requests per second max)
            time.sleep(delay_seconds)

        except Exception as e:
            print(f"  ✗ Error processing {filing_date}: {str(e)}")
            continue

    # Create combined DataFrame
    if all_holdings:
        combined_df = pd.concat(all_holdings, ignore_index=True)

        # Save combined CSV
        combined_filename = output_path / "holdings_combined.csv"
        combined_df.to_csv(combined_filename, index=False)

        print("\n" + "=" * 80)
        print(f"✓ Successfully processed {len(all_holdings)} filings")
        print(f"✓ Total holdings records: {len(combined_df)}")
        print(f"✓ Combined file saved to: {combined_filename}")
        print(f"✓ Individual files saved in: {output_path}")
        print("=" * 80)

        return combined_df
    else:
        print("\n⚠ No holdings data downloaded")
        return pd.DataFrame()


def get_filing_summary(cik: str, user_agent: str = "ETF Parser research@example.com") -> pd.DataFrame:
    """
    Get a summary of all N-PORT filings for a CIK without downloading.

    Args:
        cik: Company CIK number
        user_agent: User-Agent string with email for SEC compliance

    Returns:
        DataFrame with filing information

    Example:
        >>> summary = get_filing_summary('1432353')
        >>> print(summary)
    """
    filing_urls = get_nport_filing_urls(cik, user_agent)

    if not filing_urls:
        return pd.DataFrame()

    df = pd.DataFrame(filing_urls)
    return df


if __name__ == "__main__":
    # Example usage with Global X DAX Germany ETF
    cik = "1432353"

    print("EDGAR N-PORT Bulk Downloader")
    print("=" * 80)

    # First, get summary of available filings
    print("\n1. Getting filing summary...")
    summary = get_filing_summary(cik)
    print(f"\nAvailable N-PORT filings:")
    print(summary[['filing_date', 'form_type']].to_string(index=False))

    # Download all filings
    print("\n2. Downloading all filings...")
    response = input("\nProceed with download? (y/n): ")

    if response.lower() == 'y':
        combined_df = download_and_save_all_nport_filings(cik, output_dir="nport_data")

        if len(combined_df) > 0:
            print("\nSample of combined data:")
            print(combined_df[['filing_date', 'name', 'isin', 'value_usd', 'pct_value']].head(10))

            # Summary by filing date
            print("\nHoldings count by filing date:")
            summary_by_date = combined_df.groupby('filing_date').agg({
                'name': 'count',
                'value_usd': 'sum'
            }).rename(columns={'name': 'num_holdings', 'value_usd': 'total_value_usd'})
            print(summary_by_date)
    else:
        print("Download cancelled")
