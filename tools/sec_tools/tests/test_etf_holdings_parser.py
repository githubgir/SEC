"""
Unit tests for ETF Holdings Parser
"""

import unittest
import pandas as pd
import os
from pathlib import Path
from unittest.mock import patch, Mock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.sec_tools.etf_holdings_parser import (
    get_etf_holdings,
    get_etf_holdings_from_file,
    get_etf_holdings_from_url,
    parse_etf_holdings,
    extract_isin_from_identifiers
)
import xml.etree.ElementTree as ET


class TestISINExtraction(unittest.TestCase):
    """Test ISIN extraction from different XML formats"""

    def test_isin_attribute_format(self):
        """Test ISIN extraction from <isin value='...'> format"""
        xml = """
        <identifiers>
            <isin value="DE0005140008"/>
        </identifiers>
        """
        root = ET.fromstring(xml)
        isin = extract_isin_from_identifiers(root)
        self.assertEqual(isin, "DE0005140008")

    def test_isin_nested_format(self):
        """Test ISIN extraction from nested identifierType format"""
        xml = """
        <identifiers>
            <identifier>
                <identifierType>ISIN</identifierType>
                <identifierValue>US5949181045</identifierValue>
            </identifier>
        </identifiers>
        """
        root = ET.fromstring(xml)
        isin = extract_isin_from_identifiers(root)
        self.assertEqual(isin, "US5949181045")

    def test_isin_with_multiple_identifiers(self):
        """Test ISIN extraction when multiple identifier types present"""
        xml = """
        <identifiers>
            <identifier>
                <identifierType>Ticker</identifierType>
                <identifierValue>MSFT</identifierValue>
            </identifier>
            <identifier>
                <identifierType>ISIN</identifierType>
                <identifierValue>US5949181045</identifierValue>
            </identifier>
            <identifier>
                <identifierType>CUSIP</identifierType>
                <identifierValue>594918104</identifierValue>
            </identifier>
        </identifiers>
        """
        root = ET.fromstring(xml)
        isin = extract_isin_from_identifiers(root)
        self.assertEqual(isin, "US5949181045")

    def test_missing_isin(self):
        """Test when ISIN is not present"""
        xml = """
        <identifiers>
            <identifier>
                <identifierType>Ticker</identifierType>
                <identifierValue>MSFT</identifierValue>
            </identifier>
        </identifiers>
        """
        root = ET.fromstring(xml)
        isin = extract_isin_from_identifiers(root)
        self.assertIsNone(isin)

    def test_none_identifiers(self):
        """Test when identifiers element is None"""
        isin = extract_isin_from_identifiers(None)
        self.assertIsNone(isin)


class TestParseETFHoldings(unittest.TestCase):
    """Test parsing of ETF holdings from XML"""

    def test_parse_sample_xml(self):
        """Test parsing with sample N-PORT XML"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <edgarSubmission xmlns="http://www.sec.gov/edgar/nport">
            <formData>
                <invstOrSec>
                    <name>Microsoft Corporation</name>
                    <title>Common Stock</title>
                    <cusip>594918104</cusip>
                    <identifiers>
                        <isin value="US5949181045"/>
                    </identifiers>
                    <lei>INR2EJN1ERAN0W5ZP974</lei>
                    <balance>100000</balance>
                    <units>NS</units>
                    <valUSD>45000000</valUSD>
                    <pctVal>8.5</pctVal>
                    <curCd>USD</curCd>
                    <assetCat>EC</assetCat>
                    <issuerCat>CORP</issuerCat>
                    <invCountry>US</invCountry>
                </invstOrSec>
            </formData>
        </edgarSubmission>
        """
        df = parse_etf_holdings(xml)

        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], 'Microsoft Corporation')
        self.assertEqual(df.iloc[0]['isin'], 'US5949181045')
        self.assertEqual(df.iloc[0]['cusip'], '594918104')
        self.assertEqual(df.iloc[0]['value_usd'], 45000000.0)
        self.assertEqual(df.iloc[0]['pct_value'], 8.5)

    def test_parse_multiple_holdings(self):
        """Test parsing multiple holdings"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <edgarSubmission xmlns="http://www.sec.gov/edgar/nport">
            <formData>
                <invstOrSec>
                    <name>Microsoft Corporation</name>
                    <identifiers>
                        <isin value="US5949181045"/>
                    </identifiers>
                    <valUSD>45000000</valUSD>
                    <pctVal>8.5</pctVal>
                </invstOrSec>
                <invstOrSec>
                    <name>Apple Inc</name>
                    <identifiers>
                        <isin value="US0378331005"/>
                    </identifiers>
                    <valUSD>42000000</valUSD>
                    <pctVal>8.0</pctVal>
                </invstOrSec>
            </formData>
        </edgarSubmission>
        """
        df = parse_etf_holdings(xml)

        self.assertEqual(len(df), 2)
        self.assertIn('Microsoft Corporation', df['name'].values)
        self.assertIn('Apple Inc', df['name'].values)


class TestGetETFHoldingsFromFile(unittest.TestCase):
    """Test reading holdings from local file"""

    def setUp(self):
        """Create a temporary test file"""
        self.test_file = Path(__file__).parent / 'test_holdings.xml'
        self.test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <edgarSubmission xmlns="http://www.sec.gov/edgar/nport">
            <formData>
                <invstOrSec>
                    <name>Test Company</name>
                    <identifiers>
                        <isin value="US1234567890"/>
                    </identifiers>
                    <valUSD>1000000</valUSD>
                    <pctVal>1.5</pctVal>
                </invstOrSec>
            </formData>
        </edgarSubmission>
        """
        with open(self.test_file, 'w') as f:
            f.write(self.test_xml)

    def tearDown(self):
        """Remove temporary test file"""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_read_from_file(self):
        """Test reading and parsing from local file"""
        df = get_etf_holdings_from_file(str(self.test_file))

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], 'Test Company')
        self.assertEqual(df.iloc[0]['isin'], 'US1234567890')


class TestGetETFHoldings(unittest.TestCase):
    """Test the universal get_etf_holdings function"""

    def setUp(self):
        """Create a temporary test file"""
        self.test_file = Path(__file__).parent / 'test_universal.xml'
        self.test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <edgarSubmission xmlns="http://www.sec.gov/edgar/nport">
            <formData>
                <invstOrSec>
                    <name>Universal Test</name>
                    <identifiers>
                        <isin value="US9999999999"/>
                    </identifiers>
                    <valUSD>5000000</valUSD>
                </invstOrSec>
            </formData>
        </edgarSubmission>
        """
        with open(self.test_file, 'w') as f:
            f.write(self.test_xml)

    def tearDown(self):
        """Remove temporary test file"""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_from_file_path(self):
        """Test get_etf_holdings with file path"""
        df = get_etf_holdings(str(self.test_file))
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], 'Universal Test')

    def test_from_xml_string(self):
        """Test get_etf_holdings with XML string"""
        df = get_etf_holdings(self.test_xml)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], 'Universal Test')

    @patch('tools.sec_tools.etf_holdings_parser.requests.get')
    def test_from_url(self, mock_get):
        """Test get_etf_holdings with URL (mocked)"""
        # Mock the response
        mock_response = Mock()
        mock_response.text = self.test_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        df = get_etf_holdings('https://www.sec.gov/test.xml')
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], 'Universal Test')


class TestGetETFHoldingsFromURL(unittest.TestCase):
    """Test URL download functionality"""

    @patch('tools.sec_tools.etf_holdings_parser.requests.get')
    def test_download_from_url(self, mock_get):
        """Test downloading from URL with proper headers"""
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <edgarSubmission xmlns="http://www.sec.gov/edgar/nport">
            <formData>
                <invstOrSec>
                    <name>URL Test Company</name>
                    <identifiers>
                        <isin value="US1111111111"/>
                    </identifiers>
                    <valUSD>2000000</valUSD>
                </invstOrSec>
            </formData>
        </edgarSubmission>
        """

        # Mock the response
        mock_response = Mock()
        mock_response.text = test_xml
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        test_url = "https://www.sec.gov/Archives/edgar/data/1234567/test.xml"
        df = get_etf_holdings_from_url(test_url)

        # Verify request was made
        mock_get.assert_called_once()
        call_args = mock_get.call_args

        # Check URL
        self.assertEqual(call_args[0][0], test_url)

        # Check headers
        headers = call_args[1]['headers']
        self.assertIn('User-Agent', headers)
        self.assertIn('Host', headers)

        # Check result
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], 'URL Test Company')


if __name__ == '__main__':
    unittest.main()
