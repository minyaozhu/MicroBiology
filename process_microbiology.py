import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ws = '/Users/minyaozhu/Desktop/MicroBiology'

carved_dir = os.path.join(ws, 'carved_wells')
split_multi_dir = os.path.join(ws, 'split_charts_multi')
split_single_dir = os.path.join(ws, 'split_charts_single')

os.makedirs(carved_dir, exist_ok=True)
os.makedirs(split_multi_dir, exist_ok=True)
os.makedirs(split_single_dir, exist_ok=True)

# 1. Load source images
wells_img = cv2.imread(os.path.join(ws, '12-wells.jpeg'))
charts_multi_img = cv2.imread(os.path.join(ws, '12-charts.jpeg'))
charts_single_img = cv2.imread(os.path.join(ws, '12-chart-single.png'))

# Centers and radius for wells (1024x650)
well_centers = {
    'A1': (190, 118), 'A2': (402, 118), 'A3': (614, 118), 'A4': (826, 118),
    'B1': (190, 332), 'B2': (402, 332), 'B3': (614, 332), 'B4': (826, 332),
    'C1': (190, 546), 'C2': (402, 546), 'C3': (614, 546), 'C4': (826, 546),
}
r_well = 102

# Multi-line chart grid dimensions (1024x462)
chart_w_multi = 1024 // 4
chart_h_multi = 462 // 3
chart_multi_coords = {
    'A1': (0, 0), 'A2': (1, 0), 'A3': (2, 0), 'A4': (3, 0),
    'B1': (0, 1), 'B2': (1, 1), 'B3': (2, 1), 'B4': (3, 1),
    'C1': (0, 2), 'C2': (1, 2), 'C3': (2, 2), 'C4': (3, 2),
}

# Single-line chart bounds in 12-chart-single.png (2498 x 1294)
col_bounds_single = [(90, 625), (700, 1235), (1300, 1835), (1900, 2435)]
row_bounds_single = [(0, 350), (400, 750), (800, 1150)]
chart_single_coords = {
    'A1': (0, 0), 'A2': (1, 0), 'A3': (2, 0), 'A4': (3, 0),
    'B4': (3, 1), 'B3': (2, 1), 'B2': (1, 1), 'B1': (0, 1),
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

carved_well_cyan = {}
carved_well_status = {}
split_multi_images = {}
split_single_images = {}

# Process each position
for idx, (well_id, dose_str, dose_val, status, color_hex, status_rgb) in enumerate(dose_data):
    cx, cy = well_centers[well_id]
    x1, y1 = cx - r_well - 5, cy - r_well - 5
    x2, y2 = cx + r_well + 5, cy + r_well + 5

    crop_w = wells_img[y1:y2, x1:x2].copy()
    h_c, w_c, _ = crop_w.shape
    mask = np.zeros((h_c, w_c), dtype=np.uint8)
    cv2.circle(mask, (w_c//2, h_c//2), r_well, 255, -1)

    # Cyan well (V1)
    hl_v1 = crop_w.copy()
    cv2.circle(hl_v1, (w_c//2, h_c//2), r_well, (0, 220, 255), 4)
    cv2.circle(hl_v1, (w_c//2, h_c//2), r_well + 2, (255, 255, 255), 2)
    b, g, r_ch = cv2.split(hl_v1)
    carved_well_cyan[well_id] = Image.fromarray(cv2.cvtColor(cv2.merge([b, g, r_ch, mask]), cv2.COLOR_BGRA2RGBA))

    # Status color well (V2)
    bgr_color = (status_rgb[2], status_rgb[1], status_rgb[0])
    hl_v2 = crop_w.copy()
    cv2.circle(hl_v2, (w_c//2, h_c//2), r_well, bgr_color, 4)
    cv2.circle(hl_v2, (w_c//2, h_c//2), r_well + 2, (255, 255, 255), 2)
    b, g, r_ch = cv2.split(hl_v2)
    rgba_v2 = cv2.merge([b, g, r_ch, mask])
    carved_well_status[well_id] = Image.fromarray(cv2.cvtColor(rgba_v2, cv2.COLOR_BGRA2RGBA))
    cv2.imwrite(os.path.join(carved_dir, f'well_{well_id}.png'), rgba_v2)

    # 1) Multi-line chart crop (from 12-charts.jpeg)
    col_m, row_m = chart_multi_coords[well_id]
    cmx1, cmy1 = col_m * chart_w_multi, row_m * chart_h_multi
    cmx2, cmy2 = cmx1 + chart_w_multi, cmy1 + chart_h_multi
    crop_multi = charts_multi_img[cmy1:cmy2, cmx1:cmx2].copy()
    cv2.rectangle(crop_multi, (0, 0), (chart_w_multi-1, chart_h_multi-1), bgr_color, 2)
    cv2.imwrite(os.path.join(split_multi_dir, f'chart_multi_{well_id}.png'), crop_multi)
    split_multi_images[well_id] = Image.fromarray(cv2.cvtColor(crop_multi, cv2.COLOR_BGR2RGB))

    # 2) Single-line chart crop (from 12-chart-single.png)
    col_s, row_s = chart_single_coords[well_id]
    csx1, csx2 = col_bounds_single[col_s]
    csy1, csy2 = row_bounds_single[row_s]
    crop_single = charts_single_img[csy1:csy2, csx1:csx2].copy()
    cv2.rectangle(crop_single, (0, 0), (crop_single.shape[1]-1, crop_single.shape[0]-1), bgr_color, 2)
    cv2.imwrite(os.path.join(split_single_dir, f'chart_single_{well_id}.png'), crop_single)
    split_single_images[well_id] = Image.fromarray(cv2.cvtColor(crop_single, cv2.COLOR_BGR2RGB))

# Common layout parameters
num_cols = 12
col_width = 300
well_size = 220
padding_x = 40
footer_height = 40

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

def render_composite(chart_dict, chart_w_orig, chart_h_orig, subtitle_tag, is_v2=True, cyan_wells=False):
    chart_disp_w = 280
    chart_disp_h = int(chart_disp_w * (chart_h_orig / chart_w_orig))

    header_h = 160 if is_v2 else 130
    col_hdr_h = 90
    r1_y = header_h + col_hdr_h + 20
    colorbar_h = 36
    gap = 75 if is_v2 else 60
    r2_y = r1_y + well_size + gap

    c_w = padding_x * 2 + num_cols * col_width
    c_h = r2_y + chart_disp_h + footer_height

    canvas = Image.new('RGB', (c_w, c_h), (18, 24, 38))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle([(0, 0), (c_w, header_h)], fill=(28, 36, 56))
    draw.text((padding_x, 22), f"Microbiology Antibiotic Dose Response Assay ({subtitle_tag})", fill=(255, 255, 255), font=font_title)
    draw.text((padding_x, 68), "12 Wells & 12 Aligned Growth Charts Sorted by Antibiotic Dose (High -> Low)", fill=(0, 210, 255), font=font_subtitle)

    if is_v2:
        leg_y = 110
        draw.rectangle([(padding_x, leg_y), (padding_x + 18, leg_y + 18)], fill=(16, 185, 129))
        draw.text((padding_x + 26, leg_y), "Healthy (#1 - #4)", fill=(255, 255, 255), font=font_legend)
        draw.rectangle([(padding_x + 220, leg_y), (padding_x + 238, leg_y + 18)], fill=(245, 158, 11))
        draw.text((padding_x + 246, leg_y), "Sub-healthy (#5)", fill=(255, 255, 255), font=font_legend)
        draw.rectangle([(padding_x + 440, leg_y), (padding_x + 458, leg_y + 18)], fill=(239, 68, 68))
        draw.text((padding_x + 466, leg_y), "Infection (#6 - #12)", fill=(255, 255, 255), font=font_legend)

    for idx, (well_id, dose_str, dose_val, status, color_hex, status_rgb) in enumerate(dose_data):
        col_x = padding_x + idx * col_width
        center_x = col_x + col_width // 2

        card_color = (25, 34, 52) if idx % 2 == 0 else (21, 29, 45)
        draw.rectangle([(col_x + 5, header_h + 10), (col_x + col_width - 5, c_h - 20)], fill=card_color, outline=(40, 52, 78), width=1)
        draw.text((center_x, header_h + 25), f"#{idx+1}  [{well_id}]", fill=(255, 205, 60), font=font_rank, anchor='mm')

        dose_lines = dose_str.split('\n')
        y_text = header_h + 55
        for l_idx, line in enumerate(dose_lines):
            color = status_rgb if (is_v2 and l_idx == 0) else ((100, 255, 180) if l_idx == 0 else (180, 180, 180))
            draw.text((center_x, y_text + l_idx * 18), line, fill=color, font=font_dose, anchor='mm')

        w_dict = carved_well_cyan if cyan_wells else carved_well_status
        w_img = w_dict[well_id].resize((well_size, well_size), Image.Resampling.LANCZOS)
        well_x = center_x - well_size // 2
        well_y = r1_y
        canvas.paste(w_img, (well_x, well_y), w_img)

        if idx == 0:
            draw.text((padding_x + 10, r1_y - 25), "WELLS (Carved & Highlighted)", fill=(255, 255, 255), font=font_label)

        if is_v2:
            bar_y1 = well_y + well_size + 15
            bar_y2 = bar_y1 + colorbar_h
            bar_w = 260
            bar_x1 = center_x - bar_w // 2
            bar_x2 = center_x + bar_w // 2
            draw.rounded_rectangle([(bar_x1, bar_y1), (bar_x2, bar_y2)], radius=8, fill=status_rgb, outline=(255, 255, 255), width=1)
            t_col = (0, 0, 0) if status == 'Sub-Healthy' else (255, 255, 255)
            draw.text((center_x, bar_y1 + colorbar_h // 2), status.upper(), fill=t_col, font=font_bar, anchor='mm')

            draw.line([(center_x, well_y + well_size + 2), (center_x, bar_y1 - 2)], fill=status_rgb, width=2)
            draw.line([(center_x, bar_y2 + 2), (center_x, r2_y - 8)], fill=status_rgb, width=2)
            draw.polygon([(center_x - 5, r2_y - 10), (center_x + 5, r2_y - 10), (center_x, r2_y - 3)], fill=status_rgb)
        else:
            line_x = center_x
            draw.line([(line_x, well_y + well_size + 8), (line_x, r2_y - 12)], fill=(0, 180, 230), width=2)
            draw.polygon([(line_x - 5, r2_y - 14), (line_x + 5, r2_y - 14), (line_x, r2_y - 6)], fill=(0, 180, 230))

        ch_img = chart_dict[well_id].resize((chart_disp_w, chart_disp_h), Image.Resampling.LANCZOS)
        chart_x = center_x - chart_disp_w // 2
        chart_y = r2_y
        canvas.paste(ch_img, (chart_x, chart_y))

        outline_c = status_rgb if is_v2 else (60, 80, 120)
        draw.rectangle([(chart_x, chart_y), (chart_x + chart_disp_w, chart_y + chart_disp_h)], outline=outline_c, width=2 if is_v2 else 1)

        if idx == 0:
            draw.text((padding_x + 10, r2_y - 25), "GROWTH CHARTS (1-1 Aligned)", fill=(255, 255, 255), font=font_label)

    return canvas

# Generate and save ALL versions:
# 1) Multi-line chart version (v1 & v2)
c_multi_v1 = render_composite(split_multi_images, 256, 154, "Multi-Line Charts - Standard", is_v2=False, cyan_wells=True)
path_multi_v1 = os.path.join(ws, 'sorted_wells_and_multicharts_v1_clean.png')
c_multi_v1.save(path_multi_v1)

c_multi_v2 = render_composite(split_multi_images, 256, 154, "Multi-Line Charts - Health Status", is_v2=True, cyan_wells=False)
path_multi_v2 = os.path.join(ws, 'sorted_wells_and_multicharts_v2_colorbars.png')
c_multi_v2.save(path_multi_v2)

# 2) Single-line chart version (v1 & v2)
c_single_v1 = render_composite(split_single_images, 535, 350, "Single-Line Chart - Standard", is_v2=False, cyan_wells=True)
path_single_v1 = os.path.join(ws, 'sorted_wells_and_singlechart_v1_clean.png')
c_single_v1.save(path_single_v1)

c_single_v2 = render_composite(split_single_images, 535, 350, "Single-Line Chart - Health Status", is_v2=True, cyan_wells=False)
path_single_v2 = os.path.join(ws, 'sorted_wells_and_singlechart_v2_colorbars.png')
c_single_v2.save(path_single_v2)

# Save default main composite aliases
c_single_v2.save(os.path.join(ws, 'sorted_wells_and_charts_row.png'))
c_single_v2.save(os.path.join(ws, 'sorted_wells_and_charts_v2_colorbars.png'))
c_single_v1.save(os.path.join(ws, 'sorted_wells_and_charts_v1_original.png'))

print("Generated all versions without overwriting any previous assets:")
print(f" - {path_multi_v1}")
print(f" - {path_multi_v2}")
print(f" - {path_single_v1}")
print(f" - {path_single_v2}")
