"""
Display ETF holdings with name, ISIN, % weight, and USD value
"""

from etf_holdings_parser import get_etf_holdings
import pandas as pd

# Set pandas display options
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

# Parse the holdings
df = get_etf_holdings('primary_doc.xml')

# Select only the requested columns
holdings_display = df[['name', 'isin', 'pct_value', 'value_usd']].copy()

# Rename for clarity
holdings_display.columns = ['Name', 'ISIN', '% Weight', 'USD Value']

# Format for better readability
holdings_display['USD Value'] = holdings_display['USD Value'].apply(
    lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A"
)
holdings_display['% Weight'] = holdings_display['% Weight'].apply(
    lambda x: f"{x:.4f}%" if pd.notna(x) else "N/A"
)

print("="*100)
print(f"ETF HOLDINGS - {len(df)} Total Positions")
print("="*100)
print()
print(holdings_display.to_string(index=False))
print()
print("="*100)
print(f"Total Portfolio Value: ${df['value_usd'].sum():,.2f}")
print(f"Total Weight: {df['pct_value'].sum():.4f}%")
print(f"ISIN Coverage: {df['isin'].notna().sum()}/{len(df)} ({100*df['isin'].notna().sum()/len(df):.1f}%)")
print("="*100)
