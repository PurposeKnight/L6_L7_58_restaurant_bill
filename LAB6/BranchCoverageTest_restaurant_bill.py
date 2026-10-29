import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from restaurant_bill import bill_total, split_bill, table_wait


# =====================================================================
# Branch Coverage Test Suite: Complete Coverage of All Decision Paths
# Evaluates every control branch to both True and False (100% Branch Coverage)
# =====================================================================

# ---------------------------------------------------------------------
# Branch Tests for bill_total()
# ---------------------------------------------------------------------

def test_bill_total_invalid_section_branch():
    """Branch: section not in SERVICE_CHARGE (True)."""
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("patio", 1000, 2, False)


def test_bill_total_negative_food_branch():
    """Branch: food_total < 0 evaluates to True in 'food_total < 0 or guests < 1'."""
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -1, 2, False)


def test_bill_total_zero_guests_branch():
    """Branch: guests < 1 evaluates to True in 'food_total < 0 or guests < 1'."""
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", 500, 0, False)


def test_bill_total_happy_hour_and_large_group_branch():
    """
    Branch tests:
    - is_happy_hour and section != 'takeaway' -> True
    - guests >= 8 -> True (boundary value 8)
    """
    # food = 2000 * 80 // 100 = 1600
    # service = 1600 * 15 // 100 = 240 + 200 = 440
    # total = 2040, tax 5% = 102 -> 2142
    assert bill_total("rooftop", 2000, 8, True) == 2142


def test_bill_total_no_happy_hour_branch():
    """
    Branch tests:
    - is_happy_hour and section != 'takeaway' -> False (is_happy_hour is False) [9->11]
    - guests >= 8 -> False (guests = 7, boundary test) [12->14]
    """
    # food = 1000, service = 1000 * 10 // 100 = 100 (no 200 surcharge)
    # total = 1100, tax 5% = 55 -> 1155
    assert bill_total("dine_in", 1000, 7, False) == 1155


def test_bill_total_happy_hour_takeaway_branch():
    """
    Branch test:
    - is_happy_hour is True BUT section == 'takeaway', so compound 'and' evaluates False.
    - takeaway service charge is 0%.
    """
    # food = 500 (no discount), service = 0
    # total = 500, tax 5% = 25 -> 525
    assert bill_total("takeaway", 500, 2, True) == 525


# ---------------------------------------------------------------------
# Branch Tests for split_bill()
# ---------------------------------------------------------------------

def test_split_bill_invalid_people_branch():
    """Branch: people < 1 -> True."""
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_split_bill_negative_tip_branch():
    """Branch: tip_percent < 0 -> True."""
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 4, -1)


def test_split_bill_with_remainder_branch():
    """Branch: grand_total % people != 0 -> True (ceiling division triggered)."""
    # grand_total = 100 + 10 = 110; 110 // 3 = 36; remainder 2 != 0 -> 37
    assert split_bill(100, 3, 10) == 37


def test_split_bill_even_split_branch():
    """Branch: grand_total % people != 0 -> False (exact split, no ceiling adjustment) [25->27]."""
    # grand_total = 1000 + 100 = 1100; 1100 // 4 = 275; remainder 0
    assert split_bill(1000, 4, 10) == 275


# ---------------------------------------------------------------------
# Branch Tests for table_wait()
# ---------------------------------------------------------------------

def test_table_wait_party_over_12_branch():
    """Branch: party_size > 12 -> True."""
    assert table_wait(13, 5, False) == "call ahead"


def test_table_wait_party_boundary_12_branch():
    """Branch: party_size > 12 -> False (boundary value 12)."""
    assert table_wait(12, 0, True) == "seat now"


def test_table_wait_reservation_branch():
    """Branch: has_reservation -> True."""
    assert table_wait(4, 0, True) == "seat now"


def test_table_wait_zero_tables_branch():
    """Branch: free_tables == 0 -> True."""
    assert table_wait(4, 0, False) == "waitlist"


def test_table_wait_large_party_limited_tables_branch():
    """Branch: party_size > 6 and free_tables < 2 -> True (party=7, free=1)."""
    assert table_wait(7, 1, False) == "waitlist"


def test_table_wait_large_party_sufficient_tables_branch():
    """Branch: party_size > 6 is True, but free_tables < 2 is False (party=8, free=2) -> 'seat now'."""
    assert table_wait(8, 2, False) == "seat now"


def test_table_wait_small_party_single_table_branch():
    """Branch: party_size > 6 is False, free_tables is 1 (party=6, free=1) -> 'seat now'."""
    assert table_wait(6, 1, False) == "seat now"
