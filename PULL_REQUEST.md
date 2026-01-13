# ETF Holdings Parser - Complete SEC N-PORT Filing Parser with Bulk Download

## Summary

Complete SEC EDGAR N-PORT filing parser for extracting ETF/fund holdings data with bulk download capabilities, comprehensive tests, and Excel/CSV export.

## Features Implemented

### ✅ Core Parser
- Parse N-PORT XML filings from **URL, file path, or XML string**
- Extract all security identifiers: **ISIN, CUSIP, LEI**
- Handle **multiple ISIN XML formats** (attribute & nested)
- Extract position data: value_usd, pct_value, balance, units
- Return clean **pandas DataFrame**
- **97.6% ISIN coverage** on real data

### ✅ Bulk Download System
- Discover all historical N-PORT filings for a fund (by CIK)
- Use SEC EDGAR submissions API (data.sec.gov)
- Download and parse all filings automatically
- Save **individual CSV per filing date**
- Save **combined CSV** with filing_date column
- Respect SEC rate limits (10 req/sec with configurable delays)
- Graceful error handling

### ✅ Export & Analysis
- Export to Excel (.xlsx) and CSV (.csv)
- Display formatted holdings tables
- Time-series analysis support
- Track portfolio changes over time

### ✅ Package Structure
```
tools/sec_tools/
├── __init__.py                      # Package exports
├── etf_holdings_parser.py          # Core parser
├── edgar_bulk_downloader.py        # Bulk download
├── export_holdings.py              # Export utilities
├── show_holdings.py                # Display script
├── tests/
│   ├── __init__.py
│   └── test_etf_holdings_parser.py # 12 unit tests
├── test_parser.py                  # Sample data test
├── test_unified.py                 # Multi-format test
├── test_primary_doc.py             # Real data test
└── example_bulk_download.py        # Usage examples
```

## Test Results

### Unit Tests: **12/12 PASSING** ✅

```
test_isin_attribute_format ... ok
test_isin_nested_format ... ok
test_isin_with_multiple_identifiers ... ok
test_missing_isin ... ok
test_none_identifiers ... ok
test_parse_sample_xml ... ok
test_parse_multiple_holdings ... ok
test_read_from_file ... ok
test_from_file_path ... ok
test_from_url ... ok
test_from_xml_string ... ok
test_download_from_url ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.012s

OK
```

### Test Coverage
- ✅ ISIN extraction (attribute format: `<isin value="..."/>`)
- ✅ ISIN extraction (nested format: `<identifierType>ISIN</identifierType>`)
- ✅ Multiple identifier handling
- ✅ Missing ISIN handling
- ✅ XML parsing (single & multiple holdings)
- ✅ Local file reading
- ✅ XML string parsing
- ✅ URL download (with mocked HTTP)

## Real Data Testing

Successfully parsed **Global X DAX Germany ETF** (CIK: 1432353):

| Metric | Value |
|--------|-------|
| Holdings | 41 positions |
| ISIN Coverage | 97.6% (40/41) |
| Portfolio Value | $55,196,719 |
| Total Weight | 99.98% |
| Missing ISIN | 1 (futures contract - expected) |

**Top Holdings Parsed:**
1. SAP SE (10.68%, $5.89M) - ISIN: DE0007164600 ✅
2. Siemens AG (10.03%, $5.54M) - ISIN: DE0007236101 ✅
3. Allianz SE (7.93%, $4.38M) - ISIN: DE0008404005 ✅

## Usage Examples

### Quick Start
```python
from tools.sec_tools import get_etf_holdings

# Parse from any source
df = get_etf_holdings('primary_doc.xml')  # File path
df = get_etf_holdings('https://sec.gov/.../primary_doc.xml')  # URL
df = get_etf_holdings(xml_string)  # XML string
```

### Bulk Download
```python
from tools.sec_tools import download_and_save_all_nport_filings

# Download all historical filings
df = download_and_save_all_nport_filings(
    cik='1432353',  # Global X DAX Germany ETF
    output_dir='nport_data'
)

# Output:
# nport_data/holdings_2024-01-31.csv
# nport_data/holdings_2023-10-31.csv
# nport_data/holdings_2023-07-31.csv
# ...
# nport_data/holdings_combined.csv
```

### Time-Series Analysis
```python
# Track how holdings changed over time
sap = df[df['name'] == 'SAP SE'][['filing_date', 'value_usd', 'pct_value']]
print(sap.sort_values('filing_date'))
```

## Files Included

### Code
- ✅ `tools/sec_tools/etf_holdings_parser.py` - Core parser (273 lines)
- ✅ `tools/sec_tools/edgar_bulk_downloader.py` - Bulk download (280 lines)
- ✅ `tools/sec_tools/tests/test_etf_holdings_parser.py` - Unit tests (335 lines)

### Sample Data
- ✅ `etf_holdings.csv` (5.7KB) - Sample export
- ✅ `etf_holdings.xlsx` (9.4KB) - Excel format
- ✅ `primary_doc.xml` (58KB) - Real N-PORT filing

### Documentation
- ✅ `README.md` - Updated with bulk download section
- ✅ `BULK_DOWNLOAD_GUIDE.md` - Complete guide (350+ lines)
- ✅ Example scripts with usage demonstrations

## Dependencies

```
pandas>=2.0.0
requests>=2.28.0
lxml>=4.9.0
openpyxl>=3.0.0  # For Excel export
```

## Key Improvements

### ISIN Extraction
- Handles both N-PORT XML formats:
  - Format 1: `<isin value="DE0005140008"/>` (attribute)
  - Format 2: Nested `<identifierType>ISIN</identifierType>` structure
- Namespace-agnostic XML parsing
- Fallback strategies for edge cases

### Bulk Download
- Uses official SEC EDGAR API
- Automatic filing discovery
- Rate limiting with exponential backoff
- Progress tracking
- Error recovery

### Code Quality
- Proper package structure
- Type hints throughout
- Comprehensive docstrings
- 12 unit tests (100% passing)
- Modular, reusable functions

## Breaking Changes

None - this is a new feature addition.

## Migration Notes

Old usage (if any direct imports existed):
```python
from etf_holdings_parser import get_etf_holdings
```

New usage:
```python
from tools.sec_tools import get_etf_holdings
```

## Testing Instructions

```bash
# Run unit tests
python -m unittest tools.sec_tools.tests.test_etf_holdings_parser -v

# Test with real data
python tools/sec_tools/test_primary_doc.py

# Test bulk download (sample)
python tools/sec_tools/example_bulk_download.py
```

## Commits Included

- `38e32e6` - Reorganize code into tools/sec_tools package with unit tests
- `3eefa03` - Add bulk N-PORT downloader for historical fund holdings
- `eb6a58e` - Add Excel and CSV export functionality
- `1a2a74c` - Add display script for holdings with name, ISIN, % weight, and USD value
- `c6519bd` - Enhance ISIN extraction to support multiple N-PORT XML formats
- `86bffc3` - Add unified get_etf_holdings function for flexible input
- `a4f95da` - Add .gitignore for Python cache files
- `3df1886` - Add ETF holdings parser with ISIN extraction

## Checklist

- ✅ Code follows project standards
- ✅ All tests pass (12/12)
- ✅ Documentation is complete
- ✅ No breaking changes
- ✅ Backward compatible imports
- ✅ Ready for production use

## Screenshots / Output

### Test Results
```
test_isin_attribute_format ... ok
test_isin_nested_format ... ok
test_isin_with_multiple_identifiers ... ok
test_missing_isin ... ok
test_none_identifiers ... ok
test_parse_sample_xml ... ok
test_parse_multiple_holdings ... ok
test_read_from_file ... ok
test_from_file_path ... ok
test_from_url ... ok
test_from_xml_string ... ok
test_download_from_url ... ok

OK (12 tests)
```

### Sample Output
```
ETF HOLDINGS - 41 Total Positions
====================================================================================================

                                                Security Name         ISIN % Weight     USD Value
                                                       SAP SE DE0007164600 10.6773% $5,894,893.76
                                   Siemens Aktiengesellschaft DE0007236101 10.0337% $5,539,584.27
                                                   Allianz SE DE0008404005  7.9295% $4,377,817.94
                                                    Airbus SE NL0000235190  7.0710% $3,903,872.26
...

Total Portfolio Value: $55,196,718.89
Total Weight: 99.9768%
ISIN Coverage: 40/41 (97.6%)
```

---

**Ready to merge!** This PR provides a complete, tested, and production-ready SEC N-PORT parser with bulk download capabilities.
