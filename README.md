# Microplate Well Extraction & Growth Curve Dose-Response Alignment

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?style=flat&logo=opencv&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-PIL-000000?style=flat)

An automated image processing and analysis pipeline for microbiology dose-response assays with health transition state classification.

This repository processes 12-well microplate photos (`12-wells.jpeg`), splits multi-panel growth curves (`12-charts.jpeg`), correlates them 1-to-1 with experimental layout concentration annotations (`12-layout.png`), and outputs a high-to-low antibiotic concentration sorted visualization featuring in-between health transition color bars.

---

## 💬 Original Prompt

> "I have 3 pictures (12 wells , 12 charts, 12 layout). 1. For the 12 wells, please highlight each well and carve out as an image (totally 12).  2. For the 12 charts, split into 12 individual charts. 3. Now create a new image, line the 12 carved-out wells in a row, and line the 12 charts in a row, below the wells (1 chart aligns with 1 well).   Keep in mind, the locations of wells and charts in original pictures have 1-1 mapping, and when making them in a row, I want to sort (high => low) by the antibiotic doses info in the 12-layout picture."
>
> **Enhancement Prompt**:
> "Great! I want to enhance the final image to indicate the transition from healthy (#1 ~ #4, with green color), sub-healthy (#5, yellow color), infection (the rest, red color). insert a color-bar in-between each well-image and chart-image"

---

## 📸 Output Preview

![Microbiology Dose-Response Row Composite](sorted_wells_and_charts_row.png)

---

## ✨ Key Features

1. **In-Between Health Status Color-Bars**:
   - Inserts color-coded status indicator bars directly between each carved well image and its aligned growth chart.
   - 🟩 **Healthy** (#1–#4): Green (`#10B981`)
   - 🟨 **Sub-Healthy** (#5): Yellow (`#F59E0B`)
   - 🟥 **Infection** (#6–#12): Red (`#EF4444`)
2. **Well Extraction & Highlighting**:
   - Automatically detects and crops all 12 microplate wells.
   - Applies transparent RGBA masking and adds accent ring highlights around each well matching its health state color.
3. **Growth Curve Splitting**:
   - Crops each individual growth plot from the 3x4 panel grid with matching status borders.
4. **Antibiotic Dose Sorting (High → Low)**:
   - Maps each position (A1..C4) to its corresponding antibiotic concentration (50 µg/mL down to 0 µg/mL).
   - Rearranges all 12 wells and charts into a single high-to-low concentration row layout.
5. **1-to-1 Vertical Alignment**:
   - Positions each growth curve chart directly beneath its corresponding microplate well for intuitive visual comparison.

---

## 📊 Health Transition & Concentration Mapping

| Rank | Well ID | Antibiotic Concentration | Health Status | Color Code | Notes |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **A1** | 50 µg/mL | **Healthy** | 🟢 Green | No Bacteria (Control) |
| **#2** | **A2** | 25 µg/mL | **Healthy** | 🟢 Green | High Dose |
| **#3** | **A3** | 12.5 µg/mL | **Healthy** | 🟢 Green | High Dose |
| **#4** | **A4** | 6.25 µg/mL | **Healthy** | 🟢 Green | Medium-High Dose |
| **#5** | **B4** | 3.13 µg/mL | **Sub-Healthy** | 🟡 Yellow | Transition Zone |
| **#6** | **B3** | 1.56 µg/mL | **Infection** | 🔴 Red | Bacterial Growth |
| **#7** | **B2** | 0.78 µg/mL | **Infection** | 🔴 Red | Bacterial Growth |
| **#8** | **B1** | 0.39 µg/mL | **Infection** | 🔴 Red | Bacterial Growth |
| **#9** | **C1** | 0.195 µg/mL | **Infection** | 🔴 Red | Bacterial Growth |
| **#10** | **C2** | 0.098 µg/mL | **Infection** | 🔴 Red | Bacterial Growth |
| **#11** | **C3** | 0.098 µg/mL | **Infection** | 🔴 Red | Bacterial Growth |
| **#12** | **C4** | No antibiotic (0 µg/mL) | **Infection** | 🔴 Red | Growth Control |

---

## 📁 Repository Structure

```
MicroBiology/
├── process_microbiology.py      # Main image processing & composite generation script
├── 12-wells.jpeg                # Original 12-well plate image
├── 12-charts.jpeg               # Original 12-panel growth curve plots
├── 12-layout.png                # Original 12-well layout diagram
├── carved_wells/                # 12 individual cropped and highlighted well images
│   ├── rank_01_well_A1.png
│   └── ...
├── split_charts/                # 12 individual cropped growth curve images
│   ├── rank_01_chart_A1.png
│   └── ...
└── sorted_wells_and_charts_row.png # Final aligned row composite image with health color bars
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install opencv-python pillow numpy
```

### 2. Run Processing Pipeline
```bash
python process_microbiology.py
```

All extracted images will be generated in `carved_wells/`, `split_charts/`, and the combined composite image will be saved as `sorted_wells_and_charts_row.png`.
