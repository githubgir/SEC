"""
Example script demonstrating bulk N-PORT download functionality
"""

from edgar_bulk_downloader import (
    get_nport_filing_urls,
    download_and_save_all_nport_filings,
    get_filing_summary
)
import pandas as pd

# Set pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Example: Global X DAX Germany ETF
CIK = "1432353"

print("="*100)
print("EDGAR N-PORT Bulk Downloader - Example Usage")
print("="*100)

# Example 1: Get list of all N-PORT filing URLs
print("\n" + "="*100)
print("Example 1: Get N-PORT Filing URLs")
print("="*100)

urls = get_nport_filing_urls(CIK)

print(f"\nFound {len(urls)} N-PORT filings:\n")
for i, filing in enumerate(urls[:5], 1):  # Show first 5
    print(f"{i}. Date: {filing['filing_date']}")
    print(f"   Form: {filing['form_type']}")
    print(f"   URL:  {filing['primary_doc_url'][:80]}...")
    print()

if len(urls) > 5:
    print(f"... and {len(urls) - 5} more filings")

# Example 2: Get filing summary as DataFrame
print("\n" + "="*100)
print("Example 2: Get Filing Summary")
print("="*100)

summary = get_filing_summary(CIK)
print("\nFiling Summary:")
print(summary[['filing_date', 'form_type', 'accession_number']])

# Example 3: Download a limited number of filings (for testing)
print("\n" + "="*100)
print("Example 3: Download Recent Filings")
print("="*100)

print("\nThis example will download the 3 most recent filings.")
print("(Modify the code to download all filings)\n")

# Get the 3 most recent URLs
recent_urls = urls[:3]

print(f"Downloading {len(recent_urls)} recent filings...")

# Manual download approach for controlled testing
from etf_holdings_parser import get_etf_holdings
import requests
from pathlib import Path
import time

output_dir = Path("nport_data_sample")
output_dir.mkdir(exist_ok=True)

all_data = []
headers = {
    'User-Agent': 'ETF Parser research@example.com',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.sec.gov'
}

for i, filing in enumerate(recent_urls, 1):
    filing_date = filing['filing_date']
    url = filing['primary_doc_url']

    try:
        print(f"\n[{i}/{len(recent_urls)}] Processing {filing_date}...")

        # Download
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse
        df = get_etf_holdings(response.text)
        df['filing_date'] = filing_date

        # Save individual file
        csv_file = output_dir / f"holdings_{filing_date}.csv"
        df.to_csv(csv_file, index=False)

        print(f"  ✓ {len(df)} holdings")
        print(f"  ✓ Saved to {csv_file}")

        all_data.append(df)

        # Rate limiting
        time.sleep(0.1)

    except Exception as e:
        print(f"  ✗ Error: {e}")

# Combine and save
if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    combined_file = output_dir / "holdings_combined.csv"
    combined.to_csv(combined_file, index=False)

    print(f"\n" + "="*100)
    print("Summary")
    print("="*100)
    print(f"\nTotal records: {len(combined)}")
    print(f"Filing dates: {combined['filing_date'].nunique()}")
    print(f"Unique securities: {combined['isin'].nunique()}")

    print("\nHoldings by date:")
    date_summary = combined.groupby('filing_date').agg({
        'name': 'count',
        'value_usd': 'sum',
        'isin': lambda x: x.notna().sum()
    }).rename(columns={
        'name': 'num_holdings',
        'value_usd': 'total_value_usd',
        'isin': 'with_isin'
    })
    print(date_summary)

    print(f"\n✓ Combined file: {combined_file}")
    print(f"✓ Individual files in: {output_dir}")

print("\n" + "="*100)
print("Example completed!")
print("="*100)
print("\nTo download ALL filings, use:")
print("  df = download_and_save_all_nport_filings('1432353')")
