# DAX Index Methodology Implementation

This module implements the DAX Equity Index Methodology selection rules based on the official STOXX DAX Equity Index Methodology Guide (October 2023).

## Overview

The DAX index family uses a systematic approach to select and maintain index constituents. The methodology includes:

- **Fast Exit**: Quarterly removal of constituents falling below specific rank thresholds
- **Fast Entry**: Quarterly addition of stocks rising above specific rank thresholds
- **Regular Exit**: Semi-annual removal during regular reviews (March and September)
- **Regular Entry**: Semi-annual addition during regular reviews

## Rank Limits

### DAX (40 constituents)
- Fast Exit Rank: 60 (constituents with rank > 60 are removed)
- Fast Entry Rank: 33 (non-constituents with rank ≤ 33 are added)
- Regular Exit Rank: 53 (constituents with rank > 53 can be removed)
- Alternative Candidate Rank: 47 (replacement candidates must have rank ≤ 47)

### MDAX (Mid-Cap DAX)
- Fast Exit: 110, Fast Entry: 83, Regular Exit: 103, Alt Candidate: 97

### SDAX (Small-Cap DAX)
- Fast Exit: 180, Fast Entry: 153, Regular Exit: 173, Alt Candidate: 167

### TecDAX (Technology DAX)
- Fast Exit: 45, Fast Entry: 25, Regular Exit: 40, Alt Candidate: 35

## Selection Rules

### Fast Exit Rule
A current constituent is removed if its market cap rank is worse than (>) FAST_EXIT_RANK (60 for DAX). It is replaced by the highest-ranked non-constituent with rank ≤ ALT_CANDIDATE_RANK (47 for DAX).

**Example**: If a constituent drops to rank 65, it is removed and replaced by the best-ranked eligible candidate (rank ≤ 47).

### Fast Entry Rule
A non-constituent is added if its market cap rank is ≤ FAST_ENTRY_RANK (33 for DAX). The removed constituent will have rank > ALT_CANDIDATE_RANK (47 for DAX).

**Example**: If a non-constituent rises to rank 30, it enters the index, replacing the worst-ranked constituent with rank > 47.

### Regular Exit Rule
During semi-annual reviews, a constituent can be removed if its rank > REGULAR_EXIT_RANK (53 for DAX), provided there is a replacement candidate with rank ≤ ALT_CANDIDATE_RANK (47 for DAX).

### Regular Entry Rule
Functionally identical to regular exit, just described from the entering stock's perspective.

## Usage

### Basic Usage

```python
import pandas as pd
from dax_index_methodology import fast_exit, fast_entry, regular_exit, apply_index_review

# Create a selection index DataFrame
selection_index = pd.DataFrame({
    'ticker': ['A', 'B', 'C', 'D'],
    'is_current_constituent': [True, True, False, False],
    'market_cap_rank': [65, 30, 40, 50]
})

# Apply fast exit rule
result = fast_exit(selection_index)

# Apply fast entry rule
result = fast_entry(selection_index)

# Apply regular exit rule
result = regular_exit(selection_index)

# Apply complete quarterly review (fast exit + fast entry)
result = apply_index_review(selection_index, review_type='fast')

# Apply semi-annual review (regular exit/entry)
result = apply_index_review(selection_index, review_type='regular')
```

### Using Different Indices

```python
from dax_index_methodology import fast_exit, MDAX_RANKS, TECDAX_RANKS

# Apply MDAX rules
result = fast_exit(
    selection_index,
    fast_exit_rank=MDAX_RANKS['fast_exit_rank'],
    alt_candidate_rank=MDAX_RANKS['alt_candidate_rank']
)

# Apply TecDAX rules
result = fast_exit(
    selection_index,
    fast_exit_rank=TECDAX_RANKS['fast_exit_rank'],
    alt_candidate_rank=TECDAX_RANKS['alt_candidate_rank']
)
```

## Input Requirements

The `selection_index` DataFrame must have the following columns:
- `is_current_constituent` (bool): Whether the stock is currently in the index
- `market_cap_rank` (int): Market capitalization rank (1 = highest market cap, lower is better)

Additional columns (e.g., ticker, name, ISIN) can be included and will be preserved.

## Function Reference

### `fast_exit(selection_index, fast_exit_rank=60, alt_candidate_rank=47)`
Apply fast exit rule to remove underperforming constituents.

**Parameters:**
- `selection_index`: DataFrame with eligible stocks
- `fast_exit_rank`: Rank threshold for removal (default: 60)
- `alt_candidate_rank`: Maximum rank for replacement candidates (default: 47)

**Returns:** DataFrame with revised `is_current_constituent` column

### `fast_entry(selection_index, fast_entry_rank=33, alt_candidate_rank=47)`
Apply fast entry rule to add high-performing non-constituents.

**Parameters:**
- `selection_index`: DataFrame with eligible stocks
- `fast_entry_rank`: Rank threshold for entry (default: 33)
- `alt_candidate_rank`: Minimum rank for constituents to be removed (default: 47)

**Returns:** DataFrame with revised `is_current_constituent` column

### `regular_exit(selection_index, regular_exit_rank=53, alt_candidate_rank=47)`
Apply regular exit rule during semi-annual reviews.

**Parameters:**
- `selection_index`: DataFrame with eligible stocks
- `regular_exit_rank`: Rank threshold for removal (default: 53)
- `alt_candidate_rank`: Maximum rank for replacement candidates (default: 47)

**Returns:** DataFrame with revised `is_current_constituent` column

### `regular_entry(selection_index, regular_exit_rank=53, alt_candidate_rank=47)`
Apply regular entry rule (identical to regular exit).

### `apply_index_review(selection_index, review_type='regular', ...)`
Apply complete index review process.

**Parameters:**
- `selection_index`: DataFrame with eligible stocks
- `review_type`: 'fast' (quarterly) or 'regular' (semi-annual)
- Additional rank parameters (optional)

**Returns:** DataFrame with revised `is_current_constituent` column

## Testing

Run the comprehensive test suite:

```bash
python test_dax_methodology.py
```

The test suite includes:
- Fast exit rule tests
- Fast entry rule tests
- Regular exit/entry rule tests
- Complete review process tests
- Tests for other indices (MDAX, SDAX, TecDAX)
- Boundary condition tests

## Example Output

```
DAX Index Methodology - Example
================================================================================

Initial Selection Index:
ticker  is_current_constituent  market_cap_rank
  STK1                    True               70
  STK2                    True               40
  STK3                    True               30
  STK4                    True               55
  STK5                   False               25
  STK6                   False               45
  STK7                   False              150

After Fast Exit (removes rank > 60, replaces with rank <= 47):
ticker  is_current_constituent  market_cap_rank
  STK1                   False               70
  STK2                    True               40
  STK3                    True               30
  STK4                    True               55
  STK5                    True               25
  STK6                   False               45
  STK7                   False              150
```

## References

- [DAX Equity Index Methodology Guide (October 2023)](https://www.stoxx.com/document/News/2023/October/DAX%20Equity%20Index%20Methodology%20Guide_20231002.pdf)
- [Deutsche Börse - Index Adjustment Process](https://www.boerse-frankfurt.de/en/wissen/wertpapiere/aktien/the-index-adjustment-process)

## Dependencies

- pandas >= 2.0
- numpy >= 1.20

## License

This implementation is for educational and research purposes.
