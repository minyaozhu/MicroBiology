import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ws = '/Users/minyaozhu/Desktop/MicroBiology'

carved_dir = os.path.join(ws, 'carved_wells')
split_dir = os.path.join(ws, 'split_charts')

os.makedirs(carved_dir, exist_ok=True)
os.makedirs(split_dir, exist_ok=True)

# 1. Load source images
wells_img = cv2.imread(os.path.join(ws, '12-wells.jpeg'))
charts_img = cv2.imread(os.path.join(ws, '12-charts-v2.jpg'))

# Centers and radius for wells (1024x650)
well_centers = {
    'A1': (190, 118), 'A2': (402, 118), 'A3': (614, 118), 'A4': (826, 118),
    'B1': (190, 332), 'B2': (402, 332), 'B3': (614, 332), 'B4': (826, 332),
    'C1': (190, 546), 'C2': (402, 546), 'C3': (614, 546), 'C4': (826, 546),
}
r_well = 102

# Crop bounds for 12-charts-v2.jpg (1868 x 842)
col_bounds = [(0, 467), (467, 934), (934, 1401), (1401, 1868)]
row_bounds = [(0, 276), (280, 556), (560, 840)]

chart_coords = {
    'A1': (0, 0), 'A2': (1, 0), 'A3': (2, 0), 'A4': (3, 0),
    'B1': (0, 1), 'B2': (1, 1), 'B3': (2, 1), 'B4': (3, 1),
    'C1': (0, 2), 'C2': (1, 2), 'C3': (2, 2), 'C4': (3, 2),
}

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

carved_well_images = {}
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

    bgr_color = (status_rgb[2], status_rgb[1], status_rgb[0])
    highlight_img = crop_w.copy()
    cv2.circle(highlight_img, (w_c//2, h_c//2), r_well, bgr_color, 4)
    cv2.circle(highlight_img, (w_c//2, h_c//2), r_well + 2, (255, 255, 255), 2)

    b, g, r_ch = cv2.split(highlight_img)
    rgba = cv2.merge([b, g, r_ch, mask])

    out_well_path = os.path.join(carved_dir, f'well_{well_id}.png')
    cv2.imwrite(out_well_path, rgba)
    carved_well_images[well_id] = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))

    col_i, row_i = chart_coords[well_id]
    cx1, cx2 = col_bounds[col_i]
    cy1, cy2 = row_bounds[row_i]
    crop_chart = charts_img[cy1:cy2, cx1:cx2].copy()

    cv2.rectangle(crop_chart, (0, 0), (crop_chart.shape[1]-1, crop_chart.shape[0]-1), bgr_color, 2)
    out_chart_path = os.path.join(split_dir, f'chart_{well_id}.png')
    cv2.imwrite(out_chart_path, crop_chart)
    split_chart_images[well_id] = Image.fromarray(cv2.cvtColor(crop_chart, cv2.COLOR_BGR2RGB))

print("Extracted 12 carved wells and 12 split charts.")

# Composite Image
num_cols = 12
col_width = 300
well_size = 220
chart_disp_w = 280
chart_disp_h = int(chart_disp_w * (276 / 467))

padding_x = 40
header_height = 160
col_header_height = 90
row1_y = header_height + col_header_height + 20
colorbar_height = 36
gap_well_chart = 75
row2_y = row1_y + well_size + gap_well_chart
footer_height = 40

canvas_w = padding_x * 2 + num_cols * col_width
canvas_h = row2_y + chart_disp_h + footer_height

canvas = Image.new('RGB', (canvas_w, canvas_h), (18, 24, 38))
draw = ImageDraw.Draw(canvas)

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

draw.rectangle([(0, 0), (canvas_w, header_height)], fill=(28, 36, 56))
draw.text((padding_x, 22), "Microbiology Antibiotic Dose Response Assay", fill=(255, 255, 255), font=font_title)
draw.text((padding_x, 68), "12 Wells & 12 Aligned Growth Charts Sorted by Antibiotic Dose (High -> Low)", fill=(0, 210, 255), font=font_subtitle)

legend_y = 110
draw.rectangle([(padding_x, legend_y), (padding_x + 18, legend_y + 18)], fill=(16, 185, 129))
draw.text((padding_x + 26, legend_y), "Healthy (#1 - #4)", fill=(255, 255, 255), font=font_legend)

draw.rectangle([(padding_x + 220, legend_y), (padding_x + 238, legend_y + 18)], fill=(245, 158, 11))
draw.text((padding_x + 246, legend_y), "Sub-healthy (#5)", fill=(255, 255, 255), font=font_legend)

draw.rectangle([(padding_x + 440, legend_y), (padding_x + 458, legend_y + 18)], fill=(239, 68, 68))
draw.text((padding_x + 466, legend_y), "Infection (#6 - #12)", fill=(255, 255, 255), font=font_legend)

for idx, (well_id, dose_str, dose_val, status, color_hex, status_rgb) in enumerate(dose_data):
    col_x = padding_x + idx * col_width
    center_x = col_x + col_width // 2

    card_color = (25, 34, 52) if idx % 2 == 0 else (21, 29, 45)
    draw.rectangle([(col_x + 5, header_height + 10), (col_x + col_width - 5, canvas_h - 20)], fill=card_color, outline=(40, 52, 78), width=1)

    draw.text((center_x, header_height + 25), f"#{idx+1}  [{well_id}]", fill=(255, 205, 60), font=font_rank, anchor='mm')
    
    dose_lines = dose_str.split('\n')
    y_text = header_height + 55
    for l_idx, line in enumerate(dose_lines):
        color = status_rgb if l_idx == 0 else (180, 180, 180)
        draw.text((center_x, y_text + l_idx * 18), line, fill=color, font=font_dose, anchor='mm')

    well_img = carved_well_images[well_id].resize((well_size, well_size), Image.Resampling.LANCZOS)
    well_x = center_x - well_size // 2
    well_y = row1_y
    canvas.paste(well_img, (well_x, well_y), well_img)

    if idx == 0:
        draw.text((padding_x + 10, row1_y - 25), "WELLS (Carved & Highlighted)", fill=(255, 255, 255), font=font_label)

    bar_y1 = well_y + well_size + 15
    bar_y2 = bar_y1 + colorbar_height
    bar_w = 260
    bar_x1 = center_x - bar_w // 2
    bar_x2 = center_x + bar_w // 2

    draw.rounded_rectangle([(bar_x1, bar_y1), (bar_x2, bar_y2)], radius=8, fill=status_rgb, outline=(255, 255, 255), width=1)
    
    text_color = (0, 0, 0) if status == 'Sub-Healthy' else (255, 255, 255)
    draw.text((center_x, bar_y1 + colorbar_height // 2), status.upper(), fill=text_color, font=font_bar, anchor='mm')

    draw.line([(center_x, well_y + well_size + 2), (center_x, bar_y1 - 2)], fill=status_rgb, width=2)
    draw.line([(center_x, bar_y2 + 2), (center_x, row2_y - 8)], fill=status_rgb, width=2)
    draw.polygon([(center_x - 5, row2_y - 10), (center_x + 5, row2_y - 10), (center_x, row2_y - 3)], fill=status_rgb)

    chart_img = split_chart_images[well_id].resize((chart_disp_w, chart_disp_h), Image.Resampling.LANCZOS)
    chart_x = center_x - chart_disp_w // 2
    chart_y = row2_y
    canvas.paste(chart_img, (chart_x, chart_y))

    draw.rectangle([(chart_x, chart_y), (chart_x + chart_disp_w, chart_y + chart_disp_h)], outline=status_rgb, width=2)

    if idx == 0:
        draw.text((padding_x + 10, row2_y - 25), "GROWTH CHARTS (1-1 Aligned)", fill=(255, 255, 255), font=font_label)

# Save exact requested filename sorted_wells_and_chartsv2_v2_colorbars.png as well as sorted_wells_and_charts_row.png
out_path_v2 = os.path.join(ws, 'sorted_wells_and_chartsv2_v2_colorbars.png')
out_path_row = os.path.join(ws, 'sorted_wells_and_charts_row.png')

canvas.save(out_path_v2)
canvas.save(out_path_row)

print(f"Saved image to: {out_path_v2}")
