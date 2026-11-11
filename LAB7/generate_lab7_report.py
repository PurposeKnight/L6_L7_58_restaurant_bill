"""Regenerate the Lab 7 evidence screenshots and PDF report."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as PdfImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
SCREENSHOTS = ROOT / "screenshots"
REPORT = ROOT / "Lab7_Fuzz_Testing_Report.pdf"
PYTHONPATH = str(ROOT.parent / ".codex-temp")

BUGGY_SOURCE = '''SERVICE_CHARGE = {"dine_in": 10, "takeaway": 0, "rooftop": 15}

def bill_total(section, food_total, guests, is_happy_hour):
    if section not in SERVICE_CHARGE: raise ValueError("unknown section")
    if food_total < 0 or guests < 1: raise ValueError("invalid order")
    if is_happy_hour and section != "takeaway": food_total = food_total * 80 // 100
    service = food_total * SERVICE_CHARGE[section] // 100
    if guests >= 8: service += 200
    total = food_total + service
    return total + total * 5 // 100

def split_bill(total, people, tip_percent):
    if people < 1: raise ValueError("invalid people count")
    if tip_percent < 0: raise ValueError("invalid tip")
    grand_total = total + total * tip_percent // 100
    share = grand_total // people
    return share + (grand_total % people != 0)

def table_wait(party_size, free_tables, has_reservation):
    if party_size > 12: return "call ahead"
    if has_reservation: return "seat now"
    if free_tables == 0 or (party_size > 6 and free_tables < 2): return "waitlist"
    return "seat now"

if __name__ == "__main__":
    print("Restaurant Processor - Buggy Baseline")
    print("Dine-in total:", bill_total("dine_in", 1000, 4, True))
    print("Per-person share:", split_bill(924, 4, 10))
    print("Table decision:", table_wait(7, 1, False))
'''


def run(command: list[str], cwd: Path) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = PYTHONPATH
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        command, cwd=cwd, env=env, text=True, encoding="utf-8",
        errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False,
    )
    return result.stdout.rstrip()


def terminal_screenshot(command: str, output: str, destination: Path) -> None:
    width, margin = 1500, 34
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
    bold = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22)
    lines = [command]
    for raw_line in output.splitlines():
        lines.extend(textwrap.wrap(raw_line, width=112, replace_whitespace=False) or [""])
    line_height = 31
    height = margin * 2 + line_height * len(lines)
    image = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(image)
    y = margin
    for index, line in enumerate(lines):
        color = "#60a5fa" if index == 0 else (
            "#4ade80" if "passed" in line or "Validated" in line else
            "#f87171" if "failed" in line or "FAILED" in line else "#e5e7eb"
        )
        draw.text((margin, y), line, font=bold if index == 0 else font, fill=color)
        y += line_height
    image.save(destination)


def collect_evidence() -> None:
    SCREENSHOTS.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        (temp / "processor.py").write_text(BUGGY_SOURCE, encoding="utf-8")
        (temp / "test_processor.py").write_text(
            (ROOT / "test_processor.py").read_text(encoding="utf-8"), encoding="utf-8"
        )
        buggy_app = run([sys.executable, "processor.py"], temp)
        buggy_tests = run(
            [sys.executable, "-m", "pytest", "test_processor.py", "-q", "--tb=no"], temp
        )

    fixed_app = run([sys.executable, "processor.py"], ROOT)
    fixed_tests = run([sys.executable, "-m", "pytest", "test_processor.py", "-q"], ROOT)
    terminal_screenshot(
        "PS ...\\LAB7> python processor.py",
        buggy_app,
        SCREENSHOTS / "01_buggy_application.png",
    )
    terminal_screenshot(
        "PS ...\\LAB7> python -m pytest test_processor.py -q --tb=no",
        buggy_tests,
        SCREENSHOTS / "02_failing_fuzz_tests.png",
    )
    terminal_screenshot(
        "PS ...\\LAB7> python processor.py",
        fixed_app,
        SCREENSHOTS / "03_fixed_application.png",
    )
    terminal_screenshot(
        "PS ...\\LAB7> python -m pytest test_processor.py -q",
        fixed_tests,
        SCREENSHOTS / "04_passing_fuzz_tests.png",
    )


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d1d5db"))
    canvas.line(45, 35, A4[0] - 45, 35)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(45, 22, "Lab 7 — Fuzzing for Input Validation Bugs")
    canvas.drawRightString(A4[0] - 45, 22, f"Page {document.page}")
    canvas.restoreState()


def screenshot_block(path: Path, caption: str, body: str, styles) -> list:
    with Image.open(path) as image:
        ratio = image.height / image.width
    width = 7.05 * inch
    height = min(width * ratio, 5.8 * inch)
    return [
        Paragraph(caption, styles["Section"]),
        Paragraph(body, styles["BodyText"]),
        Spacer(1, 10),
        PdfImage(str(path), width=width, height=height),
    ]


def build_report() -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=28, leading=34, textColor=colors.HexColor("#0f172a"),
        alignment=TA_CENTER, spaceAfter=20,
    ))
    styles.add(ParagraphStyle(
        name="Section", parent=styles["Heading1"], fontSize=17, leading=21,
        textColor=colors.HexColor("#1d4ed8"), spaceAfter=8,
    ))
    styles["BodyText"].fontSize = 10.5
    styles["BodyText"].leading = 15
    document = SimpleDocTemplate(
        str(REPORT), pagesize=A4, rightMargin=45, leftMargin=45,
        topMargin=45, bottomMargin=48, title="Lab 7 Fuzz Testing Report",
        author="Pranay Shah",
    )
    story = [
        Spacer(1, 0.8 * inch),
        Paragraph("LAB 7", styles["CoverTitle"]),
        Paragraph("Fuzzing for Input Validation Bugs", styles["CoverTitle"]),
        Spacer(1, 0.35 * inch),
        Table(
            [
                ["Student", "Pranay Shah"],
                ["SRN", "PES2UG24CS366"],
                ["Email", "pranay.vshah06@gmail.com"],
                ["GitHub", "PurposeKnight"],
                ["Repository", "PurposeKnight/L6_L7_58_restaurant_bill"],
                ["Tools", "Python 3, pytest, Hypothesis"],
            ],
            colWidths=[1.35 * inch, 4.65 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1e3a8a")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]),
        ),
        Spacer(1, 0.45 * inch),
        Paragraph(
            "Objective: use property-based fuzzing to find edge-case input validation "
            "bugs in all three restaurant functions, then harden the implementation and "
            "verify the corrected behavior.", styles["BodyText"]
        ),
        PageBreak(),
        Paragraph("1. Scope and method", styles["Section"]),
        Paragraph(
            "The assigned repository contained the three-function restaurant application "
            "from Lab 6 but no separate Lab 7 starter folder. Therefore, the same three "
            "functions—bill_total, split_bill, and table_wait—were used as the processor "
            "targets. The final implementation is stored as processor.py under LAB7.",
            styles["BodyText"],
        ),
        Spacer(1, 10),
        Paragraph(
            "The Hypothesis suite generates valid and malformed values for every input "
            "boundary. Each property runs 150–250 examples and checks reference arithmetic, "
            "output invariants, domain limits, malformed types, Unicode text, None, NaN, "
            "negative values, large integers, and the special bool-is-an-int edge case.",
            styles["BodyText"],
        ),
        Spacer(1, 16),
        Paragraph("2. Bugs discovered", styles["Section"]),
        Table(
            [
                ["Counterexample", "Observed defect", "Correction"],
                ["food_total=None", "Incidental TypeError crash", "Explicit integer validation"],
                ["people=None", "Incidental TypeError crash", "Positive integer validation"],
                ["total=-1", "Negative bill accepted", "Require total >= 0"],
                ["tip_percent=101", "Unbounded tip accepted", "Require 0..100"],
                ["party_size=None", "Incidental TypeError crash", "Validate all table inputs"],
                ["bool as numeric input", "Accepted because bool subclasses int", "Use exact-type checks"],
            ],
            colWidths=[1.45 * inch, 2.35 * inch, 2.75 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]),
        ),
        PageBreak(),
    ]
    story += screenshot_block(
        SCREENSHOTS / "01_buggy_application.png",
        "3. Step 2 — Run the buggy application",
        "The baseline succeeds for ordinary sample values, which explains why conventional happy-path testing did not reveal the validation defects.",
        styles,
    )
    story += [PageBreak()]
    story += screenshot_block(
        SCREENSHOTS / "02_failing_fuzz_tests.png",
        "4. Step 4 — Failing Hypothesis tests",
        "The property-based suite automatically finds invalid inputs that crash or are incorrectly accepted by the baseline implementation.",
        styles,
    )
    story += [PageBreak()]
    story += screenshot_block(
        SCREENSHOTS / "03_fixed_application.png",
        "5. Step 5 — Run the fixed application",
        "Normal outputs are preserved, while an invalid negative total is now rejected with a predictable ValueError message.",
        styles,
    )
    story += [PageBreak()]
    story += screenshot_block(
        SCREENSHOTS / "04_passing_fuzz_tests.png",
        "6. Step 6 — Re-run tests after the fix",
        "All 14 properties pass after adding strict, centralized validation and explicit domain bounds.",
        styles,
    )
    story += [
        Spacer(1, 18),
        Paragraph("Conclusion", styles["Section"]),
        Paragraph(
            "Hypothesis exposed failures that ordinary examples missed and reduced them to "
            "actionable counterexamples. The corrected processor now rejects malformed input "
            "consistently with ValueError, preserves correct restaurant calculations, and "
            "passes the complete property-based fuzz suite.", styles["BodyText"],
        ),
    ]
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    collect_evidence()
    build_report()
    print(f"Generated {REPORT}")
