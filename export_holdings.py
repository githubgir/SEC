"""
Export ETF holdings to Excel and CSV files
"""

from etf_holdings_parser import get_etf_holdings
import pandas as pd

# Parse the holdings
print("Parsing ETF holdings from primary_doc.xml...")
df = get_etf_holdings('primary_doc.xml')

# Export to CSV
csv_filename = 'etf_holdings.csv'
df.to_csv(csv_filename, index=False)
print(f"✓ Saved to {csv_filename}")

# Export to Excel
excel_filename = 'etf_holdings.xlsx'
df.to_excel(excel_filename, index=False, sheet_name='Holdings')
print(f"✓ Saved to {excel_filename}")

# Summary
print(f"\nExport Summary:")
print(f"  Total holdings: {len(df)}")
print(f"  ISIN coverage: {df['isin'].notna().sum()}/{len(df)} ({100*df['isin'].notna().sum()/len(df):.1f}%)")
print(f"  Total value: ${df['value_usd'].sum():,.2f}")
print(f"  Total weight: {df['pct_value'].sum():.4f}%")
print(f"\nColumns exported: {', '.join(df.columns.tolist())}")
