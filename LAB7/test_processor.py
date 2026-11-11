"""Property-based fuzz tests for all three restaurant processor functions."""

import math

import pytest
from hypothesis import given, settings, strategies as st

from processor import SERVICE_CHARGE, bill_total, split_bill, table_wait


VALID_SECTIONS = st.sampled_from(tuple(SERVICE_CHARGE))
VALID_MONEY = st.integers(min_value=0, max_value=10**12)
VALID_COUNTS = st.integers(min_value=1, max_value=10**6)
NON_INTEGERS = st.one_of(
    st.none(), st.booleans(), st.text(), st.floats(allow_nan=True), st.lists(st.integers())
)


@settings(max_examples=250, deadline=None)
@given(VALID_SECTIONS, VALID_MONEY, VALID_COUNTS, st.booleans())
def test_bill_total_matches_reference(section, food_total, guests, happy_hour):
    discounted = food_total
    if happy_hour and section != "takeaway":
        discounted = food_total * 80 // 100
    service = discounted * SERVICE_CHARGE[section] // 100
    if guests >= 8:
        service += 200
    subtotal = discounted + service
    expected = subtotal + subtotal * 5 // 100
    assert bill_total(section, food_total, guests, happy_hour) == expected


@settings(max_examples=150, deadline=None)
@given(st.one_of(st.none(), st.text().filter(lambda value: value not in SERVICE_CHARGE)))
def test_bill_total_rejects_unknown_sections(section):
    with pytest.raises(ValueError):
        bill_total(section, 100, 2, False)


@settings(max_examples=250, deadline=None)
@given(NON_INTEGERS)
def test_bill_total_rejects_non_integer_money(food_total):
    with pytest.raises(ValueError):
        bill_total("dine_in", food_total, 2, False)


@settings(max_examples=150, deadline=None)
@given(st.integers(max_value=-1), st.integers(min_value=1, max_value=20))
def test_bill_total_rejects_negative_money(food_total, guests):
    with pytest.raises(ValueError):
        bill_total("dine_in", food_total, guests, False)


@settings(max_examples=250, deadline=None)
@given(st.one_of(NON_INTEGERS, st.integers(max_value=0)), st.one_of(st.none(), st.integers(), st.text()))
def test_bill_total_rejects_invalid_guests_or_flag(guests, happy_hour):
    with pytest.raises(ValueError):
        bill_total("dine_in", 100, guests, happy_hour)


@settings(max_examples=250, deadline=None)
@given(VALID_MONEY, NON_INTEGERS)
def test_split_bill_rejects_invalid_people(total, people):
    with pytest.raises(ValueError):
        split_bill(total, people, 10)


@settings(max_examples=250, deadline=None)
@given(VALID_MONEY, VALID_COUNTS, st.integers(min_value=0, max_value=100))
def test_split_bill_is_ceiling_of_each_share(total, people, tip_percent):
    grand_total = total + total * tip_percent // 100
    assert split_bill(total, people, tip_percent) == math.ceil(grand_total / people)


@settings(max_examples=150, deadline=None)
@given(st.integers(max_value=-1), VALID_COUNTS, st.integers(min_value=0, max_value=100))
def test_split_bill_rejects_negative_total(total, people, tip_percent):
    with pytest.raises(ValueError):
        split_bill(total, people, tip_percent)


@settings(max_examples=150, deadline=None)
@given(VALID_MONEY, VALID_COUNTS, st.integers().filter(lambda value: not 0 <= value <= 100))
def test_split_bill_rejects_tip_outside_percentage_range(total, people, tip_percent):
    with pytest.raises(ValueError):
        split_bill(total, people, tip_percent)


@settings(max_examples=250, deadline=None)
@given(NON_INTEGERS, VALID_COUNTS, st.integers(min_value=0, max_value=100))
def test_split_bill_rejects_non_integer_total(total, people, tip_percent):
    with pytest.raises(ValueError):
        split_bill(total, people, tip_percent)


@settings(max_examples=250, deadline=None)
@given(VALID_MONEY, VALID_COUNTS, NON_INTEGERS)
def test_split_bill_rejects_non_integer_tip(total, people, tip_percent):
    with pytest.raises(ValueError):
        split_bill(total, people, tip_percent)


@settings(max_examples=250, deadline=None)
@given(st.integers(min_value=1, max_value=100), st.integers(min_value=0, max_value=100), st.booleans())
def test_table_wait_returns_valid_decision(party_size, free_tables, has_reservation):
    assert table_wait(party_size, free_tables, has_reservation) in {
        "call ahead", "seat now", "waitlist"
    }


@settings(max_examples=200, deadline=None)
@given(st.integers(min_value=13, max_value=100), st.integers(min_value=0, max_value=100), st.booleans())
def test_large_parties_always_call_ahead(party_size, free_tables, has_reservation):
    assert table_wait(party_size, free_tables, has_reservation) == "call ahead"


@settings(max_examples=250, deadline=None)
@given(
    NON_INTEGERS,
    NON_INTEGERS,
    st.one_of(st.none(), st.integers(), st.text()),
)
def test_table_wait_rejects_malformed_inputs(party_size, free_tables, has_reservation):
    with pytest.raises(ValueError):
        table_wait(party_size, free_tables, has_reservation)
