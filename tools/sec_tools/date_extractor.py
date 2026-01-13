"""
Extract dates from SEC N-PORT XML filings

This module extracts key dates from N-PORT filings including:
- Reporting period end date (as of date for holdings)
- Report filing date (when filed with SEC)
"""

import xml.etree.ElementTree as ET
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path


def extract_nport_dates(xml_content: str) -> Dict[str, Optional[str]]:
    """
    Extract key dates from N-PORT XML filing.

    N-PORT filings contain several important dates:

    1. repPdEnd (Reporting Period End):
       - The date as of which the portfolio holdings are reported
       - This is the "as of" date for all positions, weights, and values
       - Format: YYYY-MM-DD

    2. repPdDate (Report Date):
       - The date the report was actually filed/submitted to SEC
       - Always after repPdEnd due to processing time
       - Format: YYYY-MM-DD

    3. filingDate (from header):
       - The official SEC filing date
       - When the document was accepted by EDGAR
       - Format: YYYY-MM-DD

    The delay between repPdEnd and filing dates represents:
    - Time to compile holdings data
    - Time to prepare the N-PORT report
    - Internal review and approval processes
    - SEC submission and processing

    Args:
        xml_content: XML content as string

    Returns:
        Dictionary with extracted dates:
        {
            'reporting_period_end': 'YYYY-MM-DD',  # Holdings "as of" date
            'report_date': 'YYYY-MM-DD',           # Report preparation date
            'filing_date': 'YYYY-MM-DD',           # SEC filing date
            'delay_days': int                       # Days between period end and filing
        }

    Example:
        >>> dates = extract_nport_dates(xml_content)
        >>> print(f"Holdings as of: {dates['reporting_period_end']}")
        >>> print(f"Filed with SEC: {dates['filing_date']}")
        >>> print(f"Delay: {dates['delay_days']} days")
    """
    root = ET.fromstring(xml_content)

    dates = {
        'reporting_period_end': None,
        'report_date': None,
        'filing_date': None,
        'delay_days': None
    }

    # Extract reporting period end date (the "as of" date for holdings)
    rep_pd_end = root.find('.//{*}repPdEnd')
    if rep_pd_end is not None and rep_pd_end.text:
        dates['reporting_period_end'] = rep_pd_end.text.strip()

    # Extract report date (when report was prepared)
    rep_pd_date = root.find('.//{*}repPdDate')
    if rep_pd_date is not None and rep_pd_date.text:
        dates['report_date'] = rep_pd_date.text.strip()

    # Extract filing date from header
    filing_date = root.find('.//{*}filingDate')
    if filing_date is not None and filing_date.text:
        dates['filing_date'] = filing_date.text.strip()

    # Calculate delay if we have both dates
    if dates['reporting_period_end'] and dates['filing_date']:
        try:
            end_date = datetime.strptime(dates['reporting_period_end'], '%Y-%m-%d')
            file_date = datetime.strptime(dates['filing_date'], '%Y-%m-%d')
            dates['delay_days'] = (file_date - end_date).days
        except ValueError:
            pass

    return dates


def extract_nport_dates_from_file(filepath: str) -> Dict[str, Optional[str]]:
    """
    Extract dates from N-PORT XML file.

    Args:
        filepath: Path to N-PORT XML file

    Returns:
        Dictionary with extracted dates

    Example:
        >>> dates = extract_nport_dates_from_file('primary_doc.xml')
        >>> print(dates)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    return extract_nport_dates(xml_content)


def format_date_info(dates: Dict[str, Optional[str]]) -> str:
    """
    Format date information for display.

    Args:
        dates: Dictionary from extract_nport_dates()

    Returns:
        Formatted string with date information
    """
    lines = []
    lines.append("N-PORT Filing Dates")
    lines.append("=" * 80)
    lines.append("")

    if dates['reporting_period_end']:
        lines.append(f"📅 Reporting Period End: {dates['reporting_period_end']}")
        lines.append("   (Holdings are 'as of' this date - positions, weights, values)")
        lines.append("")

    if dates['report_date']:
        lines.append(f"📝 Report Date: {dates['report_date']}")
        lines.append("   (Date the N-PORT report was prepared)")
        lines.append("")

    if dates['filing_date']:
        lines.append(f"📤 Filing Date: {dates['filing_date']}")
        lines.append("   (Date submitted to and accepted by SEC EDGAR)")
        lines.append("")

    if dates['delay_days'] is not None:
        lines.append(f"⏱️  Processing Delay: {dates['delay_days']} days")
        lines.append(f"   (Time from period end to SEC filing)")
        lines.append("")

        # Provide context
        if dates['delay_days'] <= 30:
            lines.append("   ✅ Quick turnaround (under 30 days)")
        elif dates['delay_days'] <= 60:
            lines.append("   📊 Normal processing time (30-60 days)")
        else:
            lines.append("   ⚠️  Extended processing (over 60 days)")
        lines.append("")

    lines.append("=" * 80)
    lines.append("")
    lines.append("EXPLANATION:")
    lines.append("")
    lines.append("1. REPORTING PERIOD END (repPdEnd)")
    lines.append("   - The 'as of' date for all portfolio holdings")
    lines.append("   - All position values, percentages, and balances are as of this date")
    lines.append("   - Typically the last day of a month (e.g., 2024-10-31)")
    lines.append("")
    lines.append("2. REPORT DATE (repPdDate)")
    lines.append("   - When the fund compiled and finalized the N-PORT report")
    lines.append("   - After the reporting period end")
    lines.append("")
    lines.append("3. FILING DATE (filingDate)")
    lines.append("   - When the report was submitted to SEC EDGAR")
    lines.append("   - The official public filing date")
    lines.append("   - Always after the reporting period end")
    lines.append("")
    lines.append("4. DELAY")
    lines.append("   - Time between period end and filing")
    lines.append("   - Includes: data collection, report preparation, review, submission")
    lines.append("   - Regulatory requirement: Must file within 60 days of period end")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "primary_doc.xml"

    print("Extracting dates from N-PORT filing...")
    print()

    dates = extract_nport_dates_from_file(filepath)

    print(format_date_info(dates))

    # Also show raw data
    print("RAW DATA:")
    print("=" * 80)
    for key, value in dates.items():
        print(f"{key}: {value}")
