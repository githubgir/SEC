# EDGAR N-PORT Bulk Download Guide

Complete guide for downloading and processing historical N-PORT holdings data for ETFs and mutual funds.

## Overview

The bulk download functionality allows you to:
1. **Get all N-PORT filing URLs** for a given fund (by CIK)
2. **Download all XML files** and parse holdings data
3. **Save to CSV files** - both individual date files and combined

## Quick Start

### 1. Get Filing URLs

```python
from edgar_bulk_downloader import get_nport_filing_urls

# Get all N-PORT filing URLs for a fund
cik = "1432353"  # Global X DAX Germany ETF
urls = get_nport_filing_urls(cik)

print(f"Found {len(urls)} filings")
for filing in urls[:3]:
    print(f"{filing['filing_date']}: {filing['primary_doc_url']}")
```

**Output:**
```
Found 12 filings
2024-01-31: https://www.sec.gov/Archives/edgar/data/1432353/.../primary_doc.xml
2023-10-31: https://www.sec.gov/Archives/edgar/data/1432353/.../primary_doc.xml
2023-07-31: https://www.sec.gov/Archives/edgar/data/1432353/.../primary_doc.xml
```

### 2. Download All Filings

```python
from edgar_bulk_downloader import download_and_save_all_nport_filings

# Download all filings and save to CSV
combined_df = download_and_save_all_nport_filings(
    cik='1432353',
    output_dir='nport_data',
    delay_seconds=0.1  # Respect SEC rate limits
)

print(f"Total holdings records: {len(combined_df)}")
```

**Creates:**
- `nport_data/holdings_2024-01-31.csv` - Individual filing
- `nport_data/holdings_2023-10-31.csv` - Individual filing
- ...
- `nport_data/holdings_combined.csv` - All filings combined

### 3. Get Filing Summary

```python
from edgar_bulk_downloader import get_filing_summary

# Get summary without downloading
summary = get_filing_summary('1432353')
print(summary[['filing_date', 'form_type']])
```

## Functions

### `get_nport_filing_urls(cik, user_agent)`

Gets all N-PORT filing URLs for a CIK using the SEC EDGAR API.

**Parameters:**
- `cik` (str): Company CIK number (with or without leading zeros)
- `user_agent` (str): User-Agent string with your email (SEC requirement)

**Returns:**
- List of dictionaries with filing info:
  ```python
  [
      {
          'filing_date': '2024-01-31',
          'accession_number': '0001234567-24-000001',
          'form_type': 'NPORT-P',
          'primary_doc_url': 'https://www.sec.gov/.../primary_doc.xml'
      },
      ...
  ]
  ```

**Example:**
```python
urls = get_nport_filing_urls('1432353')
print(f"Found {len(urls)} N-PORT filings")
```

### `download_and_save_all_nport_filings(cik, output_dir, delay_seconds, user_agent)`

Downloads all N-PORT filings for a CIK and saves to CSV files.

**Parameters:**
- `cik` (str): Company CIK number
- `output_dir` (str): Directory to save CSV files (default: "nport_data")
- `delay_seconds` (float): Delay between requests (default: 0.1, respects SEC 10/sec limit)
- `user_agent` (str): User-Agent with email

**Returns:**
- DataFrame with all holdings and 'filing_date' column

**Creates:**
- Individual CSV per filing date: `{output_dir}/holdings_{date}.csv`
- Combined CSV: `{output_dir}/holdings_combined.csv`

**Example:**
```python
df = download_and_save_all_nport_filings(
    cik='1432353',
    output_dir='my_fund_data'
)

# Analyze combined data
print(df.groupby('filing_date')['value_usd'].sum())
```

### `get_filing_summary(cik, user_agent)`

Gets summary of all N-PORT filings without downloading.

**Returns:**
- DataFrame with columns: filing_date, form_type, accession_number, primary_doc_url

**Example:**
```python
summary = get_filing_summary('1432353')
print(summary)
```

## Complete Example

```python
from edgar_bulk_downloader import download_and_save_all_nport_filings
import pandas as pd

# Download all filings for Global X DAX Germany ETF
cik = "1432353"

print("Downloading all N-PORT filings...")
combined_df = download_and_save_all_nport_filings(
    cik=cik,
    output_dir='dax_etf_history',
    delay_seconds=0.15  # Be respectful of SEC servers
)

# Analysis
print(f"\nTotal records: {len(combined_df)}")
print(f"Date range: {combined_df['filing_date'].min()} to {combined_df['filing_date'].max()}")

# Holdings count by date
by_date = combined_df.groupby('filing_date').agg({
    'name': 'count',
    'value_usd': 'sum',
    'isin': lambda x: x.notna().sum()
}).rename(columns={'name': 'holdings', 'value_usd': 'total_usd', 'isin': 'with_isin'})

print("\nHoldings summary by filing date:")
print(by_date)

# Track specific security over time
security = "SAP SE"
sap_history = combined_df[combined_df['name'] == security][
    ['filing_date', 'name', 'isin', 'value_usd', 'pct_value']
].sort_values('filing_date')

print(f"\n{security} holdings over time:")
print(sap_history)
```

## Output Files

### Individual Date Files

Each filing gets its own CSV file with all holdings for that date:

**File:** `nport_data/holdings_2024-01-31.csv`

| name | isin | value_usd | pct_value | balance | ... | filing_date |
|------|------|-----------|-----------|---------|-----|-------------|
| SAP SE | DE0007164600 | 5894893.76 | 10.6773 | 33749 | ... | 2024-01-31 |
| Siemens AG | DE0007236101 | 5539584.27 | 10.0337 | 30596 | ... | 2024-01-31 |
| ... | ... | ... | ... | ... | ... | ... |

### Combined File

All filings merged with filing_date column:

**File:** `nport_data/holdings_combined.csv`

| name | isin | value_usd | pct_value | filing_date |
|------|------|-----------|-----------|-------------|
| SAP SE | DE0007164600 | 5894893.76 | 10.6773 | 2024-01-31 |
| SAP SE | DE0007164600 | 5621340.12 | 10.4221 | 2023-10-31 |
| SAP SE | DE0007164600 | 5340987.45 | 10.1892 | 2023-07-31 |
| ... | ... | ... | ... | ... |

## Finding CIK Numbers

1. Go to [SEC EDGAR Company Search](https://www.sec.gov/edgar/searchedgar/companysearch.html)
2. Search for fund name (e.g., "Global X DAX")
3. CIK appears in search results (e.g., 0001432353 or 1432353)

## SEC Rate Limits

**Important:** SEC EDGAR has rate limits:
- Maximum 10 requests per second
- Use `delay_seconds=0.1` or higher
- Include your email in User-Agent header

The functions automatically respect these limits with the `delay_seconds` parameter.

## Common Use Cases

### 1. Track Portfolio Changes Over Time

```python
df = download_and_save_all_nport_filings('1432353')

# Get top 10 holdings for each date
top_holdings = df.groupby('filing_date').apply(
    lambda x: x.nlargest(10, 'pct_value')[['name', 'pct_value']]
)
```

### 2. Analyze Specific Security

```python
security_isin = "DE0007164600"  # SAP SE
history = df[df['isin'] == security_isin].sort_values('filing_date')
print(history[['filing_date', 'name', 'value_usd', 'pct_value']])
```

### 3. Export to Excel with Multiple Sheets

```python
with pd.ExcelWriter('fund_history.xlsx') as writer:
    for date in df['filing_date'].unique():
        date_df = df[df['filing_date'] == date]
        date_df.to_excel(writer, sheet_name=date, index=False)
```

## Error Handling

The functions handle common errors gracefully:
- Network failures: Logged and skipped
- Missing data: Individual filings may fail but process continues
- Rate limits: Built-in delays respect SEC limits

Example with error handling:

```python
try:
    df = download_and_save_all_nport_filings('1432353')
except requests.HTTPError as e:
    print(f"HTTP Error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Tips

1. **Start with summary:** Use `get_filing_summary()` first to see what's available
2. **Test with recent filings:** Download 2-3 recent filings first before running full history
3. **Respect rate limits:** Use delay_seconds=0.15 or higher for large downloads
4. **Update your email:** Replace 'research@example.com' with your actual email in user_agent
5. **Check disk space:** Full history can be several MB per fund

## Troubleshooting

**"403 Forbidden" errors:**
- Make sure User-Agent includes your email
- Increase delay_seconds to 0.2 or higher
- Check if SEC EDGAR is accessible from your location

**"No filings found":**
- Verify CIK is correct
- Check fund has filed N-PORT reports (required since 2019)
- Try with leading zeros (e.g., '0001432353')

**Missing holdings:**
- Some filings may have format variations
- Parser handles most formats but edge cases may exist
- Check individual XML files manually if needed
