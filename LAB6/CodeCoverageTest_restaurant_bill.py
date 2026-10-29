import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from restaurant_bill import bill_total, split_bill, table_wait


# =====================================================================
# Code Coverage Test Suite (Line Coverage Focus - >= 90%)
# =====================================================================

def test_bill_total_happy_hour_large_group():
    """Test happy hour discount and large party surcharge together."""
    # Exercises happy hour branch (line 10) and guests >= 8 surcharge (line 13)
    assert bill_total("rooftop", 2000, 8, True) == 2142


def test_bill_total_invalid_section():
    """Test exception for invalid seating section (line 6)."""
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("balcony", 1000, 2, False)


def test_bill_total_negative_food():
    """Test exception for negative food total (line 8)."""
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -10, 2, False)


def test_split_bill_invalid_people():
    """Test exception for people count < 1 (line 20)."""
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(100, 0, 10)


def test_split_bill_invalid_tip():
    """Test exception for negative tip (line 22)."""
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(100, 2, -1)


def test_split_bill_with_remainder():
    """Test uneven split requiring ceiling adjustment (line 26)."""
    # 100 + 10% = 110; 110 // 3 = 36; remainder 2 != 0 -> 37
    assert split_bill(100, 3, 10) == 37


def test_table_wait_call_ahead():
    """Test party exceeding 12 guests must call ahead (line 32)."""
    assert table_wait(14, 5, False) == "call ahead"


def test_table_wait_reservation():
    """Test party with reservation is seated immediately (line 34)."""
    assert table_wait(4, 0, True) == "seat now"


def test_table_wait_no_free_tables():
    """Test waitlist when no tables are available (line 36)."""
    assert table_wait(4, 0, False) == "waitlist"


def test_table_wait_large_party_limited_tables():
    """Test waitlist for party > 6 with only 1 free table (line 38)."""
    assert table_wait(8, 1, False) == "waitlist"


def test_table_wait_seat_now():
    """Test standard walk-in party accommodated (line 39)."""
    assert table_wait(4, 2, False) == "seat now"
