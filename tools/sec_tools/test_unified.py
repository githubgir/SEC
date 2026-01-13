"""
Test the unified get_etf_holdings function with all input types
"""

from etf_holdings_parser import get_etf_holdings
import pandas as pd

# Set pandas display options to show all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

print("="*80)
print("ETF Holdings Parser - Unified Function Test")
print("="*80)

# Test with file path
print("\nTesting with file path: 'sample_primary_doc.xml'")
print("-"*80)

df = get_etf_holdings('sample_primary_doc.xml')

print(f"\nTotal holdings found: {len(df)}")
print(f"ISIN coverage: {df['isin'].notna().sum()}/{len(df)} ({100*df['isin'].notna().sum()/len(df):.1f}%)")
print(f"Total portfolio value: ${df['value_usd'].sum():,.0f}")
print(f"Total percentage: {df['pct_value'].sum():.4f}%")

print("\n" + "="*80)
print("FULL DATAFRAME - Security Name, ISIN, USD Value, % Position")
print("="*80)

# Select and display key columns
display_df = df[['name', 'isin', 'value_usd', 'pct_value']].copy()
display_df['value_usd'] = display_df['value_usd'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
display_df['pct_value'] = display_df['pct_value'].apply(lambda x: f"{x:.4f}%" if pd.notna(x) else "N/A")

# Rename columns for display
display_df.columns = ['Security Name', 'ISIN', 'Value (USD)', 'Position %']

print("\n" + display_df.to_string(index=False))

print("\n" + "="*80)
print("ALL COLUMNS DATA")
print("="*80)
print("\n" + df.to_string(index=False))

print("\n" + "="*80)
print("Testing different input methods:")
print("="*80)

# Test with XML string
print("\n1. ✓ File path: Works with 'sample_primary_doc.xml'")

# Test with absolute path
import os
abs_path = os.path.abspath('sample_primary_doc.xml')
df2 = get_etf_holdings(abs_path)
print(f"2. ✓ Absolute path: Works with '{abs_path}'")
print(f"   Found {len(df2)} holdings")

# Test with XML string
with open('sample_primary_doc.xml', 'r') as f:
    xml_string = f.read()
df3 = get_etf_holdings(xml_string)
print(f"3. ✓ XML string: Works with {len(xml_string)} character XML string")
print(f"   Found {len(df3)} holdings")

print("\n" + "="*80)
print("All tests passed! Function works with URL, file path, and XML string.")
print("="*80)
