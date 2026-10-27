#!/usr/bin/env python3
"""titleblock_check.py — verifikasi field title block per ISO 7200:2004.

ISO 7200:2004 membedakan dua kelompok data:

  A. Data area (WAJIB / direkomendasikan)
     - Legal owner              (pemilik/ perusahaan)
     - Identification number    (nomor dokumen)
     - Date of issue
     - Revision index
     - Sheet number             (bila lebih dari satu lembar)
     - Title / subject          (direkomendasikan)

  B. Data area administratif (WAJIB menurut ISO 7200 §4.2)
     - Responsible department
     - Technical reference (dokumen acuan)
     - Approval (dibuat/diperiksa/disetujui)
     - Status (issue for review / construction / ...)
     - Sheet size

Aturan proyek ini (dokumen/01-design-basis.md §6a) menambahkan:
     - Project name
     - Scale

Pemetaan dilakukan pada manifest teks (`cad/*.texts.json`), karena semua
teks di repo ini adalah MTEXT yang ditulis dari manifest.

Pemakaian:
    python tools/titleblock_check.py
    python tools/titleblock_check.py --json
    python tools/titleblock_check.py --strict
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAD = REPO / "cad"
REGISTRY = Path(__file__).resolve().parent / "documents.json"

# --- aturan field -----------------------------------------------------------
# level: "ERROR" = wajib; "WARN" = direkomendasikan/diproyeksikan
FIELDS = {
    "legal_owner": {
        "level": "ERROR",
        "iso": "ISO 7200 §4.1 (legal owner)",
        "patterns": [r"PT\s+[A-Z]", r"\bCOMPANY\b", r"\bCONSULTANT\b",
                     r"\bOWNER\b", r"REKA"],
    },
    "identification_number": {
        "level": "ERROR",
        "iso": "ISO 7200 §4.1 (identification number)",
        "patterns": [r"GPF-\d{2}-[A-Z]{2}-[A-Z]{3}-\d{4}"],
    },
    "date_of_issue": {
        "level": "ERROR",
        "iso": "ISO 7200 §4.1 (date of issue)",
        # Bentuk sah di repo: "26 OCT 2026", "09 OCT 26" (2 digit tahun),
        # "12 OCT 2026", atau numerik "26/10/2026".
        "patterns": [
            r"\b\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{2,4}\b",
            r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b",
        ],
    },
    "revision_index": {
        "level": "ERROR",
        "iso": "ISO 7200 §4.1 (revision index)",
        # sel revisi berdiri sendiri (A0..Z9) ATAU deklarasi "REV: A3"
        "patterns": [r"^[A-Z]\d$", r"^REV\s*:?\s*[A-Z]\d"],
    },
    "sheet_number": {
        "level": "ERROR",
        "iso": "ISO 7200 §4.1 (sheet number)",
        # Di repo ini label dan nilai sering DIPISAH menjadi dua MTEXT:
        #   "SHEET:"  +  "1 OF 1"      (atau "SHEET: 1 OF 1" satu teks)
        "patterns": [r"SHEET\s*:?\s*\d+\s*(OF|/)\s*\d+",
                     r"SHT\s*:?\s*\d+\s*(OF|/)\s*\d+",
                     r"^\d+\s*(OF|/)\s*\d+$",      # nilai terpisah dari label
                     r"^SHEET\s*:?$"],            # label terpisah dari nilai
    },
    "title": {
        "level": "ERROR",
        "iso": "ISO 7200 §4.1 (title)",
        # judul: teks kapital panjang di area title block, atau kata kunci jenis
        "patterns": [r"\bP&?ID\b", r"PIPING PLAN", r"ISOMETRIC",
                     r"SEPARATOR", r"ALIGNMENT", r"WELLHEAD", r"COMPRESS",
                     r"METERING", r"BLOCK VALVE", r"SUPPORT"],
    },
    "responsible_dept": {
        "level": "WARN",
        "iso": "ISO 7200 §4.2 (responsible department)",
        "patterns": [r"\bDEPT\b", r"DEPARTMENT", r"DISCIPLINE",
                     r"\bENGINEERING\b"],
    },
    "approval": {
        "level": "WARN",
        "iso": "ISO 7200 §4.2 (approval)",
        "patterns": [r"\bAPPROV", r"\bCHECK\b", r"\bCHK\b", r"\bDRAWN\b"],
    },
    "status": {
        "level": "WARN",
        "iso": "ISO 7200 §4.2 (status)",
        "patterns": [r"ISSUED FOR", r"\bIFR\b", r"\bIFC\b", r"\bIFA\b",
                     r"FOR REVIEW", r"FOR CONSTRUCTION"],
    },
    "sheet_size": {
        "level": "ERROR",
        "iso": "ISO 7200 §4.2 / ISO 5457 (sheet size)",
        "patterns": [r"^\s*A[0-4]\s*$", r"\bA[0-4]\b\s*(SHEET|SIZE)"],
    },
    "scale": {
        "level": "WARN",
        "iso": "design basis §6a (scale)",
        "patterns": [r"\bSCALE\s*:?\s*(1:\d+|NTS)"],
    },
}

# Field yang memang belum diwajibkan proyek ini (dicatat, tidak diperiksa)
NOT_REQUIRED = {
    "language": "ISO 7200 tidak mewajibkan field bahasa",
    "technical_reference": "acuan tercantum di blok REFERENCE DOCUMENT "
                           "(bukan title block utama)",
}


@dataclass
class Finding:
    level: str
    sheet: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    sheets: dict = field(default_factory=dict)

    def err(self, sheet, msg):
        self.findings.append(Finding("ERROR", sheet, msg))

    def warn(self, sheet, msg):
        self.findings.append(Finding("WARN", sheet, msg))

    @property
    def errors(self):
        return [f for f in self.findings if f.level == "ERROR"]


def load_texts(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    texts = data["texts"] if isinstance(data, dict) else data
    out = []
    for t in texts:
        s = t.get("t") if isinstance(t, dict) else t
        if isinstance(s, str):
            out.append(s.strip())
    return out


def field_present(texts: list[str], patterns: list[str]) -> int:
    n = 0
    for t in texts:
        if any(re.search(p, t, re.I) for p in patterns):
            n += 1
    return n


def check_title_block(name: str, texts: list[str], rep: Report) -> dict:
    info = {"sheet": name, "texts": len(texts), "present": {}, "missing": []}
    for key, spec in FIELDS.items():
        n = field_present(texts, spec["patterns"])
        info["present"][key] = n
        if n == 0:
            info["missing"].append(key)
            msg = f"field '{key}' tidak ditemukan — {spec['iso']}"
            (rep.err if spec["level"] == "ERROR" else rep.warn)(name, msg)
    return info


# Ukuran lembar ISO 5457 (mm) -> nama
SHEET_SIZES = {"A0": (1189, 841), "A1": (841, 594), "A2": (594, 420),
               "A3": (420, 297), "A4": (297, 210)}
# Toleransi selisih total (lebar+tinggi) antara extents border dan ukuran
# kertas. Lihat penjelasan pada detect_sheet_size_from_dxf.
SHEET_SIZE_TOL_MM = 45.0


def _entity_points(e) -> list:
    """Titik pembentuk entity DXF (tanpa bergantung pada API bbox)."""
    t = e.dxftype()
    try:
        if t == "LINE":
            return [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        if t == "LWPOLYLINE":
            return [(p[0], p[1]) for p in e.get_points("xy")]
        if t == "POLYLINE":
            return [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
        if t in ("CIRCLE", "ARC"):
            c, r = e.dxf.center, e.dxf.radius
            return [(c.x - r, c.y - r), (c.x + r, c.y + r)]
        if t == "SOLID":
            return [(v.x, v.y) for v in (e.dxf.vtx0, e.dxf.vtx1, e.dxf.vtx2)]
        if t in ("TEXT", "MTEXT"):
            ip = e.dxf.insert
            return [(ip.x, ip.y)]
    except Exception:
        return []
    return []


def detect_sheet_size_from_dxf(stem: str) -> "str | None":
    """Tentukan ukuran lembar dari GEOMETRI border (sumber kebenaran).

    Token "A1" pada teks ambigu: di repo ini "A0"/"A1" juga dipakai sebagai
    SEL REVISI, sehingga ukuran lembar tidak dapat disimpulkan dari teks.
    Border ISO 5457 digambar sesuai ukuran kertas, jadi extents layer
    REF-FRAME adalah bukti yang dapat dipercaya.

    Catatan: `ezdxf` tidak menyediakan `Entity.bbox()` secara default.
    Extents dihitung manual dari titik entity.
    """
    p = CAD / f"{stem}.dxf"
    if not p.is_file():
        return None
    try:
        import ezdxf
        msp = ezdxf.readfile(str(p)).modelspace()
        xs, ys = [], []
        for e in msp.query('*[layer=="REF-FRAME"]'):
            for x, y in _entity_points(e):
                xs.append(x)
                ys.append(y)
        if not xs:
            return None
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        # Border digambar di DALAM tepi kertas (ISO 5457), sehingga extents
        # border selalu lebih kecil dari ukuran kertas. Hasil terukur:
        #   A1 -> 821,0 x 580,0  (841-20, 594-14)   selisih total 34,0
        #   A3 -> 416,0 x 294,4  (420-4,  297-2,6)  selisih total  6,6
        # Toleransi 45 mm memisahkan A1 (34) dari A2 (selisih ~200 mm),
        # cukup longgar untuk border, cukup ketat untuk menolak tebakan.
        best, bestd = None, 1e9
        for k, (bw, bh) in SHEET_SIZES.items():
            d = min(abs(bw - w) + abs(bh - h),      # orientasi sama
                    abs(bh - w) + abs(bw - h))      # orientasi diputar
            if d < bestd:
                best, bestd = k, d
        return best if bestd <= SHEET_SIZE_TOL_MM else None
    except Exception:
        return None


def check_registry_consistency(manifests: dict, rep: Report) -> None:
    """Ukuran lembar (dari geometri) harus sesuai registri."""
    if not REGISTRY.is_file():
        return
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for d in reg.get("documents", []):
        f, size = d["file"], d.get("sheet", "")
        if not size or f not in manifests:
            continue
        actual = detect_sheet_size_from_dxf(f)
        if actual is None:
            rep.warn(f, "ukuran lembar tidak dapat ditentukan dari geometri "
                        "(border REF-FRAME tidak terbaca)")
            continue
        if actual != size:
            rep.err(f, f"ukuran lembar {actual} (geometri) != {size} "
                       f"(registri)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="warning = gagal")
    args = ap.parse_args(argv)

    rep = Report()
    manifests: dict[str, list[str]] = {}
    for p in sorted(CAD.glob("*.texts.json")):
        if p.name.startswith(("test_", "test_opt")):
            continue
        try:
            manifests[p.name.replace(".texts.json", "")] = load_texts(p)
        except Exception as exc:
            rep.err(p.stem, f"manifest tidak terbaca: {exc}")

    if not manifests:
        rep.err("titleblock", f"tidak ada manifest di {CAD}")

    for name, texts in manifests.items():
        rep.sheets[name] = check_title_block(name, texts, rep)

    check_registry_consistency(manifests, rep)

    failed = bool(rep.errors) or (args.strict and
                                  any(f.level == "WARN" for f in rep.findings))
    if args.json:
        print(json.dumps({
            "ok": not failed,
            "sheets": rep.sheets,
            "findings": [f.__dict__ for f in rep.findings],
            "not_required": NOT_REQUIRED,
        }, indent=2, ensure_ascii=False))
    else:
        print("=" * 78)
        print("TITLE BLOCK — ISO 7200:2004")
        print("=" * 78)
        req = [k for k, v in FIELDS.items() if v["level"] == "ERROR"]
        rec = [k for k, v in FIELDS.items() if v["level"] == "WARN"]
        print(f"field wajib ({len(req)})  : {', '.join(req)}")
        print(f"field dianjurkan ({len(rec)}): {', '.join(rec)}")
        print(f"lembar diperiksa: {len(manifests)}")
        print("-" * 78)
        for f in rep.findings:
            print(f"[{f.level:<5}] {f.sheet:<20} {f.message}")
        if not rep.findings:
            print("semua field wajib & dianjurkan terpenuhi")
        print("-" * 78)
        nw = sum(1 for f in rep.findings if f.level == "WARN")
        print(f"HASIL: {len(rep.errors)} error, {nw} warning")
        print("LENGKAP" if not failed else "BELUM LENGKAP")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
