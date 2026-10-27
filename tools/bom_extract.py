#!/usr/bin/env python3
"""bom_extract.py — cek konsistensi Bill of Materials vs geometri isometrik.

Masalah yang diselesaikan
-------------------------
BOM pada lembar isometrik ditulis TANGAN sebagai daftar literal di script
generator. Riwayat review menunjukkan kelas bug yang berulang karena itu:

    04-review-log.md, ROUND A2, temuan #2:
      "ISO-0003 BOM: 4x elbow LR90 DN150 vs geometri 3 belokan"
      "ISO-0005 BOM: 8x elbow LR90 DN80 vs geometri 9 belokan"
      "ISO-0004 BOM: 2x flange WN DN80 vs flange suction DN65"

Semuanya diperbaiki manual. Script ini membuat pemeriksaan itu otomatis:
menghitung jumlah belokan dari GEOMETRI lalu membandingkannya dengan BOM
yang tertulis di lembar.

Batasan yang disengaja
----------------------
Panjang pipa (meter) TIDAK diverifikasi: skala isometrik NTS dan panjang
segmen pada kertas tidak dapat dikonversi ke panjang nyata tanpa tabel
vertex. Yang dapat dihitung secara jujur adalah JUMLAH belokan, karena
setiap belokan = titik sambungan antar segmen dengan perubahan arah > 5°.

DN per belokan juga tidak diklaim: DN tidak tertanam di entitas
garis, hanya di label teks. Karena itu perbandingan dilakukan pada
TOTAL belokan per lembar, bukan per ukuran.

Pemakaian:
    python tools/bom_extract.py              # laporan
    python tools/bom_extract.py --json       # terstruktur (CI)
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAD = REPO / "cad"

# Toleransi panjang nyata untuk menganggap dua ujung segmen menyatu (mm kertas)
JOINT_EPS_MM = 0.35
# Perubahan arah minimum yang dianggap belokan (derajat). Sudut isometrik
# sejati berjarak 60°, sehingga 5° aman memisahkan belokan dari kolinear.
BEND_MIN_DEG = 5.0

# Kolom tabel BOM pada lembar A3 (koordinat mm), lihat iso_common.py
BOM_NO_X = (272.0, 277.0)
BOM_DESC_X = (276.0, 300.0)
BOM_SIZE_X = (330.0, 340.0)
BOM_QTY_X = (340.0, 360.0)


@dataclass
class BomRow:
    no: str
    desc: str
    size: str
    qty_text: str
    qty: int | None


@dataclass
class Finding:
    level: str      # ERROR | WARN | INFO
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


# --------------------------------------------------------------------------- geom
def _angle(p, q) -> float:
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180.0


def count_bends(msp, layer="REF-PROC") -> tuple[int, int, list]:
    """Hitung belokan (elbow) dari segmen line pada layer pipa.

    Kembalikan (jumlah_belokan, jumlah_segmen, daftar_titik_belokan).

    Klasifikasi titik sambungan:
      derajat 0   : kolinear (sambungan lurus / stub)  -> bukan belokan
      derajat 1-2 : TEE / cabang (3 segmen bertemu)    -> BUKAN elbow
      derajat 2   : elbow sejati                       -> dihitung
    Toleransi: ujung menyatu < JOINT_EPS_MM, belokan bila > BEND_MIN_DEG.
    """
    segs = [((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y))
            for e in msp.query(f'LINE[layer=="{layer}"]')]

    # kumpulkan semua ujung yang berimpit -> titik sambungan
    joints: dict[tuple[float, float], list] = {}

    def key(p):
        return (round(p[0] / JOINT_EPS_MM), round(p[1] / JOINT_EPS_MM))

    for s, t in segs:
        for p, q in ((s, t), (t, s)):
            joints.setdefault(key(p), []).append((p, q))

    bends = []
    for bucket in joints.values():
        # buang duplikat segmen (sebagian entity kembar)
        uniq = {(round(p[0], 3), round(p[1], 3), round(q[0], 3), round(q[1], 3))
                for p, q in bucket}
        if len(uniq) != 2:
            # 1 arah = ujung bebas; >=3 arah = TEE / cabang -> bukan elbow
            continue
        # uniq berisi (p.x, p.y, q.x, q.y) -> ubah kembali ke pasangan titik
        items = list(uniq)
        (p1x, p1y, q1x, q1y), (p2x, p2y, q2x, q2y) = items[0], items[1]
        a1 = _angle((p1x, p1y), (q1x, q1y))
        a2 = _angle((p2x, p2y), (q2x, q2y))
        delta = abs(a1 - a2)
        delta = min(delta, 180.0 - delta)
        if delta >= BEND_MIN_DEG:
            bends.append((round(q1x, 2), round(q1y, 2), round(delta, 1)))
    return len(bends), len(segs), bends


# --------------------------------------------------------------------------- bom
def parse_bom(msp) -> list[BomRow]:
    """Parse tabel BOM dari kolom kanan lembar (koordinat tetap)."""
    texts = [(e.dxf.insert.x, e.dxf.insert.y, e.text.strip())
             for e in msp.query("MTEXT")]

    # baris ditandai kolom NO berisi angka bulat
    rows = []
    for x, y, t in texts:
        if not (BOM_NO_X[0] <= x <= BOM_NO_X[1]) or not re.fullmatch(r"\d{1,2}", t):
            continue
        desc = size = qty = ""
        for x2, y2, t2 in texts:
            if abs(y2 - y) > 0.6 or x2 <= BOM_NO_X[1]:
                continue
            if BOM_DESC_X[0] <= x2 <= BOM_DESC_X[1] and not size:
                desc = t2
            elif BOM_SIZE_X[0] <= x2 <= BOM_SIZE_X[1]:
                size = t2
            elif BOM_QTY_X[0] <= x2 <= BOM_QTY_X[1]:
                qty = t2
        m = re.match(r"(\d+)", qty)
        rows.append(BomRow(t, desc, size, qty, int(m.group(1)) if m else None))
    rows.sort(key=lambda r: int(r.no) if r.no.isdigit() else 99)
    return rows


def is_elbow(desc: str) -> bool:
    return bool(re.search(r"\b(ELL|ELBOW)\b", desc.upper()))


def is_tee(desc: str) -> bool:
    return "TEE" in desc.upper()


# --------------------------------------------------------------------------- main
def check_sheet(path: Path, rep: Report) -> dict:
    import ezdxf

    doc = ezdxf.readfile(str(path))
    msp = doc.modelspace()
    n_bend, n_seg, pts = count_bends(msp)
    rows = parse_bom(msp)

    elbows = [r for r in rows if is_elbow(r.desc)]
    tees = [r for r in rows if is_tee(r.desc)]
    qty_elbow = sum(r.qty for r in elbows if r.qty is not None)
    qty_tee = sum(r.qty for r in tees if r.qty is not None)

    sheet = path.stem
    info = {
        "sheet": sheet,
        "segments": n_seg,
        "bends_geometry": n_bend,
        "elbows_bom": qty_elbow,
        "tees_bom": qty_tee,
        "bom_rows": len(rows),
        "unparsed_qty": [r.no for r in rows if r.qty is None],
    }

    if n_seg == 0:
        rep.err(sheet, "tidak ada segmen REF-PROC — geometri pipa tidak terbaca")
        return info
    if not rows:
        rep.err(sheet, "tabel BOM tidak terbaca")
        return info

    # Geometri menghitung belokan; BOM menghitung elbow + tee.
    # TEE tidak menimbulkan perubahan arah, jadi:
    #   bends_geom  ==  elbows_bom
    expected = qty_elbow
    if n_bend != expected:
        rep.err(sheet,
                f"jumlah belokan geometri {n_bend} != elbow di BOM {expected} "
                f"(selisih {n_bend - expected:+d}); rincian BOM: "
                + ", ".join(f"{r.qty or '?'}x {r.size}" for r in elbows))

    if info["unparsed_qty"]:
        rep.warn(sheet, f"baris BOM tanpa kuantitas terbaca: "
                        f"{info['unparsed_qty']}")
    if qty_tee:
        rep.findings.append(Finding(
            "INFO", sheet,
            f"{qty_tee} tee di BOM (tidak dihitung sebagai belokan — "
            f"tee tidak mengubah arah)"))
    return info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    try:
        import ezdxf  # noqa: F401
    except ImportError:
        print("ezdxf tidak terpasang — BOM check dilewati")
        return 0

    rep = Report()
    sheets = sorted(CAD.glob("iso_*.dxf"))
    if not sheets:
        rep.err("bom", f"tidak ada iso_*.dxf di {CAD}")

    for p in sheets:
        try:
            rep.sheets[p.stem] = check_sheet(p, rep)
        except Exception as exc:
            rep.err(p.stem, f"gagal memproses: {exc}")

    failed = bool(rep.errors) or (args.strict and any(
        f.level == "WARN" for f in rep.findings))

    if args.json:
        print(json.dumps({
            "ok": not failed,
            "sheets": rep.sheets,
            "findings": [f.__dict__ for f in rep.findings],
        }, indent=2, ensure_ascii=False))
    else:
        print("=" * 78)
        print("KONSISTENSI BOM vs GEOMETRI ISOMETRIK")
        print("=" * 78)
        hdr = f"{'lembar':<16}{'segmen':>7}{'belokan':>9}{'elbow BOM':>10}{'tee BOM':>8}"
        print(hdr)
        print("-" * 78)
        for name, s in rep.sheets.items():
            print(f"{name:<16}{s['segments']:>7}{s['bends_geometry']:>9}"
                  f"{s['elbows_bom']:>10}{s['tees_bom']:>8}")
        print("-" * 78)
        for f in rep.findings:
            print(f"[{f.level:<5}] {f.sheet:<16} {f.message}")
        if not rep.findings:
            print("tidak ada temuan")
        print("-" * 78)
        ne = len(rep.errors)
        print(f"HASIL: {ne} error, "
              f"{sum(1 for f in rep.findings if f.level == 'WARN')} warning")
        print("KONSISTEN" if not failed else "TIDAK KONSISTEN")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
