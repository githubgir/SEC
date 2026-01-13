"""
Test script for ETF Holdings Parser
"""

from etf_holdings_parser import parse_etf_holdings, get_etf_holdings_from_file

# Sample N-PORT XML structure for testing
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<edgarSubmission xmlns="http://www.sec.gov/edgar/nport">
    <formData>
        <invstOrSec>
            <name>Microsoft Corporation</name>
            <title>Common Stock</title>
            <cusip>594918104</cusip>
            <identifiers>
                <identifier>
                    <identifierType>ISIN</identifierType>
                    <identifierValue>US5949181045</identifierValue>
                </identifier>
                <identifier>
                    <identifierType>Ticker</identifierType>
                    <identifierValue>MSFT</identifierValue>
                </identifier>
            </identifiers>
            <balance>100000</balance>
            <units>NS</units>
            <valUSD>45000000</valUSD>
            <pctVal>8.5</pctVal>
            <curCd>USD</curCd>
            <assetCat>EC</assetCat>
            <issuerCat>CORP</issuerCat>
            <invCountry>US</invCountry>
        </invstOrSec>
        <invstOrSec>
            <name>Apple Inc</name>
            <title>Common Stock</title>
            <cusip>037833100</cusip>
            <identifiers>
                <identifier>
                    <identifierType>ISIN</identifierType>
                    <identifierValue>US0378331005</identifierValue>
                </identifier>
                <identifier>
                    <identifierType>Ticker</identifierType>
                    <identifierValue>AAPL</identifierValue>
                </identifier>
            </identifiers>
            <balance>150000</balance>
            <units>NS</units>
            <valUSD>42000000</valUSD>
            <pctVal>8.0</pctVal>
            <curCd>USD</curCd>
            <assetCat>EC</assetCat>
            <issuerCat>CORP</issuerCat>
            <invCountry>US</invCountry>
        </invstOrSec>
        <invstOrSec>
            <name>Amazon.com Inc</name>
            <title>Common Stock</title>
            <cusip>023135106</cusip>
            <identifiers>
                <identifier>
                    <identifierType>ISIN</identifierType>
                    <identifierValue>US0231351067</identifierValue>
                </identifier>
                <identifier>
                    <identifierType>Ticker</identifierType>
                    <identifierValue>AMZN</identifierValue>
                </identifier>
            </identifiers>
            <balance>80000</balance>
            <units>NS</units>
            <valUSD>38000000</valUSD>
            <pctVal>7.2</pctVal>
            <curCd>USD</curCd>
            <assetCat>EC</assetCat>
            <issuerCat>CORP</issuerCat>
            <invCountry>US</invCountry>
        </invstOrSec>
    </formData>
</edgarSubmission>
"""


def test_parser():
    """Test the parser with sample XML"""
    print("Testing ETF Holdings Parser")
    print("=" * 60)

    # Parse sample XML
    df = parse_etf_holdings(SAMPLE_XML)

    # Display results
    print(f"\nFound {len(df)} holdings")
    print(f"\nColumns: {list(df.columns)}")

    print("\n" + "=" * 60)
    print("Holdings Data:")
    print("=" * 60)
    print(df.to_string(index=False))

    # Verify ISIN extraction
    print("\n" + "=" * 60)
    print("ISIN Extraction Verification:")
    print("=" * 60)
    for idx, row in df.iterrows():
        print(f"{row['name']:25} | ISIN: {row['isin']}")

    # Summary statistics
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Total holdings: {len(df)}")
    print(f"Holdings with ISIN: {df['isin'].notna().sum()}")
    print(f"ISIN coverage: {100 * df['isin'].notna().sum() / len(df):.1f}%")
    print(f"Total value (USD): ${df['value_usd'].sum():,.0f}")
    print(f"Total percentage: {df['pct_value'].sum():.1f}%")

    return df


if __name__ == "__main__":
    df = test_parser()

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
    print("\nTo use with a real SEC EDGAR file:")
    print("1. Download the XML file from SEC EDGAR")
    print("2. Use: df = get_etf_holdings_from_file('primary_doc.xml')")
    print("\nOr download directly from URL:")
    print("   url = 'https://www.sec.gov/Archives/edgar/data/...xml'")
    print("   df = get_etf_holdings_from_url(url)")
