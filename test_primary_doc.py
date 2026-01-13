"""
Test script to parse primary_doc.xml and display full dataframe
Run this with your actual primary_doc.xml file
"""

from etf_holdings_parser import get_etf_holdings
import pandas as pd
import sys

# Set pandas display options to show ALL rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

print("="*100)
print("ETF Holdings Parser - Testing with primary_doc.xml")
print("="*100)

try:
    # Use the unified function - works with URL, file path, or XML string
    df = get_etf_holdings('primary_doc.xml')

    print(f"\n✓ Successfully parsed primary_doc.xml")
    print(f"  Total holdings found: {len(df)}")
    print(f"  ISIN coverage: {df['isin'].notna().sum()}/{len(df)} ({100*df['isin'].notna().sum()/len(df):.1f}%)")

    if len(df) > 0:
        print(f"  Total portfolio value: ${df['value_usd'].sum():,.0f}")
        print(f"  Total percentage: {df['pct_value'].sum():.4f}%")

    print("\n" + "="*100)
    print("FULL DATAFRAME - Security Name, ISIN, USD Value, % Position")
    print("="*100)

    # Key columns for display
    if len(df) > 0:
        key_cols = ['name', 'isin', 'value_usd', 'pct_value']
        display_df = df[key_cols].copy()

        # Format for readability
        display_df['value_usd'] = display_df['value_usd'].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
        )
        display_df['pct_value'] = display_df['pct_value'].apply(
            lambda x: f"{x:.4f}%" if pd.notna(x) else "N/A"
        )

        display_df.columns = ['Security Name', 'ISIN', 'Value (USD)', 'Position %']

        print("\n" + display_df.to_string(index=False))

        print("\n" + "="*100)
        print("ALL COLUMNS - COMPLETE DATA")
        print("="*100)
        print("\n" + df.to_string(index=False))

        # Top 10 holdings
        if len(df) >= 10:
            print("\n" + "="*100)
            print("TOP 10 HOLDINGS BY VALUE")
            print("="*100)
            top10 = df.nlargest(10, 'value_usd')[['name', 'isin', 'value_usd', 'pct_value']].copy()
            top10['value_usd'] = top10['value_usd'].apply(lambda x: f"${x:,.0f}")
            top10['pct_value'] = top10['pct_value'].apply(lambda x: f"{x:.4f}%")
            print("\n" + top10.to_string(index=False))

        # Export to CSV
        csv_filename = 'etf_holdings_output.csv'
        df.to_csv(csv_filename, index=False)
        print(f"\n✓ Data exported to {csv_filename}")

    else:
        print("\n⚠ No holdings found in the file")

except FileNotFoundError:
    print("\n✗ Error: primary_doc.xml not found")
    print("  Make sure the file exists in the current directory")
    sys.exit(1)

except Exception as e:
    print(f"\n✗ Error parsing file: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*100)
print("USAGE EXAMPLES:")
print("="*100)
print("""
The get_etf_holdings() function works with three input types:

1. File path (relative or absolute):
   df = get_etf_holdings('primary_doc.xml')
   df = get_etf_holdings('/path/to/file.xml')

2. URL:
   df = get_etf_holdings('https://www.sec.gov/Archives/edgar/data/.../primary_doc.xml')

3. XML string:
   with open('primary_doc.xml', 'r') as f:
       xml_content = f.read()
   df = get_etf_holdings(xml_content)
""")
print("="*100)
