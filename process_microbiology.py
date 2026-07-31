import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ws = '/Users/minyaozhu/Desktop/MicroBiology'
carved_dir = os.path.join(ws, 'carved_wells')
split_dir = os.path.join(ws, 'split_charts')
os.makedirs(carved_dir, exist_ok=True)
os.makedirs(split_dir, exist_ok=True)

# 1. Load images
wells_img = cv2.imread(os.path.join(ws, '12-wells.jpeg'))
charts_img = cv2.imread(os.path.join(ws, '12-charts.jpeg'))

# Centers and radius for wells (1024x650)
well_centers = {
    'A1': (190, 118), 'A2': (402, 118), 'A3': (614, 118), 'A4': (826, 118),
    'B1': (190, 332), 'B2': (402, 332), 'B3': (614, 332), 'B4': (826, 332),
    'C1': (190, 546), 'C2': (402, 546), 'C3': (614, 546), 'C4': (826, 546),
}
r_well = 102

# Chart grid dimensions (1024x462)
chart_w = 1024 // 4 # 256
chart_h = 462 // 3 # 154

chart_coords = {
    'A1': (0, 0), 'A2': (1, 0), 'A3': (2, 0), 'A4': (3, 0),
    'B1': (0, 1), 'B2': (1, 1), 'B3': (2, 1), 'B4': (3, 1),
    'C1': (0, 2), 'C2': (1, 2), 'C3': (2, 2), 'C4': (3, 2),
}

# Layout mapping & sorting high to low dose
dose_data = [
    ('A1', '50 ug/mL\n(No Bacteria)', 50.0),
    ('A2', '25 ug/mL', 25.0),
    ('A3', '12.5 ug/mL', 12.5),
    ('A4', '6.25 ug/mL', 6.25),
    ('B4', '3.13 ug/mL', 3.13),
    ('B3', '1.56 ug/mL', 1.56),
    ('B2', '0.78 ug/mL', 0.78),
    ('B1', '0.39 ug/mL', 0.39),
    ('C1', '0.195 ug/mL', 0.195),
    ('C2', '0.098 ug/mL', 0.098),
    ('C3', '0.098 ug/mL', 0.098),
    ('C4', 'No antibiotic\n(0 ug/mL)', 0.0),
]

carved_well_images = {}
split_chart_images = {}

# Process each of 12 positions
for idx, (well_id, dose_str, dose_val) in enumerate(dose_data):
    # --- Extract & Highlight Well ---
    cx, cy = well_centers[well_id]
    x1, y1 = cx - r_well - 5, cy - r_well - 5
    x2, y2 = cx + r_well + 5, cy + r_well + 5

    # Crop square area around well
    crop_w = wells_img[y1:y2, x1:x2].copy()

    # Create circular masked image with RGBA background
    h_c, w_c, _ = crop_w.shape
    mask = np.zeros((h_c, w_c), dtype=np.uint8)
    cv2.circle(mask, (w_c//2, h_c//2), r_well, 255, -1)

    # Highlight ring around circle
    highlight_img = crop_w.copy()
    cv2.circle(highlight_img, (w_c//2, h_c//2), r_well, (0, 220, 255), 4) # Vibrant cyan ring outline
    cv2.circle(highlight_img, (w_c//2, h_c//2), r_well + 2, (255, 255, 255), 2) # Outer white accent border

    # Convert to RGBA
    b, g, r_ch = cv2.split(highlight_img)
    rgba = cv2.merge([b, g, r_ch, mask])

    # Save individual carved well file with rank and well_id
    out_well_path1 = os.path.join(carved_dir, f'rank_{idx+1:02d}_well_{well_id}.png')
    out_well_path2 = os.path.join(carved_dir, f'well_{well_id}.png')
    cv2.imwrite(out_well_path1, rgba)
    cv2.imwrite(out_well_path2, rgba)
    carved_well_images[well_id] = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))

    # --- Extract Chart ---
    col, row = chart_coords[well_id]
    cx1 = col * chart_w
    cy1 = row * chart_h
    cx2 = cx1 + chart_w
    cy2 = cy1 + chart_h
    crop_chart = charts_img[cy1:cy2, cx1:cx2].copy()

    # Add a thin clean border around chart
    cv2.rectangle(crop_chart, (0, 0), (chart_w-1, chart_h-1), (200, 200, 200), 1)

    out_chart_path1 = os.path.join(split_dir, f'rank_{idx+1:02d}_chart_{well_id}.png')
    out_chart_path2 = os.path.join(split_dir, f'chart_{well_id}.png')
    cv2.imwrite(out_chart_path1, crop_chart)
    cv2.imwrite(out_chart_path2, crop_chart)
    split_chart_images[well_id] = Image.fromarray(cv2.cvtColor(crop_chart, cv2.COLOR_BGR2RGB))

print("Extracted 12 carved wells and 12 split charts.")

# --- Build High-Resolution Composite Image ---
num_cols = 12
col_width = 300
well_size = 220
chart_disp_w = 280
chart_disp_h = int(chart_disp_w * (chart_h / chart_w))

padding_x = 40
header_height = 130
col_header_height = 90
row1_y = header_height + col_header_height + 20
row2_y = row1_y + well_size + 60
footer_height = 40

canvas_w = padding_x * 2 + num_cols * col_width
canvas_h = row2_y + chart_disp_h + footer_height

# Dark sleek canvas
canvas = Image.new('RGB', (canvas_w, canvas_h), (18, 24, 38))
draw = ImageDraw.Draw(canvas)

# Load fonts with clean fallbacks
try:
    font_title = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 32)
    font_subtitle = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 18)
    font_rank = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 20)
    font_dose = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 16)
    font_label = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)
except Exception:
    font_title = font_subtitle = font_rank = font_dose = font_label = ImageFont.load_default()

# Header background banner
draw.rectangle([(0, 0), (canvas_w, header_height)], fill=(28, 36, 56))
draw.text((padding_x, 22), "Microbiology Antibiotic Dose Response Assay", fill=(255, 255, 255), font=font_title)
draw.text((padding_x, 72), "12 Wells & 12 Aligned Growth Charts Sorted by Antibiotic Dose (High -> Low)", fill=(0, 210, 255), font=font_subtitle)

# Process 12 sorted items in a row
for idx, (well_id, dose_str, dose_val) in enumerate(dose_data):
    col_x = padding_x + idx * col_width
    center_x = col_x + col_width // 2

    # Column Card Background highlight
    card_color = (25, 34, 52) if idx % 2 == 0 else (21, 29, 45)
    draw.rectangle([(col_x + 5, header_height + 10), (col_x + col_width - 5, canvas_h - 20)], fill=card_color, outline=(40, 52, 78), width=1)

    # Column Rank & ID Header
    draw.text((center_x, header_height + 25), f"#{idx+1}  [{well_id}]", fill=(255, 205, 60), font=font_rank, anchor='mm')
    
    # Dose Label Box
    dose_lines = dose_str.split('\n')
    y_text = header_height + 55
    for l_idx, line in enumerate(dose_lines):
        color = (100, 255, 180) if l_idx == 0 else (180, 180, 180)
        draw.text((center_x, y_text + l_idx * 18), line, fill=color, font=font_dose, anchor='mm')

    # Paste Carved Well
    well_img = carved_well_images[well_id].resize((well_size, well_size), Image.Resampling.LANCZOS)
    well_x = center_x - well_size // 2
    well_y = row1_y
    canvas.paste(well_img, (well_x, well_y), well_img)

    # Row label for Wells
    if idx == 0:
        draw.text((padding_x + 10, row1_y - 25), "WELLS (Carved & Highlighted)", fill=(255, 255, 255), font=font_label)

    # Alignment arrow / line between well and chart
    line_x = center_x
    draw.line([(line_x, well_y + well_size + 8), (line_x, row2_y - 12)], fill=(0, 180, 230), width=2)
    # Arrowhead pointing down
    draw.polygon([(line_x - 5, row2_y - 14), (line_x + 5, row2_y - 14), (line_x, row2_y - 6)], fill=(0, 180, 230))

    # Paste Split Chart
    chart_img = split_chart_images[well_id].resize((chart_disp_w, chart_disp_h), Image.Resampling.LANCZOS)
    chart_x = center_x - chart_disp_w // 2
    chart_y = row2_y
    canvas.paste(chart_img, (chart_x, chart_y))

    # Chart border accent
    draw.rectangle([(chart_x, chart_y), (chart_x + chart_disp_w, chart_y + chart_disp_h)], outline=(60, 80, 120), width=1)

    # Row label for Charts
    if idx == 0:
        draw.text((padding_x + 10, row2_y - 25), "GROWTH CHARTS (1-1 Aligned)", fill=(255, 255, 255), font=font_label)

out_composite_path = os.path.join(ws, 'sorted_wells_and_charts_row.png')
canvas.save(out_composite_path)
print(f"Updated composite image saved to {out_composite_path}")
