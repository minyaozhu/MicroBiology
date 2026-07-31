# Microplate Well Extraction & Growth Curve Dose-Response Alignment

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?style=flat&logo=opencv&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-PIL-000000?style=flat)

An automated image processing and analysis pipeline for microbiology dose-response assays. 

This repository processes 12-well microplate photos (`12-wells.jpeg`), splits multi-panel growth curves (`12-charts.jpeg`), correlates them 1-to-1 with experimental layout concentration annotations (`12-layout.png`), and outputs a high-to-low antibiotic concentration sorted visualization.

---

## 📸 Output Preview

![Microbiology Dose-Response Row Composite](sorted_wells_and_charts_row.png)

---

## ✨ Key Features

1. **Well Extraction & Highlighting**:
   - Automatically detects and crops all 12 microplate wells.
   - Applies transparent RGBA masking and adds a sleek cyan accent ring around each well.
2. **Growth Curve Splitting**:
   - Crops each individual growth plot from the 3x4 panel grid.
3. **Antibiotic Dose Sorting (High → Low)**:
   - Maps each position (A1..C4) to its corresponding antibiotic concentration (50 µg/mL down to 0 µg/mL).
   - Rearranges all 12 wells and charts into a single high-to-low concentration row layout.
4. **1-to-1 Vertical Alignment**:
   - Positions each growth curve chart directly beneath its corresponding microplate well for intuitive visual comparison.

---

## 📊 Concentration Mapping

| Rank | Well ID | Antibiotic Concentration | Notes |
| :---: | :---: | :---: | :--- |
| **#1** | **A1** | 50 µg/mL | No Bacteria (Control) |
| **#2** | **A2** | 25 µg/mL | High Dose |
| **#3** | **A3** | 12.5 µg/mL | High Dose |
| **#4** | **A4** | 6.25 µg/mL | Medium-High Dose |
| **#5** | **B4** | 3.13 µg/mL | Medium Dose |
| **#6** | **B3** | 1.56 µg/mL | Medium Dose |
| **#7** | **B2** | 0.78 µg/mL | Low-Medium Dose |
| **#8** | **B1** | 0.39 µg/mL | Low Dose |
| **#9** | **C1** | 0.195 µg/mL | Very Low Dose |
| **#10** | **C2** | 0.098 µg/mL | Lowest Dose |
| **#11** | **C3** | 0.098 µg/mL | Lowest Dose |
| **#12** | **C4** | No antibiotic (0 µg/mL) | Bacterial Growth Control |

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
└── sorted_wells_and_charts_row.png # Final aligned row composite image
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
