# Lab 7 — Fuzzing for Input Validation Bugs

This folder contains the three Lab 7 deliverables:

- `processor.py` — hardened versions of the three restaurant functions.
- `test_processor.py` — Hypothesis property-based fuzz tests.
- `Lab7_Fuzz_Testing_Report.pdf` — report with the four required screenshots.

## Reproduce the tests

```powershell
python -m pip install -r requirements.txt
python processor.py
python -m pytest test_processor.py -q
```

The test suite uses at least 150–250 generated examples per property and checks
both valid-domain behavior and malformed input rejection.
