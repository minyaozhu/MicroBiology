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
# Use new high-res single chart image 12-chart-single.png
charts_img = cv2.imread(os.path.join(ws, '12-chart-single.png'))

# Centers and radius for wells (1024x650)
well_centers = {
    'A1': (190, 118), 'A2': (402, 118), 'A3': (614, 118), 'A4': (826, 118),
    'B1': (190, 332), 'B2': (402, 332), 'B3': (614, 332), 'B4': (826, 332),
    'C1': (190, 546), 'C2': (402, 546), 'C3': (614, 546), 'C4': (826, 546),
}
r_well = 102

# Coordinates in 12-chart-single.png (2498 x 1294)
# 4 columns, 3 rows cropped precisely to remove global X/Y legends ("Signal (a.u.)", "Time (a.u.)")
col_bounds = [
    (90, 625),
    (700, 1235),
    (1300, 1835),
    (1900, 2435)
]
row_bounds = [
    (0, 350),
    (400, 750),
    (800, 1150)
]

# Map well_id to (col_index, row_index) in 12-chart-single.png
chart_single_coords = {
    'A1': (0, 0), # Panel 1
    'A2': (1, 0), # Panel 2
    'A3': (2, 0), # Panel 3
    'A4': (3, 0), # Panel 4
    'B4': (3, 1), # Panel 5
    'B3': (2, 1), # Panel 6
    'B2': (1, 1), # Panel 7
    'B1': (0, 1), # Panel 8
    'C1': (0, 2), # Panel 9
    'C2': (1, 2), # Panel 10
    'C3': (2, 2), # Panel 11
    'C4': (3, 2), # Panel 12
}

# Dose data sorted High to Low with Health Status mapping:
# #1~#4: Healthy (Green)
# #5: Sub-healthy (Yellow)
# #6~#12: Infection (Red)
dose_data = [
    ('A1', '50 ug/mL\n(No Bacteria)', 50.0, 'Healthy', '#10B981', (16, 185, 129)),
    ('A2', '25 ug/mL', 25.0, 'Healthy', '#10B981', (16, 185, 129)),
    ('A3', '12.5 ug/mL', 12.5, 'Healthy', '#10B981', (16, 185, 129)),
    ('A4', '6.25 ug/mL', 6.25, 'Healthy', '#10B981', (16, 185, 129)),
    ('B4', '3.13 ug/mL', 3.13, 'Sub-Healthy', '#F59E0B', (245, 158, 11)),
    ('B3', '1.56 ug/mL', 1.56, 'Infection', '#EF4444', (239, 68, 68)),
    ('B2', '0.78 ug/mL', 0.78, 'Infection', '#EF4444', (239, 68, 68)),
    ('B1', '0.39 ug/mL', 0.39, 'Infection', '#EF4444', (239, 68, 68)),
    ('C1', '0.195 ug/mL', 0.195, 'Infection', '#EF4444', (239, 68, 68)),
    ('C2', '0.098 ug/mL', 0.098, 'Infection', '#EF4444', (239, 68, 68)),
    ('C3', '0.098 ug/mL', 0.098, 'Infection', '#EF4444', (239, 68, 68)),
    ('C4', 'No antibiotic\n(0 ug/mL)', 0.0, 'Infection', '#EF4444', (239, 68, 68)),
]

carved_well_images_cyan = {}
carved_well_images_status = {}
split_chart_images = {}

# Extract each position
for idx, (well_id, dose_str, dose_val, status, color_hex, status_rgb) in enumerate(dose_data):
    cx, cy = well_centers[well_id]
    x1, y1 = cx - r_well - 5, cy - r_well - 5
    x2, y2 = cx + r_well + 5, cy + r_well + 5

    crop_w = wells_img[y1:y2, x1:x2].copy()
    h_c, w_c, _ = crop_w.shape
    mask = np.zeros((h_c, w_c), dtype=np.uint8)
    cv2.circle(mask, (w_c//2, h_c//2), r_well, 255, -1)

    # 1) Cyan highlight (V1)
    highlight_v1 = crop_w.copy()
    cv2.circle(highlight_v1, (w_c//2, h_c//2), r_well, (0, 220, 255), 4)
    cv2.circle(highlight_v1, (w_c//2, h_c//2), r_well + 2, (255, 255, 255), 2)
    b, g, r_ch = cv2.split(highlight_v1)
    rgba_v1 = cv2.merge([b, g, r_ch, mask])
    carved_well_images_cyan[well_id] = Image.fromarray(cv2.cvtColor(rgba_v1, cv2.COLOR_BGRA2RGBA))

    # 2) Status color highlight (V2)
    bgr_color = (status_rgb[2], status_rgb[1], status_rgb[0])
    highlight_v2 = crop_w.copy()
    cv2.circle(highlight_v2, (w_c//2, h_c//2), r_well, bgr_color, 4)
    cv2.circle(highlight_v2, (w_c//2, h_c//2), r_well + 2, (255, 255, 255), 2)
    b, g, r_ch = cv2.split(highlight_v2)
    rgba_v2 = cv2.merge([b, g, r_ch, mask])
    carved_well_images_status[well_id] = Image.fromarray(cv2.cvtColor(rgba_v2, cv2.COLOR_BGRA2RGBA))

    # Save files
    cv2.imwrite(os.path.join(carved_dir, f'rank_{idx+1:02d}_well_{well_id}.png'), rgba_v2)
    cv2.imwrite(os.path.join(carved_dir, f'well_{well_id}.png'), rgba_v2)

    # --- Extract Chart from 12-chart-single.png ---
    col_i, row_i = chart_single_coords[well_id]
    cx1, cx2 = col_bounds[col_i]
    cy1, cy2 = row_bounds[row_i]
    crop_chart = charts_img[cy1:cy2, cx1:cx2].copy()

    # Border matching status color
    cv2.rectangle(crop_chart, (0, 0), (crop_chart.shape[1]-1, crop_chart.shape[0]-1), bgr_color, 2)

    cv2.imwrite(os.path.join(split_dir, f'rank_{idx+1:02d}_chart_{well_id}.png'), crop_chart)
    cv2.imwrite(os.path.join(split_dir, f'chart_{well_id}.png'), crop_chart)
    split_chart_images[well_id] = Image.fromarray(cv2.cvtColor(crop_chart, cv2.COLOR_BGR2RGB))

# Common dimensions & fonts
num_cols = 12
col_width = 300
well_size = 220
chart_disp_w = 280
chart_disp_h = int(chart_disp_w * (350 / 535)) # Maintain aspect ratio (~183px)

try:
    font_title = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 32)
    font_subtitle = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 18)
    font_legend = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 16)
    font_rank = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 20)
    font_dose = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 16)
    font_label = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)
    font_bar = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 15)
except Exception:
    font_title = font_subtitle = font_legend = font_rank = font_dose = font_label = font_bar = ImageFont.load_default()

# ==========================================
# BUILD VERSION 1 (Standard Clean Composite)
# ==========================================
padding_x = 40
header_height_v1 = 130
col_header_height = 90
row1_y_v1 = header_height_v1 + col_header_height + 20
row2_y_v1 = row1_y_v1 + well_size + 60
footer_height = 40

canvas_w = padding_x * 2 + num_cols * col_width
canvas_h_v1 = row2_y_v1 + chart_disp_h + footer_height

canvas_v1 = Image.new('RGB', (canvas_w, canvas_h_v1), (18, 24, 38))
draw_v1 = ImageDraw.Draw(canvas_v1)

draw_v1.rectangle([(0, 0), (canvas_w, header_height_v1)], fill=(28, 36, 56))
draw_v1.text((padding_x, 22), "Microbiology Antibiotic Dose Response Assay (v1 Standard)", fill=(255, 255, 255), font=font_title)
draw_v1.text((padding_x, 72), "12 Wells & 12 Aligned Growth Charts Sorted by Antibiotic Dose (High -> Low)", fill=(0, 210, 255), font=font_subtitle)

for idx, (well_id, dose_str, dose_val, status, color_hex, status_rgb) in enumerate(dose_data):
    col_x = padding_x + idx * col_width
    center_x = col_x + col_width // 2

    card_color = (25, 34, 52) if idx % 2 == 0 else (21, 29, 45)
    draw_v1.rectangle([(col_x + 5, header_height_v1 + 10), (col_x + col_width - 5, canvas_h_v1 - 20)], fill=card_color, outline=(40, 52, 78), width=1)
    draw_v1.text((center_x, header_height_v1 + 25), f"#{idx+1}  [{well_id}]", fill=(255, 205, 60), font=font_rank, anchor='mm')
    
    dose_lines = dose_str.split('\n')
    y_text = header_height_v1 + 55
    for l_idx, line in enumerate(dose_lines):
        color = (100, 255, 180) if l_idx == 0 else (180, 180, 180)
        draw_v1.text((center_x, y_text + l_idx * 18), line, fill=color, font=font_dose, anchor='mm')

    well_img = carved_well_images_cyan[well_id].resize((well_size, well_size), Image.Resampling.LANCZOS)
    well_x = center_x - well_size // 2
    well_y = row1_y_v1
    canvas_v1.paste(well_img, (well_x, well_y), well_img)

    if idx == 0:
        draw_v1.text((padding_x + 10, row1_y_v1 - 25), "WELLS (Carved & Highlighted)", fill=(255, 255, 255), font=font_label)

    line_x = center_x
    draw_v1.line([(line_x, well_y + well_size + 8), (line_x, row2_y_v1 - 12)], fill=(0, 180, 230), width=2)
    draw_v1.polygon([(line_x - 5, row2_y_v1 - 14), (line_x + 5, row2_y_v1 - 14), (line_x, row2_y_v1 - 6)], fill=(0, 180, 230))

    chart_img = split_chart_images[well_id].resize((chart_disp_w, chart_disp_h), Image.Resampling.LANCZOS)
    chart_x = center_x - chart_disp_w // 2
    chart_y = row2_y_v1
    canvas_v1.paste(chart_img, (chart_x, chart_y))
    draw_v1.rectangle([(chart_x, chart_y), (chart_x + chart_disp_w, chart_y + chart_disp_h)], outline=(60, 80, 120), width=1)

    if idx == 0:
        draw_v1.text((padding_x + 10, row2_y_v1 - 25), "GROWTH CHARTS (1-1 Aligned)", fill=(255, 255, 255), font=font_label)

path_v1 = os.path.join(ws, 'sorted_wells_and_charts_v1_original.png')
canvas_v1.save(path_v1)
print(f"Saved Version 1 composite image to: {path_v1}")

# ========================================================
# BUILD VERSION 2 (Enhanced with Health Color Bars)
# ========================================================
header_height_v2 = 160
row1_y_v2 = header_height_v2 + col_header_height + 20
colorbar_height = 36
gap_well_chart = 75
row2_y_v2 = row1_y_v2 + well_size + gap_well_chart

canvas_h_v2 = row2_y_v2 + chart_disp_h + footer_height
canvas_v2 = Image.new('RGB', (canvas_w, canvas_h_v2), (18, 24, 38))
draw_v2 = ImageDraw.Draw(canvas_v2)

draw_v2.rectangle([(0, 0), (canvas_w, header_height_v2)], fill=(28, 36, 56))
draw_v2.text((padding_x, 22), "Microbiology Antibiotic Dose Response Assay (v2 Health Status)", fill=(255, 255, 255), font=font_title)
draw_v2.text((padding_x, 68), "12 Wells & 12 Aligned Growth Charts Sorted by Antibiotic Dose (High -> Low)", fill=(0, 210, 255), font=font_subtitle)

# Legend Bar
legend_y = 110
draw_v2.rectangle([(padding_x, legend_y), (padding_x + 18, legend_y + 18)], fill=(16, 185, 129))
draw_v2.text((padding_x + 26, legend_y), "Healthy (#1 - #4)", fill=(255, 255, 255), font=font_legend)

draw_v2.rectangle([(padding_x + 220, legend_y), (padding_x + 238, legend_y + 18)], fill=(245, 158, 11))
draw_v2.text((padding_x + 246, legend_y), "Sub-healthy (#5)", fill=(255, 255, 255), font=font_legend)

draw_v2.rectangle([(padding_x + 440, legend_y), (padding_x + 458, legend_y + 18)], fill=(239, 68, 68))
draw_v2.text((padding_x + 466, legend_y), "Infection (#6 - #12)", fill=(255, 255, 255), font=font_legend)

for idx, (well_id, dose_str, dose_val, status, color_hex, status_rgb) in enumerate(dose_data):
    col_x = padding_x + idx * col_width
    center_x = col_x + col_width // 2

    card_color = (25, 34, 52) if idx % 2 == 0 else (21, 29, 45)
    draw_v2.rectangle([(col_x + 5, header_height_v2 + 10), (col_x + col_width - 5, canvas_h_v2 - 20)], fill=card_color, outline=(40, 52, 78), width=1)

    draw_v2.text((center_x, header_height_v2 + 25), f"#{idx+1}  [{well_id}]", fill=(255, 205, 60), font=font_rank, anchor='mm')
    
    dose_lines = dose_str.split('\n')
    y_text = header_height_v2 + 55
    for l_idx, line in enumerate(dose_lines):
        color = status_rgb if l_idx == 0 else (180, 180, 180)
        draw_v2.text((center_x, y_text + l_idx * 18), line, fill=color, font=font_dose, anchor='mm')

    well_img = carved_well_images_status[well_id].resize((well_size, well_size), Image.Resampling.LANCZOS)
    well_x = center_x - well_size // 2
    well_y = row1_y_v2
    canvas_v2.paste(well_img, (well_x, well_y), well_img)

    if idx == 0:
        draw_v2.text((padding_x + 10, row1_y_v2 - 25), "WELLS (Carved & Highlighted)", fill=(255, 255, 255), font=font_label)

    # Color bar
    bar_y1 = well_y + well_size + 15
    bar_y2 = bar_y1 + colorbar_height
    bar_w = 260
    bar_x1 = center_x - bar_w // 2
    bar_x2 = center_x + bar_w // 2

    draw_v2.rounded_rectangle([(bar_x1, bar_y1), (bar_x2, bar_y2)], radius=8, fill=status_rgb, outline=(255, 255, 255), width=1)
    
    text_color = (0, 0, 0) if status == 'Sub-Healthy' else (255, 255, 255)
    draw_v2.text((center_x, bar_y1 + colorbar_height // 2), status.upper(), fill=text_color, font=font_bar, anchor='mm')

    draw_v2.line([(center_x, well_y + well_size + 2), (center_x, bar_y1 - 2)], fill=status_rgb, width=2)
    draw_v2.line([(center_x, bar_y2 + 2), (center_x, row2_y_v2 - 8)], fill=status_rgb, width=2)
    draw_v2.polygon([(center_x - 5, row2_y_v2 - 10), (center_x + 5, row2_y_v2 - 10), (center_x, row2_y_v2 - 3)], fill=status_rgb)

    chart_img = split_chart_images[well_id].resize((chart_disp_w, chart_disp_h), Image.Resampling.LANCZOS)
    chart_x = center_x - chart_disp_w // 2
    chart_y = row2_y_v2
    canvas_v2.paste(chart_img, (chart_x, chart_y))

    draw_v2.rectangle([(chart_x, chart_y), (chart_x + chart_disp_w, chart_y + chart_disp_h)], outline=status_rgb, width=2)

    if idx == 0:
        draw_v2.text((padding_x + 10, row2_y_v2 - 25), "GROWTH CHARTS (1-1 Aligned)", fill=(255, 255, 255), font=font_label)

path_v2 = os.path.join(ws, 'sorted_wells_and_charts_v2_colorbars.png')
canvas_v2.save(path_v2)
print(f"Saved Version 2 composite image to: {path_v2}")

# Main composite alias pointing to V2
path_main = os.path.join(ws, 'sorted_wells_and_charts_row.png')
canvas_v2.save(path_main)
print("Updated sorted_wells_and_charts_row.png")
