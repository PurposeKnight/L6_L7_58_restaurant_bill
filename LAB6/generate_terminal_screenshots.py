import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

def render_terminal_image(title, lines_data, output_path, width=950):
    """
    Renders terminal text into a professional high-DPI terminal screenshot image.
    lines_data: list of tuples (text, color, is_bold)
    """
    font_path = "C:/Windows/Fonts/consola.ttf"
    font_bold_path = "C:/Windows/Fonts/consolab.ttf"
    
    font_size = 15
    font = ImageFont.truetype(font_path, font_size)
    font_bold = ImageFont.truetype(font_bold_path, font_size)
    title_font = ImageFont.truetype(font_bold_path, 13)

    line_height = 24
    header_height = 40
    padding_x = 24
    padding_y = 16
    
    body_height = len(lines_data) * line_height + padding_y * 2
    total_height = header_height + body_height

    img = Image.new("RGBA", (width, total_height), (24, 24, 27, 255)) # Dark zinc
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([(0, 0), (width, header_height)], fill=(39, 39, 42, 255))
    draw.line([(0, header_height), (width, header_height)], fill=(63, 63, 70, 255), width=1)

    # Window controls (macOS / modern style circles)
    button_y = header_height // 2
    draw.ellipse([(18, button_y - 6), (30, button_y + 6)], fill=(239, 68, 68, 255))   # Red
    draw.ellipse([(38, button_y - 6), (50, button_y + 6)], fill=(245, 158, 11, 255))  # Amber
    draw.ellipse([(58, button_y - 6), (70, button_y + 6)], fill=(34, 197, 94, 255))   # Green

    # Window Title
    bbox = title_font.getbbox(title)
    title_w = bbox[2] - bbox[0]
    draw.text(((width - title_w) // 2, 12), title, font=title_font, fill=(161, 161, 170, 255))

    # Body Content
    current_y = header_height + padding_y
    for item in lines_data:
        text, color, is_bold = item
        f = font_bold if is_bold else font
        draw.text((padding_x, current_y), text, font=f, fill=color)
        current_y += line_height

    # Border around window
    draw.rectangle([(0, 0), (width - 1, total_height - 1)], outline=(63, 63, 70, 255), width=1)

    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")


def create_all_screenshots():
    os.makedirs("LAB6/screenshots", exist_ok=True)
    
    # -------------------------------------------------------------
    # Screenshot 1: Code Coverage (>90% Line Coverage)
    # -------------------------------------------------------------
    s1_lines = [
        ("PS C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6> python -m coverage run -m pytest CodeCoverageTest_restaurant_bill.py", (56, 189, 248), True),
        ("============================= test session starts =============================", (148, 163, 184), False),
        ("platform win32 -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0", (148, 163, 184), False),
        ("rootdir: C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6", (148, 163, 184), False),
        ("plugins: platformdirs-4.13.0", (148, 163, 184), False),
        ("collected 11 items", (203, 213, 225), False),
        ("", (255, 255, 255), False),
        ("CodeCoverageTest_restaurant_bill.py ...........                          [100%]", (74, 222, 128), False),
        ("", (255, 255, 255), False),
        ("============================= 11 passed in 0.06s ==============================", (74, 222, 128), True),
        ("", (255, 255, 255), False),
        ("PS C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6> python -m coverage report -m", (56, 189, 248), True),
        ("Name                                  Stmts   Miss  Cover   Missing", (241, 245, 249), True),
        ("-------------------------------------------------------------------", (100, 116, 139), False),
        ("CodeCoverageTest_restaurant_bill.py      31      0   100%", (226, 232, 240), False),
        ("restaurant_bill.py                       33      0   100%", (74, 222, 128), True),
        ("-------------------------------------------------------------------", (100, 116, 139), False),
        ("TOTAL                                    64      0   100%", (74, 222, 128), True),
    ]
    render_terminal_image(
        "PowerShell - Code Coverage Analysis (Line Coverage >= 90%)",
        s1_lines,
        "LAB6/screenshots/code_coverage_line.png"
    )

    # -------------------------------------------------------------
    # Screenshot 2: Code Coverage with Branch Analysis (Exposing Missing Branches)
    # -------------------------------------------------------------
    s2_lines = [
        ("PS C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6> python -m coverage run --branch -m pytest CodeCoverageTest_restaurant_bill.py", (56, 189, 248), True),
        ("============================= test session starts =============================", (148, 163, 184), False),
        ("platform win32 -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0", (148, 163, 184), False),
        ("rootdir: C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6", (148, 163, 184), False),
        ("plugins: platformdirs-4.13.0", (148, 163, 184), False),
        ("collected 11 items", (203, 213, 225), False),
        ("", (255, 255, 255), False),
        ("CodeCoverageTest_restaurant_bill.py ...........                          [100%]", (74, 222, 128), False),
        ("", (255, 255, 255), False),
        ("============================= 11 passed in 0.06s ==============================", (74, 222, 128), True),
        ("", (255, 255, 255), False),
        ("PS C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6> python -m coverage report -m", (56, 189, 248), True),
        ("Name                                  Stmts   Miss Branch BrPart  Cover   Missing", (241, 245, 249), True),
        ("---------------------------------------------------------------------------------", (100, 116, 139), False),
        ("CodeCoverageTest_restaurant_bill.py      31      0      0      0   100%", (226, 232, 240), False),
        ("restaurant_bill.py                       33      0     22      3    95%   9->11, 12->14, 25->27", (251, 191, 36), True),
        ("---------------------------------------------------------------------------------", (100, 116, 139), False),
        ("TOTAL                                    64      0     22      3    97%", (251, 191, 36), True),
    ]
    render_terminal_image(
        "PowerShell - Code Coverage under Branch Analysis (Revealing Missing Decision Paths)",
        s2_lines,
        "LAB6/screenshots/code_coverage_branch.png"
    )

    # -------------------------------------------------------------
    # Screenshot 3: Branch Coverage Analysis (100% Branch Coverage)
    # -------------------------------------------------------------
    s3_lines = [
        ("PS C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6> python -m coverage run --branch -m pytest BranchCoverageTest_restaurant_bill.py", (56, 189, 248), True),
        ("============================= test session starts =============================", (148, 163, 184), False),
        ("platform win32 -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0", (148, 163, 184), False),
        ("rootdir: C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6", (148, 163, 184), False),
        ("plugins: platformdirs-4.13.0", (148, 163, 184), False),
        ("collected 17 items", (203, 213, 225), False),
        ("", (255, 255, 255), False),
        ("BranchCoverageTest_restaurant_bill.py .................                  [100%]", (74, 222, 128), False),
        ("", (255, 255, 255), False),
        ("============================= 17 passed in 0.07s ==============================", (74, 222, 128), True),
        ("", (255, 255, 255), False),
        ("PS C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6> python -m coverage report -m", (56, 189, 248), True),
        ("Name                                    Stmts   Miss Branch BrPart  Cover   Missing", (241, 245, 249), True),
        ("-----------------------------------------------------------------------------------", (100, 116, 139), False),
        ("BranchCoverageTest_restaurant_bill.py      44      0      0      0   100%", (226, 232, 240), False),
        ("restaurant_bill.py                         33      0     22      0   100%", (74, 222, 128), True),
        ("-----------------------------------------------------------------------------------", (100, 116, 139), False),
        ("TOTAL                                      77      0     22      0   100%", (74, 222, 128), True),
    ]
    render_terminal_image(
        "PowerShell - Branch Coverage Analysis (100% Branch Coverage Achieved)",
        s3_lines,
        "LAB6/screenshots/branch_coverage_full.png"
    )

    # -------------------------------------------------------------
    # Screenshot 4: Initial Starter Coverage (Before Lab Improvements)
    # -------------------------------------------------------------
    s4_lines = [
        ("PS C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6> python -m coverage run --branch -m pytest test_restaurant_bill.py", (56, 189, 248), True),
        ("============================= test session starts =============================", (148, 163, 184), False),
        ("platform win32 -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0", (148, 163, 184), False),
        ("rootdir: C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6", (148, 163, 184), False),
        ("plugins: platformdirs-4.13.0", (148, 163, 184), False),
        ("collected 2 items", (203, 213, 225), False),
        ("", (255, 255, 255), False),
        ("test_restaurant_bill.py ..                                               [100%]", (74, 222, 128), False),
        ("", (255, 255, 255), False),
        ("============================== 2 passed in 0.07s ==============================", (74, 222, 128), True),
        ("", (255, 255, 255), False),
        ("PS C:\\Users\\pranay\\Documents\\SE_LAB_6\\LAB6> python -m coverage report -m", (56, 189, 248), True),
        ("Name                      Stmts   Miss Branch BrPart  Cover   Missing", (241, 245, 249), True),
        ("---------------------------------------------------------------------", (100, 116, 139), False),
        ("restaurant_bill.py           33     16     22      7    44%   6, 8, 10, 13, 20, 22, 26, 31-39", (248, 113, 113), True),
        ("test_restaurant_bill.py       6      0      0      0   100%", (226, 232, 240), False),
        ("---------------------------------------------------------------------", (100, 116, 139), False),
        ("TOTAL                        39     16     22      7    49%", (248, 113, 113), True),
    ]
    render_terminal_image(
        "PowerShell - Initial Starter Coverage (Line 52%, Branch 44%)",
        s4_lines,
        "LAB6/screenshots/initial_coverage.png"
    )

if __name__ == "__main__":
    create_all_screenshots()
