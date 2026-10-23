"""PIPELINE ALIGNMENT SHEET — GPF-00-PI-PLN-0019 Rev A0 (DEMO).

Sheet A1 841x594 split-window sesuai Bagian VI doc GPF-00-PM-PLN-0008:
  - Panel atas 40%: PLAN VIEW (sumbu pipa per stasiun KP, ROW 50 m,
    cold/hot bend, penyeberangan jalan & sungai, north arrow).
  - Panel tengah 30%: PROFILE VIEW (V 1:250 berlebih, kontur NGL, BOP,
    depth of cover, HDD vs open cut).
  - Panel bawah 30%: DATA BANDS per stasiun KP (8 band standar).

Demo menulis data survei sintetis (20 stasiun KP 0+000 s/d 1+900, 2-3
belokan, satu penyeberangan jalan + satu sungai HDD) ke
cad/alignment_demo_survey.csv, lalu merender sheet lengkap dari CSV
tersebut via alignment_sheet_builder.parse_survey_csv.

Teks = MTEXT Arial via manifest TEXTS + cad/apply_text.py (Company
Standard) — DILARANG outline bd.Text / entity TEXT.

Rantai build (dari root proyek):
  uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 \
      python cad/alignment_demo.py --force
  uvx ... python cad/apply_text.py cad/alignment_demo.dxf cad/alignment_demo.texts.json
  uvx ... python cad/validate_cad_rules.py cad/alignment_demo.dxf cad/alignment_demo.texts.json
  uvx ... cadgen dxf snapshot cad/alignment_demo.dxf cad/alignment_demo.png \
      --width 2400 --height 1700
"""

from __future__ import annotations

import csv
from pathlib import Path

from cadgen import dxf

from alignment_sheet_builder import (
    AlignmentSheetContext,
    derive_features,
    parse_survey_csv,
)

_HERE = Path(__file__).resolve().parent
CSV_PATH = _HERE / "alignment_demo_survey.csv"
JSON_PATH = _HERE / "alignment_demo.texts.json"

_SURVEY_HEADER = [
    "KP", "Northing", "Easting", "Elevasi", "Depth_of_Cover", "Wall_Thk",
    "Grade", "Class_Location", "Coating", "Soil", "Feature",
]

# Data survei sintetis: 20 stasiun KP 0+000 s/d 1+900 (pitch 100 m).
# Rute umum ke Timur dengan 3 belokan (cold/hot/cold), penyeberangan
# sungai HDD (KP 0+700) dan jalan open cut (KP 1+100).
_SURVEY_ROWS = [
    # KP,     Northing, Easting, Elevasi, DOC,  WT,   Grade, Class,  Coating,   Soil, Feature
    ("0+000", 1000.0, 0.0, 106.2, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "CL", ""),
    ("0+100", 1000.0, 100.0, 107.1, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "CL", ""),
    ("0+200", 1000.0, 200.0, 108.4, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "CL", ""),
    ("0+300", 1000.0, 300.0, 107.6, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "SC", ""),
    ("0+400", 1000.0, 400.0, 108.9, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "SC", "BEND;COLD;12;R"),
    ("0+500", 1021.3, 500.0, 109.5, 1.20, 9.5, "X52", "CL2", "3LPE", "SM", ""),
    ("0+600", 1042.5, 600.0, 104.8, 6.00, 11.0, "X52", "CL2", "3LPE+CONC", "SM", ""),
    ("0+700", 1063.8, 700.0, 101.2, 8.50, 11.0, "X52", "CL2", "3LPE+CONC", "SM", "RIVER;SUNGAI CEMARA;HDD;30"),
    ("0+800", 1085.1, 800.0, 103.5, 5.00, 11.0, "X52", "CL2", "3LPE+CONC", "SM", ""),
    ("0+900", 1106.3, 900.0, 108.1, 1.20, 9.5, "X52", "CL2", "3LPE", "SC", "BEND;HOT;28;L"),
    ("1+000", 1077.6, 1000.0, 109.4, 1.50, 9.5, "X52", "CL2", "3LPE+C", "SC", ""),
    ("1+100", 1049.0, 1100.0, 110.2, 1.50, 9.5, "X52", "CL2", "3LPE+C", "CL", "ROAD;ASPHALT ROAD 8 m;OPEN CUT;8"),
    ("1+200", 1020.3, 1200.0, 111.8, 1.50, 9.5, "X52", "CL2", "3LPE+C", "CL", ""),
    ("1+300", 991.7, 1300.0, 112.5, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "CL", ""),
    ("1+400", 963.0, 1400.0, 111.0, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "ML", ""),
    ("1+500", 934.3, 1500.0, 113.6, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "CL", "BEND;COLD;10;R"),
    ("1+600", 923.8, 1600.0, 114.2, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "CL", ""),
    ("1+700", 913.3, 1700.0, 113.1, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "SC", ""),
    ("1+800", 902.8, 1800.0, 112.4, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "SC", ""),
    ("1+900", 892.3, 1900.0, 111.8, 1.20, 9.5, "X52", "CL1-D2", "3LPE", "SM", ""),
]

_NOTES = [
    "1. ALIGNMENT COMPILED FROM TOPOGRAPHIC SURVEY FILE cad/alignment_demo_survey.csv.",
    "2. DATUM: WGS84 UTM ZONE 48S. ELEVATIONS IN m ABOVE MEAN SEA LEVEL.",
    "3. SCALES: HORIZONTAL 1:4000, VERTICAL 1:250 (VEX 16:1) AT A1.",
    "4. PLAN VIEW PLOTTED ALONG CHAINAGE (SCHEMATIC); NORTH AS PER ARROW.",
    "5. PIPE: API 5L X52, OD 20 IN (508 mm), WT PER BAND. JOINT COATING 3LPE.",
    "6. MIN DEPTH OF COVER 1.2 m PER ASME B31.8-2022; 1.5 m AT ROAD CROSSING.",
    "7. RIVER CROSSING KP 0+600 - 0+800 BY HDD; CONCRETE WEIGHT COATING THERE.",
    "8. CLASS LOCATION PER ASME B31.8-2022 POPULATION DENSITY SURVEY (DEMO).",
    "9. SOIL CLASSIFICATION PER USCS. GEOTECHNICAL SURVEY BY OTHERS.",
    "10. SYNTHETIC DEMONSTRATION DATA - NOT FOR CONSTRUCTION.",
]

_REF_DOCS = [
    "GPF-00-DB-0001 - DESIGN BASIS",
    "GPF-00-PM-PLN-0008 - ROADMAP BAGIAN VI",
    "ASME B31.8-2022 - GAS TRANSMISSION",
]


def write_survey_csv(path: Path = CSV_PATH) -> Path:
    """Tulis data survei sintetis ke CSV (sumber kebenaran render demo)."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(_SURVEY_HEADER)
        for row in _SURVEY_ROWS:
            w.writerow(row)
    return path


def build_sheet_context() -> AlignmentSheetContext:
    """Parser CSV survei -> context sheet lengkap (semua panel tergambar)."""
    stations = parse_survey_csv(CSV_PATH)
    bends, crossings = derive_features(stations)
    ctx = AlignmentSheetContext(
        stations,
        bends,
        crossings,
        plan_n_ref=1000.0,
        doc_no="GPF-00-PI-PLN-0019",
        title_main="PIPELINE ALIGNMENT SHEET",
        rev="A0",
        rev_desc="ISSUED FOR REVIEW",
        date_str="23 OCT 2026",
    )
    ctx.setup_frame()
    ctx.setup_title_block()
    ctx.setup_reference_docs(_REF_DOCS)
    ctx.draw_plan_view(
        row_width_m=25.0,
        from_label=("FROM METERING STATION", "GAS TRANSMISSION 20 IN"),
        to_label=("TO SALES GAS DELIVERY PT", "GAS TRANSMISSION 20 IN"),
        route_label="GPF-00-PI-PLN-0019 - GAS TRANSMISSION PIPELINE 20 IN (DN500)",
    )
    ctx.draw_plan_legend()
    ctx.draw_profile_view()
    ctx.draw_profile_notes(_NOTES)
    ctx.draw_data_bands()
    return ctx


@dxf
def alignment_demo():
    """cadgen model: render alignment sheet penuh dari CSV survei."""
    write_survey_csv()
    ctx = build_sheet_context()
    return ctx.export_manifest(JSON_PATH)


if __name__ == "__main__":
    alignment_demo()  # build: the daemon worker runs the body in ITS process
    # harvest the manifest in THIS process: re-run the raw body (pure side
    # effect, writes nothing) so module-level state is populated here
    alignment_demo.__cadgen_model__.func()
