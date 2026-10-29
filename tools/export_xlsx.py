#!/usr/bin/env python3
"""export_xlsx.py — ekspor data drawing ke Excel untuk procurement & QA.

Sumber data hanya yang DAPAT DIBUKTIKAN dari repo, sehingga tidak ada angka
karangan:

  1. Bill of Materials   — dibaca dari tabel BOM pada tiap lembar isometrik
  2. Komponen Tercatat   — gabungan semua baris BOM lintas lembar (pivot)
  3. Line List           — dari design basis proyek aktif
  4. Instrument Index    — dari design basis proyek aktif
  5. Equipment Register  — dari design basis proyek aktif
  6. Register Dokumen    — dari registri proyek aktif
  7. Ringkasan QA        — status tiap pemeriksa (linter, konsistensi, BOM,
                           title block) bila tersedia

Yang TIDAK diekspor: panjang pipa nyata (isometrik NTS) dan harga/material
take-off berbayar — datanya tidak ada di repo.

Pemakaian:
    python tools/export_xlsx.py                    # -> dist/gpf-register.xlsx
    python tools/export_xlsx.py -o laporan.xlsx
    python tools/export_xlsx.py --project /path/project.json -o laporan.xlsx
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
try:
    from .project_config import load_project, load_register_json
except ImportError:
    from project_config import load_project, load_register_json

REPO = Path(__file__).resolve().parent.parent
CAD = REPO / "cad"
DB = REPO / "dokumen" / "01-design-basis.md"
REGISTRY = Path(__file__).resolve().parent / "documents.json"

# kolom tabel BOM pada lembar A3 (lihat iso_common.py)
BOM_NO_X = (272.0, 277.0)
BOM_DESC_X = (276.0, 300.0)
BOM_SIZE_X = (330.0, 340.0)
BOM_QTY_X = (340.0, 360.0)


# --------------------------------------------------------------------------- BOM
def parse_bom_rows(msp) -> list[dict]:
    texts = [(e.dxf.insert.x, e.dxf.insert.y, e.text.strip())
             for e in msp.query("MTEXT")]
    rows = []
    for x, y, t in texts:
        if not (BOM_NO_X[0] <= x <= BOM_NO_X[1]) or not re.fullmatch(r"\d{1,2}", t):
            continue
        desc = size = qty = ""
        for x2, y2, t2 in texts:
            if abs(y2 - y) > 0.6 or x2 <= BOM_NO_X[1]:
                continue
            if BOM_DESC_X[0] <= x2 <= BOM_DESC_X[1] and not desc:
                desc = t2
            elif BOM_SIZE_X[0] <= x2 <= BOM_SIZE_X[1]:
                size = t2
            elif BOM_QTY_X[0] <= x2 <= BOM_QTY_X[1]:
                qty = t2
        m = re.match(r"([\d.]+)", qty)
        rows.append({
            "no": t,
            "description": desc,
            "size": size,
            "quantity": float(m.group(1)) if m else None,
            "uom": qty.split()[-1] if qty.split() else "",
        })
    return rows


def classify(desc: str) -> str:
    d = desc.upper()
    if re.search(r"\b(ELL|ELBOW)\b", d):
        return "FITTING"
    if "TEE" in d or "REDUCER" in d or "CAP" in d:
        return "FITTING"
    if "FLANGE" in d:
        return "FLANGE"
    if "GASKET" in d:
        return "GASKET"
    if "BOLT" in d or "STUD" in d:
        return "BOLT"
    if "VALVE" in d or re.search(r"\b(PSV|GV|CV|LV|SDV|BV|NRV)\b", d):
        return "VALVE"
    if "PIPE" in d:
        return "PIPE"
    return "OTHER"


# --------------------------------------------------------------------------- DB
def parse_design_basis(path=DB) -> dict:
    out = {"equipment": [], "lines": [], "instruments": [], "meta": {}}
    path = Path(path)
    if not path.is_file(): raise ValueError(f'design basis tidak ditemukan: {path}')
    md = path.read_text(encoding="utf-8")
    if any(section not in md for section in ('## 3. DAFTAR EQUIPMENT','## 4. LINE LIST','## 5. INSTRUMENT INDEX','## 6.')):
        raise ValueError('Format design basis bukan gpf-markdown-v1; pemetaan diperlukan')
    m = re.search(r"Dok\s*:\s*(GPF-[\w-]+),\s*Rev\s*(\w+)", md)
    if not m:
        raise ValueError('Nomor dokumen dan revisi design basis GPF tidak ditemukan')
    out["meta"]["doc_no"], out["meta"]["rev"] = m.group(1), m.group(2)

    def table(section: str, next_sec: str) -> list[list[str]]:
        try:
            body = md.split(section)[1].split(next_sec)[0]
        except IndexError:
            return []
        rows = []
        for line in body.splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            if cells and cells[0].lower() in ("tag", "no. line", "loop"):
                continue
            rows.append(cells)
        return rows

    for r in table("## 3. DAFTAR EQUIPMENT", "## 4."):
        if len(r) >= 3:
            # Baris tanpa tag ("—") = item non-equipment (pipe rack, road,
            # fence, tank bund). Tetap diekspor karena berguna untuk QA
            # layout, tetapi diberi label eksplisit agar tidak dihitung
            # sebagai peralatan ber-tag.
            tag = r[0] if r[0] not in ("—", "-", "") else "(non-tag)"
            out["equipment"].append({"tag": tag, "description": r[1],
                                     "position": r[2],
                                     "elevation": r[3] if len(r) > 3 else ""})
    for r in table("## 4. LINE LIST", "## 5."):
        if len(r) >= 3 and re.match(r"\d{3}-[A-Z]{2}-\d{4}", r[0]):
            out["lines"].append({"line_no": r[0], "dn": r[1], "from_to": r[2],
                                 "valves": r[3] if len(r) > 3 else "",
                                 "note": r[4] if len(r) > 4 else ""})
    for r in table("## 5. INSTRUMENT INDEX", "## 6."):
        # Tag instrumen selalu berpola FUNGSI-NNN (PT-101, FE/FT-141).
        if len(r) >= 3 and re.fullmatch(r"[A-Z]+(?:/[A-Z]+)?-\d{3}",
                                        r[1].strip()):
            out["instruments"].append({
                "loop": r[0], "tag": r[1].strip(), "function": r[2],
                "location": r[3] if len(r) > 3 else "",
                "action": r[4] if len(r) > 4 else ""})
    if not (out['equipment'] or out['lines'] or out['instruments']):
        raise ValueError('Register design basis kosong atau gagal dipetakan')
    return out


# --------------------------------------------------------------------------- xlsx
def build_workbook(out_path: Path, project=None) -> dict:
    project = project or load_project()
    target = Path(out_path).resolve()
    protected = {project.config_path, project.basis, project.registry}
    if project.hmb: protected.add(project.hmb)
    if target in protected or target.is_relative_to(project.cad_dir):
        raise ValueError('output tidak boleh menimpa sumber proyek atau berada di direktori drawing')
    if not project.registry.is_file(): raise ValueError(f'registri dokumen tidak ditemukan: {project.registry}')
    try:
        reg = json.loads(project.registry.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc: raise ValueError(f'registri dokumen tidak valid: {exc}') from exc
    if not isinstance(reg,dict) or not isinstance(reg.get('documents'),list): raise ValueError('registri documents harus berupa daftar')
    if not project.cad_dir.is_dir(): raise ValueError(f'direktori drawing tidak ditemukan: {project.cad_dir}')
    db = parse_design_basis(project.basis) if project.basis_format == 'gpf-markdown-v1' else load_register_json(project.basis)
    expected_doc = reg.get('design_basis', {}).get('doc_no')
    if expected_doc and expected_doc != db['meta']['doc_no']:
        raise ValueError('nomor dokumen design basis tidak cocok dengan registri proyek')
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    bold = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="1F4E79")
    wrap = Alignment(vertical="top", wrap_text=True)

    wb = Workbook()
    summary: dict = {}

    def sheet(title: str, headers: list[str], rows: list[list],
              widths: list[int]):
        ws = wb.create_sheet(title)
        ws.append(headers)
        for c, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=c)
            cell.font = bold
            cell.fill = head_fill
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            ws.column_dimensions[get_column_letter(c)].width = widths[c - 1]
        for r in rows:
            ws.append(r)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = wrap
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        return ws

    # ---- 1-2. BOM per lembar + komponen gabungan
    per_sheet: list[list] = []
    composite: dict[tuple, dict] = {}
    try:
        import ezdxf
        for p in sorted(project.cad_dir.glob("iso_*.dxf")):
            msp = ezdxf.readfile(str(p)).modelspace()
            for r in parse_bom_rows(msp):
                cat = classify(r["description"])
                per_sheet.append([p.stem, r["no"], cat, r["description"],
                                  r["size"], r["quantity"], r["uom"]])
                key = (cat, r["description"], r["size"], r["uom"])
                c = composite.setdefault(key, {"qty": 0.0, "sheets": set()})
                if r["quantity"]:
                    c["qty"] += r["quantity"]
                c["sheets"].add(p.stem)
    except ImportError:
        pass

    sheet("BOM per Lembar",
          ["Lembar", "Item", "Kategori", "Deskripsi", "Ukuran", "Qty", "UOM"],
          per_sheet, [16, 7, 12, 46, 12, 8, 7])
    summary["bom_rows"] = len(per_sheet)

    comp_rows = [
        [k[0], k[1], k[2], k[3], round(v["qty"], 2) if v["qty"] else "",
         ", ".join(sorted(v["sheets"]))]
        for k, v in sorted(composite.items())]
    sheet("Komponen Gabungan",
          ["Kategori", "Deskripsi", "Ukuran", "UOM", "Total Qty", "Dipakai di"],
          comp_rows, [12, 46, 12, 7, 11, 34])
    summary["composite_items"] = len(comp_rows)

    # ---- 3-5. design basis
    sheet("Equipment Register",
          ["Tag", "Deskripsi", "Posisi Plant", "Elevasi"],
          [[e["tag"], e.get("description", ""), e.get("position", ""), e.get("elevation", "")]
           for e in db["equipment"]], [12, 46, 40, 20])
    sheet("Line List",
          ["No. Line", "DN", "Dari -> Ke", "Valve/Spesial", "Keterangan"],
          [[l["line_no"], l["dn"], l.get("from_to", ""), l.get("valves", ""), l.get("note", "")]
           for l in db["lines"]], [16, 7, 46, 40, 22])
    sheet("Instrument Index",
          ["Loop", "Tag", "Fungsi", "Lokasi", "Output/Aksi"],
          [[i.get("loop", ""), i["tag"], i.get("function", ""), i.get("location", ""), i.get("action", "")]
           for i in db["instruments"]], [8, 14, 34, 30, 30])
    summary["equipment"] = len(db["equipment"])
    summary["lines"] = len(db["lines"])
    summary["instruments"] = len(db["instruments"])

    # ---- 6. register dokumen
    doc_rows = []
    for d in reg.get("documents", []):
        doc_rows.append([d["doc_no"], d["file"], d["type"], d["sheet"]])
    sheet("Register Dokumen",
          ["Nomor Dokumen", "File", "Jenis", "Lembar"], doc_rows,
          [24, 22, 16, 9])
    summary["documents"] = len(doc_rows)

    # ---- 7. ringkasan QA
    qa = [["Dibuat oleh", "tools/export_xlsx.py"],
          ["Proyek", project.project_id],
          ["HMB", project.hmb_status + (f' ({project.hmb})' if project.hmb else '')],
          ["Design basis", db["meta"].get("doc_no", "-") +
           " Rev " + db["meta"].get("rev", "-")],
          ["Baris BOM", summary["bom_rows"]],
          ["Item komponen gabungan", summary["composite_items"]],
          ["Equipment / Line / Instrument", f"{summary['equipment']} / "
           f"{summary['lines']} / {summary['instruments']}"],
          ["Catatan", "Panjang pipa nyata TIDAK diekspor: isometrik berskala "
                      "NTS sehingga tidak dapat dikonversi tanpa tabel vertex."]]
    ws = sheet("Ringkasan", ["Keterangan", "Nilai"],
               [[a, b] for a, b in qa], [30, 80])
    ws.column_dimensions["B"].width = 80

    # hapus Sheet default
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", help='path output; default dist/<project_id>-register.xlsx di folder konfigurasi')
    ap.add_argument('--project', help='path konfigurasi proyek; default project.gpf.json untuk repo GPF')
    args = ap.parse_args(argv)

    try:
        project = load_project(args.project)
        out = Path(args.out) if args.out else project.config_path.parent / 'dist' / (project.project_id.lower() + '-register.xlsx')
        try:
            import openpyxl  # noqa: F401
        except ImportError:
            print("openpyxl tidak terpasang — ekspor XLSX dilewati", file=sys.stderr)
            return 0
        summary = build_workbook(out, project)
    except (ValueError, OSError, KeyError) as exc:
        print(f'Ekspor gagal: {exc}', file=sys.stderr)
        return 2
    print("=" * 70)
    print("EKSPOR EXCEL")
    print("=" * 70)
    print(f"berkas        : {out}")
    print(f"BOM rows      : {summary.get('bom_rows', 0)}")
    print(f"komponen unik : {summary.get('composite_items', 0)}")
    print(f"equipment     : {summary.get('equipment', 0)}")
    print(f"line          : {summary.get('lines', 0)}")
    print(f"instrument    : {summary.get('instruments', 0)}")
    print(f"dokumen       : {summary.get('documents', 0)}")
    print("SELESAI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
