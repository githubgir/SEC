# ETF Holdings Parser

Python function to download SEC EDGAR XML files and extract ETF fund constituents/positions as a pandas DataFrame.

## Features

- Downloads N-PORT XML filings from SEC EDGAR
- Parses XML and extracts security positions
- Correctly handles nested ISIN identifiers
- Returns clean pandas DataFrame
- Supports both URL download and local file parsing

## Installation

```bash
pip install pandas requests lxml
```

## Usage

### From URL

```python
from etf_holdings_parser import get_etf_holdings_from_url

url = "https://www.sec.gov/Archives/edgar/data/1432353/000175272424075322/primary_doc.xml"
df = get_etf_holdings_from_url(url)

print(f"Found {len(df)} holdings")
print(df.head())
```

### From Local File

```python
from etf_holdings_parser import get_etf_holdings_from_file

df = get_etf_holdings_from_file('primary_doc.xml')
print(df.head())
```

### Advanced Usage

```python
from etf_holdings_parser import download_edgar_xml, parse_etf_holdings

# Download XML
xml_content = download_edgar_xml(url)

# Parse to DataFrame
df = parse_etf_holdings(xml_content)

# Analyze holdings
print(f"Total holdings: {len(df)}")
print(f"ISIN coverage: {df['isin'].notna().sum()}/{len(df)}")
print(f"\nTop 10 holdings by value:")
print(df.nlargest(10, 'value_usd')[['name', 'isin', 'value_usd', 'pct_value']])
```

## DataFrame Columns

The returned DataFrame includes the following columns:

- `name`: Security name
- `title`: Security title/description
- `cusip`: CUSIP identifier
- `isin`: ISIN identifier (extracted from nested elements)
- `lei`: LEI identifier
- `balance`: Number of shares/units
- `units`: Unit type (shares, principal amount, etc.)
- `value_usd`: Market value in USD
- `pct_value`: Percentage of total portfolio value
- `currency`: Currency code
- `asset_category`: Asset category (equity, debt, etc.)
- `issuer_category`: Issuer category
- `country`: Country of investment

## ISIN Extraction

The parser correctly handles nested ISIN identifiers in N-PORT XML files. The XML structure typically looks like:

```xml
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
```

The `extract_isin_from_identifiers()` function searches through all identifier elements to find the one with type "ISIN" and extracts its value.

## Example Output

```
Found 523 holdings

Columns: ['name', 'cusip', 'isin', 'lei', 'balance', 'units', 'value_usd',
          'pct_value', 'currency', 'asset_category', 'issuer_category', 'country']

First few holdings:
                    name        cusip          isin  value_usd  pct_value
0     Microsoft Corp    594918104  US5949181045   45000000       8.5
1     Apple Inc         037833100  US0378331005   42000000       8.0
2     Amazon.com Inc    023135106  US0231351067   38000000       7.2

ISIN coverage: 515/523 (98.5%)
```

## Error Handling

The function handles common issues:

- **Network errors**: SEC.gov may block automated requests. Download manually if needed and use `get_etf_holdings_from_file()`
- **Missing fields**: Returns None/NaN for missing data
- **Namespaces**: Uses wildcard matching to handle different XML namespaces
- **Encoding**: Handles UTF-8 encoding for international characters

## Notes

- Replace the User-Agent email in `download_edgar_xml()` with your actual email
- SEC.gov requires proper User-Agent headers and may rate-limit requests
- N-PORT files are typically filed quarterly by ETFs and mutual funds
- Some holdings may not have ISIN identifiers (e.g., derivatives, cash positions)

## Finding N-PORT Filings

1. Go to [SEC EDGAR](https://www.sec.gov/edgar/searchedgar/companysearch.html)
2. Search for your fund/ETF
3. Look for "NPORT-P" filings
4. Click on the filing and find the "primary_doc.xml" link

## Bulk Download - Historical Filings

Download ALL historical N-PORT filings for a fund automatically:

```python
from edgar_bulk_downloader import download_and_save_all_nport_filings

# Download all filings for a fund (by CIK)
df = download_and_save_all_nport_filings(
    cik='1432353',  # Global X DAX Germany ETF
    output_dir='nport_data'
)

# Creates individual CSV per date + combined CSV
# nport_data/holdings_2024-01-31.csv
# nport_data/holdings_2023-10-31.csv
# nport_data/holdings_combined.csv
```

See [BULK_DOWNLOAD_GUIDE.md](BULK_DOWNLOAD_GUIDE.md) for complete documentation.

### Key Functions

- `get_nport_filing_urls(cik)` - Get list of all filing URLs
- `download_and_save_all_nport_filings(cik)` - Download and save all filings
- `get_filing_summary(cik)` - Get filing info without downloading

## Export Functions

Export holdings to Excel and CSV:

```python
from export_holdings import export_to_excel_and_csv

# Export current holdings
export_to_excel_and_csv('primary_doc.xml')
# Creates: etf_holdings.xlsx and etf_holdings.csv
```
