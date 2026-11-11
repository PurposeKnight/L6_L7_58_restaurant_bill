"""Validated restaurant bill processor hardened through fuzz testing."""

SERVICE_CHARGE = {"dine_in": 10, "takeaway": 0, "rooftop": 15}


def bill_total(section, food_total, guests, is_happy_hour):
    """Return the final bill in whole currency units.

    Raises ValueError for every malformed or out-of-domain input so callers
    receive one predictable validation error instead of incidental TypeErrors.
    """
    if not isinstance(section, str) or section not in SERVICE_CHARGE:
        raise ValueError("section must be dine_in, takeaway, or rooftop")
    _require_int("food_total", food_total, minimum=0)
    _require_int("guests", guests, minimum=1)
    _require_bool("is_happy_hour", is_happy_hour)
    if is_happy_hour and section != "takeaway":
        food_total = food_total * 80 // 100
    service = food_total * SERVICE_CHARGE[section] // 100
    if guests >= 8:
        service += 200
    total = food_total + service
    return total + total * 5 // 100


def split_bill(total, people, tip_percent):
    """Return the ceiling of each diner's share after a 0-100% tip."""
    _require_int("total", total, minimum=0)
    _require_int("people", people, minimum=1)
    _require_int("tip_percent", tip_percent, minimum=0, maximum=100)
    grand_total = total + total * tip_percent // 100
    share = grand_total // people
    if grand_total % people != 0:
        share += 1
    return share


def table_wait(party_size, free_tables, has_reservation):
    """Return a seating decision for a validated party and table count."""
    _require_int("party_size", party_size, minimum=1)
    _require_int("free_tables", free_tables, minimum=0)
    _require_bool("has_reservation", has_reservation)
    if party_size > 12:
        return "call ahead"
    if has_reservation:
        return "seat now"
    if free_tables == 0:
        return "waitlist"
    if party_size > 6 and free_tables < 2:
        return "waitlist"
    return "seat now"


def _require_int(name, value, *, minimum, maximum=None):
    """Validate a true integer (bool is deliberately not accepted)."""
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    if value < minimum or (maximum is not None and value > maximum):
        bounds = f"{minimum}..{maximum}" if maximum is not None else f">= {minimum}"
        raise ValueError(f"{name} must be {bounds}")


def _require_bool(name, value):
    """Validate a real boolean rather than relying on truthiness."""
    if type(value) is not bool:
        raise ValueError(f"{name} must be a boolean")


if __name__ == "__main__":
    print("Restaurant Processor - Validated Version")
    print("Dine-in total:", bill_total("dine_in", 1000, 4, True))
    print("Per-person share:", split_bill(924, 4, 10))
    print("Table decision:", table_wait(7, 1, False))
    try:
        split_bill(-1, 2, 10)
    except ValueError as error:
        print("Invalid input rejected:", error)
