"""
DAX Equity Index Methodology - Selection Rules

This module implements the selection rules for DAX equity indices based on
the DAX Equity Index Methodology Guide (October 2023).

The module provides functions for:
- Fast Exit: Quarterly removal of constituents falling below specific thresholds
- Fast Entry: Quarterly addition of stocks rising above specific thresholds
- Regular Exit: Semi-annual removal during regular reviews
- Regular Entry: Semi-annual addition during regular reviews

References:
    - DAX Equity Index Methodology Guide (October 2023)
    - https://www.stoxx.com/document/News/2023/October/DAX%20Equity%20Index%20Methodology%20Guide_20231002.pdf

Rank Limits for DAX Index:
    - FAST_EXIT_RANK = 60 (constituents with rank > 60 are removed)
    - FAST_ENTRY_RANK = 33 (non-constituents with rank <= 33 are added)
    - REGULAR_EXIT_RANK = 53 (constituents with rank > 53 can be removed)
    - ALT_CANDIDATE_RANK = 47 (alternative candidates must have rank <= 47)
"""

import pandas as pd
import numpy as np
from typing import Optional


# Default rank limits for DAX index
# These can be overridden for other indices (MDAX, SDAX, TecDAX)
DEFAULT_FAST_EXIT_RANK = 60
DEFAULT_FAST_ENTRY_RANK = 33
DEFAULT_REGULAR_EXIT_RANK = 53
DEFAULT_ALT_CANDIDATE_RANK = 47


def fast_exit(
    selection_index: pd.DataFrame,
    fast_exit_rank: int = DEFAULT_FAST_EXIT_RANK,
    alt_candidate_rank: int = DEFAULT_ALT_CANDIDATE_RANK
) -> pd.DataFrame:
    """
    Apply fast exit rule to index constituents.

    Fast Exit Rule:
    A current constituent is removed from the index if its market cap rank is
    worse than (greater than) FAST_EXIT_RANK. It is replaced by the highest-ranked
    non-constituent with rank equal to or better than (<=) ALT_CANDIDATE_RANK.

    Args:
        selection_index: DataFrame with columns:
            - is_current_constituent (bool): Whether the stock is currently in the index
            - market_cap_rank (int): Market capitalization rank (1 = highest market cap)
        fast_exit_rank: Rank threshold for removal (default: 60 for DAX)
        alt_candidate_rank: Maximum rank for replacement candidates (default: 47 for DAX)

    Returns:
        DataFrame with revised is_current_constituent column

    Example:
        >>> df = pd.DataFrame({
        ...     'is_current_constituent': [True, True, False, False],
        ...     'market_cap_rank': [65, 30, 45, 50]
        ... })
        >>> result = fast_exit(df)
        >>> # Stock with rank 65 is removed, stock with rank 45 is added
    """
    # Create a copy to avoid modifying the original
    result = selection_index.copy()

    # Find constituents that violate the fast exit rule (rank > fast_exit_rank)
    constituents_to_remove = result[
        (result['is_current_constituent'] == True) &
        (result['market_cap_rank'] > fast_exit_rank)
    ].copy()

    # Find eligible replacement candidates (non-constituents with rank <= alt_candidate_rank)
    eligible_candidates = result[
        (result['is_current_constituent'] == False) &
        (result['market_cap_rank'] <= alt_candidate_rank)
    ].copy()

    # Sort both by rank (best rank first)
    constituents_to_remove = constituents_to_remove.sort_values('market_cap_rank')
    eligible_candidates = eligible_candidates.sort_values('market_cap_rank')

    # Perform replacements: one-to-one matching
    num_replacements = min(len(constituents_to_remove), len(eligible_candidates))

    if num_replacements > 0:
        # Remove the worst-ranked constituents
        result.loc[constituents_to_remove.index[:num_replacements], 'is_current_constituent'] = False

        # Add the best-ranked candidates
        result.loc[eligible_candidates.index[:num_replacements], 'is_current_constituent'] = True

    return result


def fast_entry(
    selection_index: pd.DataFrame,
    fast_entry_rank: int = DEFAULT_FAST_ENTRY_RANK,
    alt_candidate_rank: int = DEFAULT_ALT_CANDIDATE_RANK
) -> pd.DataFrame:
    """
    Apply fast entry rule to index constituents.

    Fast Entry Rule:
    A non-constituent is added to the index if its market cap rank is equal to or
    better than (<=) FAST_ENTRY_RANK. The removed constituent will have a rank
    worse than (>) ALT_CANDIDATE_RANK.

    Args:
        selection_index: DataFrame with columns:
            - is_current_constituent (bool): Whether the stock is currently in the index
            - market_cap_rank (int): Market capitalization rank (1 = highest market cap)
        fast_entry_rank: Rank threshold for entry (default: 33 for DAX)
        alt_candidate_rank: Minimum rank for constituents to be removed (default: 47 for DAX)

    Returns:
        DataFrame with revised is_current_constituent column

    Example:
        >>> df = pd.DataFrame({
        ...     'is_current_constituent': [True, True, False, False],
        ...     'market_cap_rank': [50, 55, 30, 35]
        ... })
        >>> result = fast_entry(df)
        >>> # Stock with rank 30 is added, stock with rank 55 is removed
    """
    # Create a copy to avoid modifying the original
    result = selection_index.copy()

    # Find non-constituents that qualify for fast entry (rank <= fast_entry_rank)
    candidates_to_add = result[
        (result['is_current_constituent'] == False) &
        (result['market_cap_rank'] <= fast_entry_rank)
    ].copy()

    # Find constituents that can be removed (rank > alt_candidate_rank)
    constituents_to_remove = result[
        (result['is_current_constituent'] == True) &
        (result['market_cap_rank'] > alt_candidate_rank)
    ].copy()

    # Sort both by rank
    candidates_to_add = candidates_to_add.sort_values('market_cap_rank')
    constituents_to_remove = constituents_to_remove.sort_values('market_cap_rank', ascending=False)

    # Perform replacements: one-to-one matching
    num_replacements = min(len(candidates_to_add), len(constituents_to_remove))

    if num_replacements > 0:
        # Add the best-ranked candidates
        result.loc[candidates_to_add.index[:num_replacements], 'is_current_constituent'] = True

        # Remove the worst-ranked constituents
        result.loc[constituents_to_remove.index[:num_replacements], 'is_current_constituent'] = False

    return result


def regular_exit(
    selection_index: pd.DataFrame,
    regular_exit_rank: int = DEFAULT_REGULAR_EXIT_RANK,
    alt_candidate_rank: int = DEFAULT_ALT_CANDIDATE_RANK
) -> pd.DataFrame:
    """
    Apply regular exit rule to index constituents.

    Regular Exit Rule:
    A current constituent can be removed from the index if its market cap rank is
    worse than (>) REGULAR_EXIT_RANK, provided that there is a non-constituent
    with rank equal to or better than (<=) ALT_CANDIDATE_RANK.

    Args:
        selection_index: DataFrame with columns:
            - is_current_constituent (bool): Whether the stock is currently in the index
            - market_cap_rank (int): Market capitalization rank (1 = highest market cap)
        regular_exit_rank: Rank threshold for removal (default: 53 for DAX)
        alt_candidate_rank: Maximum rank for replacement candidates (default: 47 for DAX)

    Returns:
        DataFrame with revised is_current_constituent column

    Example:
        >>> df = pd.DataFrame({
        ...     'is_current_constituent': [True, True, False, False],
        ...     'market_cap_rank': [55, 40, 45, 60]
        ... })
        >>> result = regular_exit(df)
        >>> # Stock with rank 55 is removed, stock with rank 45 is added
    """
    # Create a copy to avoid modifying the original
    result = selection_index.copy()

    # Find constituents that can be removed (rank > regular_exit_rank)
    constituents_to_remove = result[
        (result['is_current_constituent'] == True) &
        (result['market_cap_rank'] > regular_exit_rank)
    ].copy()

    # Find eligible replacement candidates (rank <= alt_candidate_rank)
    eligible_candidates = result[
        (result['is_current_constituent'] == False) &
        (result['market_cap_rank'] <= alt_candidate_rank)
    ].copy()

    # Sort both by rank
    constituents_to_remove = constituents_to_remove.sort_values('market_cap_rank')
    eligible_candidates = eligible_candidates.sort_values('market_cap_rank')

    # Perform replacements: one-to-one matching
    num_replacements = min(len(constituents_to_remove), len(eligible_candidates))

    if num_replacements > 0:
        # Remove the worst-ranked constituents
        result.loc[constituents_to_remove.index[:num_replacements], 'is_current_constituent'] = False

        # Add the best-ranked candidates
        result.loc[eligible_candidates.index[:num_replacements], 'is_current_constituent'] = True

    return result


def regular_entry(
    selection_index: pd.DataFrame,
    regular_exit_rank: int = DEFAULT_REGULAR_EXIT_RANK,
    alt_candidate_rank: int = DEFAULT_ALT_CANDIDATE_RANK
) -> pd.DataFrame:
    """
    Apply regular entry rule to index constituents.

    Regular Entry Rule:
    A non-constituent is added to the index if its market cap rank is equal to or
    better than (<=) ALT_CANDIDATE_RANK, provided that there is a constituent
    with rank worse than (>) REGULAR_EXIT_RANK.

    This is essentially the same as regular_exit, just described from the perspective
    of the entering stock rather than the exiting stock.

    Args:
        selection_index: DataFrame with columns:
            - is_current_constituent (bool): Whether the stock is currently in the index
            - market_cap_rank (int): Market capitalization rank (1 = highest market cap)
        regular_exit_rank: Minimum rank for constituents to be removed (default: 53 for DAX)
        alt_candidate_rank: Maximum rank for candidates to enter (default: 47 for DAX)

    Returns:
        DataFrame with revised is_current_constituent column

    Example:
        >>> df = pd.DataFrame({
        ...     'is_current_constituent': [True, True, False, False],
        ...     'market_cap_rank': [55, 40, 45, 60]
        ... })
        >>> result = regular_entry(df)
        >>> # Stock with rank 45 is added, stock with rank 55 is removed
    """
    # Regular entry is functionally identical to regular exit
    # Just a different perspective on the same rule
    return regular_exit(selection_index, regular_exit_rank, alt_candidate_rank)


def apply_index_review(
    selection_index: pd.DataFrame,
    review_type: str = 'regular',
    fast_exit_rank: int = DEFAULT_FAST_EXIT_RANK,
    fast_entry_rank: int = DEFAULT_FAST_ENTRY_RANK,
    regular_exit_rank: int = DEFAULT_REGULAR_EXIT_RANK,
    alt_candidate_rank: int = DEFAULT_ALT_CANDIDATE_RANK
) -> pd.DataFrame:
    """
    Apply complete index review process.

    Args:
        selection_index: DataFrame with eligible stocks
        review_type: Type of review - 'fast' (quarterly) or 'regular' (semi-annual)
        fast_exit_rank: Rank threshold for fast exit (default: 60 for DAX)
        fast_entry_rank: Rank threshold for fast entry (default: 33 for DAX)
        regular_exit_rank: Rank threshold for regular exit (default: 53 for DAX)
        alt_candidate_rank: Rank threshold for replacement candidates (default: 47 for DAX)

    Returns:
        DataFrame with revised is_current_constituent column

    Example:
        >>> df = pd.DataFrame({
        ...     'ticker': ['A', 'B', 'C', 'D'],
        ...     'is_current_constituent': [True, True, False, False],
        ...     'market_cap_rank': [65, 30, 25, 50]
        ... })
        >>> result = apply_index_review(df, review_type='fast')
    """
    result = selection_index.copy()

    if review_type == 'fast':
        # Apply fast exit first, then fast entry
        result = fast_exit(result, fast_exit_rank, alt_candidate_rank)
        result = fast_entry(result, fast_entry_rank, alt_candidate_rank)
    elif review_type == 'regular':
        # Apply regular exit/entry (they're the same rule)
        result = regular_exit(result, regular_exit_rank, alt_candidate_rank)
    else:
        raise ValueError(f"Invalid review_type: {review_type}. Must be 'fast' or 'regular'")

    return result


# Rank limits for other DAX indices
MDAX_RANKS = {
    'fast_exit_rank': 110,
    'fast_entry_rank': 83,
    'regular_exit_rank': 103,
    'alt_candidate_rank': 97
}

SDAX_RANKS = {
    'fast_exit_rank': 180,
    'fast_entry_rank': 153,
    'regular_exit_rank': 173,
    'alt_candidate_rank': 167
}

TECDAX_RANKS = {
    'fast_exit_rank': 45,
    'fast_entry_rank': 25,
    'regular_exit_rank': 40,
    'alt_candidate_rank': 35
}


if __name__ == "__main__":
    # Example usage
    print("DAX Index Methodology - Example")
    print("=" * 80)

    # Create sample data
    sample_data = pd.DataFrame({
        'ticker': ['STK1', 'STK2', 'STK3', 'STK4', 'STK5', 'STK6', 'STK7'],
        'is_current_constituent': [True, True, True, True, False, False, False],
        'market_cap_rank': [70, 40, 30, 55, 25, 45, 150]
    })

    print("\nInitial Selection Index:")
    print(sample_data.to_string(index=False))

    # Apply fast exit
    print("\n" + "=" * 80)
    print("After Fast Exit (removes rank > 60, replaces with rank <= 47):")
    result_fast_exit = fast_exit(sample_data)
    print(result_fast_exit.to_string(index=False))

    # Apply fast entry
    print("\n" + "=" * 80)
    print("After Fast Entry (adds rank <= 33, removes rank > 47):")
    result_fast_entry = fast_entry(sample_data)
    print(result_fast_entry.to_string(index=False))

    # Apply regular exit
    print("\n" + "=" * 80)
    print("After Regular Exit (removes rank > 53, replaces with rank <= 47):")
    result_regular = regular_exit(sample_data)
    print(result_regular.to_string(index=False))

    # Apply complete fast review
    print("\n" + "=" * 80)
    print("After Complete Fast Review (exit then entry):")
    result_complete = apply_index_review(sample_data, review_type='fast')
    print(result_complete.to_string(index=False))
