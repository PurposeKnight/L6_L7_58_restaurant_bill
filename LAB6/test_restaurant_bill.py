import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from restaurant_bill import bill_total, split_bill, table_wait


# =====================================================================
# Starter Test Cases (from handout)
# =====================================================================

def test_dine_in_bill():
    assert bill_total("dine_in", 1000, 2, False) == 1155


def test_even_split():
    assert split_bill(1000, 4, 10) == 275


# =====================================================================
# Additional Comprehensive Test Cases (Achieving 100% Coverage)
# =====================================================================

def test_bill_total_invalid_section():
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("terrace", 1000, 2, False)


def test_bill_total_negative_food():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -10, 2, False)


def test_bill_total_zero_guests():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", 500, 0, False)


def test_bill_total_happy_hour_and_large_party_rooftop():
    # food = 2000 * 80 // 100 = 1600; service = 1600 * 15 // 100 + 200 = 440
    # total = 2040, tax = 102 -> 2142
    assert bill_total("rooftop", 2000, 8, True) == 2142


def test_bill_total_happy_hour_takeaway():
    # takeaway has no happy hour discount and 0 service charge
    assert bill_total("takeaway", 500, 1, True) == 525


def test_split_bill_invalid_people():
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_split_bill_negative_tip():
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 4, -5)


def test_split_bill_with_remainder():
    # 100 + 10 = 110; 110 // 3 = 36; remainder != 0 -> 37
    assert split_bill(100, 3, 10) == 37


def test_table_wait_call_ahead():
    assert table_wait(13, 2, False) == "call ahead"


def test_table_wait_reservation():
    assert table_wait(4, 0, True) == "seat now"


def test_table_wait_zero_tables():
    assert table_wait(4, 0, False) == "waitlist"


def test_table_wait_large_party_limited_tables():
    assert table_wait(7, 1, False) == "waitlist"


def test_table_wait_large_party_sufficient_tables():
    assert table_wait(8, 2, False) == "seat now"


def test_table_wait_small_party_one_table():
    assert table_wait(4, 1, False) == "seat now"
