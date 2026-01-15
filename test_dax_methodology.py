"""
Test suite for DAX Index Methodology functions

Tests the fast exit, fast entry, regular exit, and regular entry rules
for DAX equity indices.
"""

import pandas as pd
import numpy as np
from dax_index_methodology import (
    fast_exit,
    fast_entry,
    regular_exit,
    regular_entry,
    apply_index_review,
    MDAX_RANKS,
    SDAX_RANKS,
    TECDAX_RANKS
)


def test_fast_exit():
    """Test the fast exit rule."""
    print("Test: Fast Exit Rule")
    print("=" * 80)

    # Test case 1: Constituent with rank > 60 should be removed
    df = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D'],
        'is_current_constituent': [True, True, False, False],
        'market_cap_rank': [65, 30, 40, 50]
    })

    print("\nTest Case 1: Remove constituent with rank 65, add candidate with rank 40")
    print("Input:")
    print(df.to_string(index=False))

    result = fast_exit(df)
    print("\nOutput:")
    print(result.to_string(index=False))

    # Verify: A should be removed, C should be added
    assert result.loc[0, 'is_current_constituent'] == False, "Stock A should be removed"
    assert result.loc[1, 'is_current_constituent'] == True, "Stock B should remain"
    assert result.loc[2, 'is_current_constituent'] == True, "Stock C should be added"
    assert result.loc[3, 'is_current_constituent'] == False, "Stock D should not be added"
    print("✓ Test passed")

    # Test case 2: Multiple constituents to remove
    df2 = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D', 'E', 'F'],
        'is_current_constituent': [True, True, True, False, False, False],
        'market_cap_rank': [70, 65, 30, 40, 45, 50]
    })

    print("\n" + "-" * 80)
    print("Test Case 2: Remove multiple constituents (ranks 70, 65), add best candidates")
    print("Input:")
    print(df2.to_string(index=False))

    result2 = fast_exit(df2)
    print("\nOutput:")
    print(result2.to_string(index=False))

    # Verify: A and B should be removed, D and E should be added (best candidates)
    assert result2.loc[0, 'is_current_constituent'] == False, "Stock A (rank 70) should be removed"
    assert result2.loc[1, 'is_current_constituent'] == False, "Stock B (rank 65) should be removed"
    assert result2.loc[2, 'is_current_constituent'] == True, "Stock C should remain"
    assert result2.loc[3, 'is_current_constituent'] == True, "Stock D (rank 40) should be added"
    assert result2.loc[4, 'is_current_constituent'] == True, "Stock E (rank 45) should be added"
    assert result2.loc[5, 'is_current_constituent'] == False, "Stock F (rank 50) should not be added"
    print("✓ Test passed")

    # Test case 3: No eligible candidates (all candidates have rank > 47)
    df3 = pd.DataFrame({
        'ticker': ['A', 'B', 'C'],
        'is_current_constituent': [True, True, False],
        'market_cap_rank': [65, 30, 50]
    })

    print("\n" + "-" * 80)
    print("Test Case 3: No eligible candidates (rank 50 > 47)")
    print("Input:")
    print(df3.to_string(index=False))

    result3 = fast_exit(df3)
    print("\nOutput:")
    print(result3.to_string(index=False))

    # Verify: A should remain (no eligible replacement)
    assert result3.loc[0, 'is_current_constituent'] == True, "Stock A should remain (no replacement)"
    assert result3.loc[2, 'is_current_constituent'] == False, "Stock C should not be added (rank > 47)"
    print("✓ Test passed")

    print("\n" + "=" * 80)
    print("All Fast Exit tests passed!\n")


def test_fast_entry():
    """Test the fast entry rule."""
    print("Test: Fast Entry Rule")
    print("=" * 80)

    # Test case 1: Candidate with rank <= 33 should be added
    df = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D'],
        'is_current_constituent': [True, True, False, False],
        'market_cap_rank': [50, 55, 30, 40]
    })

    print("\nTest Case 1: Add candidate with rank 30, remove constituent with rank 55")
    print("Input:")
    print(df.to_string(index=False))

    result = fast_entry(df)
    print("\nOutput:")
    print(result.to_string(index=False))

    # Verify: C should be added, B should be removed
    assert result.loc[0, 'is_current_constituent'] == True, "Stock A should remain"
    assert result.loc[1, 'is_current_constituent'] == False, "Stock B should be removed (rank 55 > 47)"
    assert result.loc[2, 'is_current_constituent'] == True, "Stock C should be added (rank 30 <= 33)"
    assert result.loc[3, 'is_current_constituent'] == False, "Stock D should not be added (rank 40 > 33)"
    print("✓ Test passed")

    # Test case 2: Multiple candidates qualify
    df2 = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D', 'E', 'F'],
        'is_current_constituent': [True, True, True, False, False, False],
        'market_cap_rank': [50, 55, 40, 25, 30, 35]
    })

    print("\n" + "-" * 80)
    print("Test Case 2: Add multiple candidates (ranks 25, 30), remove worst constituents")
    print("Input:")
    print(df2.to_string(index=False))

    result2 = fast_entry(df2)
    print("\nOutput:")
    print(result2.to_string(index=False))

    # Verify: D and E should be added, B and A should be removed
    assert result2.loc[0, 'is_current_constituent'] == False, "Stock A (rank 50) should be removed"
    assert result2.loc[1, 'is_current_constituent'] == False, "Stock B (rank 55) should be removed"
    assert result2.loc[2, 'is_current_constituent'] == True, "Stock C should remain"
    assert result2.loc[3, 'is_current_constituent'] == True, "Stock D (rank 25) should be added"
    assert result2.loc[4, 'is_current_constituent'] == True, "Stock E (rank 30) should be added"
    assert result2.loc[5, 'is_current_constituent'] == False, "Stock F (rank 35 > 33) should not be added"
    print("✓ Test passed")

    # Test case 3: No constituents to remove (all have rank <= 47)
    df3 = pd.DataFrame({
        'ticker': ['A', 'B', 'C'],
        'is_current_constituent': [True, True, False],
        'market_cap_rank': [40, 45, 30]
    })

    print("\n" + "-" * 80)
    print("Test Case 3: No constituents eligible for removal (all rank <= 47)")
    print("Input:")
    print(df3.to_string(index=False))

    result3 = fast_entry(df3)
    print("\nOutput:")
    print(result3.to_string(index=False))

    # Verify: C should not be added (no space)
    assert result3.loc[0, 'is_current_constituent'] == True, "Stock A should remain"
    assert result3.loc[1, 'is_current_constituent'] == True, "Stock B should remain"
    assert result3.loc[2, 'is_current_constituent'] == False, "Stock C should not be added (no space)"
    print("✓ Test passed")

    print("\n" + "=" * 80)
    print("All Fast Entry tests passed!\n")


def test_regular_exit():
    """Test the regular exit rule."""
    print("Test: Regular Exit Rule")
    print("=" * 80)

    # Test case 1: Constituent with rank > 53 should be removed
    df = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D'],
        'is_current_constituent': [True, True, False, False],
        'market_cap_rank': [55, 40, 45, 50]
    })

    print("\nTest Case 1: Remove constituent with rank 55, add candidate with rank 45")
    print("Input:")
    print(df.to_string(index=False))

    result = regular_exit(df)
    print("\nOutput:")
    print(result.to_string(index=False))

    # Verify: A should be removed, C should be added
    assert result.loc[0, 'is_current_constituent'] == False, "Stock A should be removed (rank 55 > 53)"
    assert result.loc[1, 'is_current_constituent'] == True, "Stock B should remain"
    assert result.loc[2, 'is_current_constituent'] == True, "Stock C should be added (rank 45 <= 47)"
    assert result.loc[3, 'is_current_constituent'] == False, "Stock D should not be added (rank 50 > 47)"
    print("✓ Test passed")

    # Test case 2: Boundary case (rank exactly at threshold)
    df2 = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D'],
        'is_current_constituent': [True, True, False, False],
        'market_cap_rank': [53, 54, 47, 48]
    })

    print("\n" + "-" * 80)
    print("Test Case 2: Boundary test (ranks at thresholds 53, 54, 47, 48)")
    print("Input:")
    print(df2.to_string(index=False))

    result2 = regular_exit(df2)
    print("\nOutput:")
    print(result2.to_string(index=False))

    # Verify: A (rank 53) should NOT be removed, B (rank 54) should be removed
    assert result2.loc[0, 'is_current_constituent'] == True, "Stock A (rank 53) should remain (not > 53)"
    assert result2.loc[1, 'is_current_constituent'] == False, "Stock B (rank 54) should be removed (54 > 53)"
    assert result2.loc[2, 'is_current_constituent'] == True, "Stock C (rank 47) should be added (47 <= 47)"
    assert result2.loc[3, 'is_current_constituent'] == False, "Stock D (rank 48) should not be added (48 > 47)"
    print("✓ Test passed")

    print("\n" + "=" * 80)
    print("All Regular Exit tests passed!\n")


def test_regular_entry():
    """Test the regular entry rule."""
    print("Test: Regular Entry Rule")
    print("=" * 80)

    # Test case: Regular entry is same as regular exit
    df = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D'],
        'is_current_constituent': [True, True, False, False],
        'market_cap_rank': [55, 40, 45, 50]
    })

    print("\nTest Case: Regular entry should produce same result as regular exit")
    print("Input:")
    print(df.to_string(index=False))

    result_entry = regular_entry(df)
    result_exit = regular_exit(df)

    print("\nRegular Entry Output:")
    print(result_entry.to_string(index=False))

    print("\nRegular Exit Output:")
    print(result_exit.to_string(index=False))

    # Verify they're identical
    pd.testing.assert_frame_equal(result_entry, result_exit)
    print("\n✓ Test passed: Regular entry and exit produce identical results")

    print("\n" + "=" * 80)
    print("All Regular Entry tests passed!\n")


def test_complete_review():
    """Test the complete review process."""
    print("Test: Complete Index Review")
    print("=" * 80)

    # Test case 1: Fast review (quarterly)
    df = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
        'is_current_constituent': [True, True, True, True, False, False, False, False],
        'market_cap_rank': [70, 55, 40, 30, 25, 32, 45, 50]
    })

    print("\nTest Case 1: Fast Review (applies both fast exit and fast entry)")
    print("Input:")
    print(df.to_string(index=False))

    result = apply_index_review(df, review_type='fast')
    print("\nOutput:")
    print(result.to_string(index=False))

    # Expected changes:
    # Fast Exit: A (70) removed, E (25) added (best candidate rank <= 47)
    # Fast Entry: F (32) added (rank <= 33), B (55) removed (rank > 47)
    assert result.loc[0, 'is_current_constituent'] == False, "A should be removed by fast exit"
    assert result.loc[1, 'is_current_constituent'] == False, "B should be removed by fast entry"
    assert result.loc[4, 'is_current_constituent'] == True, "E should be added by fast exit"
    assert result.loc[5, 'is_current_constituent'] == True, "F should be added by fast entry"
    print("✓ Test passed")

    # Test case 2: Regular review (semi-annual)
    df2 = pd.DataFrame({
        'ticker': ['A', 'B', 'C', 'D', 'E'],
        'is_current_constituent': [True, True, True, False, False],
        'market_cap_rank': [60, 55, 40, 45, 50]
    })

    print("\n" + "-" * 80)
    print("Test Case 2: Regular Review")
    print("Input:")
    print(df2.to_string(index=False))

    result2 = apply_index_review(df2, review_type='regular')
    print("\nOutput:")
    print(result2.to_string(index=False))

    # Expected: B (55) removed, D (45) added
    assert result2.loc[1, 'is_current_constituent'] == False, "B should be removed"
    assert result2.loc[3, 'is_current_constituent'] == True, "D should be added"
    print("✓ Test passed")

    print("\n" + "=" * 80)
    print("All Complete Review tests passed!\n")


def test_other_indices():
    """Test with rank limits for MDAX, SDAX, and TecDAX."""
    print("Test: Other DAX Indices (MDAX, SDAX, TecDAX)")
    print("=" * 80)

    # Test MDAX
    print("\nTest MDAX (Fast Exit: 110, Alt Candidate: 97)")
    df_mdax = pd.DataFrame({
        'ticker': ['A', 'B', 'C'],
        'is_current_constituent': [True, True, False],
        'market_cap_rank': [115, 50, 95]
    })

    print("Input:")
    print(df_mdax.to_string(index=False))

    result_mdax = fast_exit(
        df_mdax,
        fast_exit_rank=MDAX_RANKS['fast_exit_rank'],
        alt_candidate_rank=MDAX_RANKS['alt_candidate_rank']
    )
    print("\nOutput:")
    print(result_mdax.to_string(index=False))

    assert result_mdax.loc[0, 'is_current_constituent'] == False, "A should be removed (115 > 110)"
    assert result_mdax.loc[2, 'is_current_constituent'] == True, "C should be added (95 <= 97)"
    print("✓ MDAX test passed")

    # Test TecDAX
    print("\n" + "-" * 80)
    print("Test TecDAX (Fast Entry: 25, Alt Candidate: 35)")
    df_tecdax = pd.DataFrame({
        'ticker': ['A', 'B', 'C'],
        'is_current_constituent': [True, True, False],
        'market_cap_rank': [40, 38, 20]
    })

    print("Input:")
    print(df_tecdax.to_string(index=False))

    result_tecdax = fast_entry(
        df_tecdax,
        fast_entry_rank=TECDAX_RANKS['fast_entry_rank'],
        alt_candidate_rank=TECDAX_RANKS['alt_candidate_rank']
    )
    print("\nOutput:")
    print(result_tecdax.to_string(index=False))

    assert result_tecdax.loc[0, 'is_current_constituent'] == False, "A should be removed (40 > 35)"
    assert result_tecdax.loc[2, 'is_current_constituent'] == True, "C should be added (20 <= 25)"
    print("✓ TecDAX test passed")

    print("\n" + "=" * 80)
    print("All Other Indices tests passed!\n")


def run_all_tests():
    """Run all test suites."""
    print("\n" + "=" * 80)
    print("DAX INDEX METHODOLOGY - COMPREHENSIVE TEST SUITE")
    print("=" * 80 + "\n")

    try:
        test_fast_exit()
        test_fast_entry()
        test_regular_exit()
        test_regular_entry()
        test_complete_review()
        test_other_indices()

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED! ✓")
        print("=" * 80 + "\n")

    except AssertionError as e:
        print("\n" + "=" * 80)
        print(f"TEST FAILED: {e}")
        print("=" * 80 + "\n")
        raise


if __name__ == "__main__":
    run_all_tests()
