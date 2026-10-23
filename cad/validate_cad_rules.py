#!/usr/bin/env python3
"""validate_cad_rules.py — CAD Linter & Cross-Discipline QA for Company Engineering Drawings.

Memeriksa file DXF dan manifest teks engineering terhadap standar drafting perusahaan
(ANSI/ISA-5.1-2024, ISO 10628-2, ISO 6412-2, company-cad-standard):
  1. Check 1 (Forbidden Entities): Bebas POLYFACE, MESH, 3DSOLID, dan single-line TEXT (wajib MTEXT).
  2. Check 2 (MTEXT Style & Height): Style ARIAL, tinggi karakter 0.5 <= h <= 3.0 mm.
  3. Check 3 (Layer Lineweights): Layer utama REF-* lineweight > 0 (telah dipost-process apply_text.py).
  4. Check 4 (Unbroken Orthogonal Process Line Crossings): Deteksi pipa proses REF-PROC yang bersilang tanpa break gap 3 mm.
  5. Check 5 (Text Collisions): Deteksi tabrakan teks vs LINE/ARC/CIRCLE di REF-PROC/EQUIP/SYM, dan teks vs teks (>0.3 mm).
  6. Check 6 (Dangling Endpoints): Deteksi ujung bebas (floating / dangling) pada LINE REF-PROC dan REF-EQUIP.
  7. Check 7 (Signal Crossings): Deteksi garis sinyal REF-SIG/REF-SIGP ortogonal yang menembus pipa/peralatan tanpa break 3 mm.
  8. Cross-Discipline QA (--cross-check): Verifikasi konsistensi Line Numbers & Tag Katup/Instrumen lintas disiplin.

Pemakaian CLI:
  $PY validate_cad_rules.py <dxf_path> [texts_json_path] [--mode auto|pid|iso|plan] [--cross-check <pid_json> <iso1_json> ...]
  $PY validate_cad_rules.py --cross-check pid.texts.json iso1.texts.json plan.texts.json
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import ezdxf
except ImportError:
    sys.exit("Error: pustaka 'ezdxf' tidak ditemukan. Jalankan dengan runtime Python yang memiliki ezdxf.")

# Standard Company Lineweights (mm x 100)
COMPANY_LINEWEIGHTS = {
    "REF-PROC": 50,
    "REF-EQUIP": 35,
    "REF-FRAME": 35,
    "REF-SYM": 25,
    "REF-TITLE": 25,
    "REF-TEXT": 18,
    "REF-ROAD": 18,
    "REF-SIG": 13,
    "REF-SIGP": 13,
    "REF-HATCH": 13,
    "REF-FENCE": 13,
    "REF-DIM": 9,
    "REF-GRID": 9,
}

LINE_RE = re.compile(r"\b\d{3}-[A-Z]{2}-\d{4}\b")
TAG_RE = re.compile(r"\b(?:GV|LV|PV|SDV|CV|PSV|ST|FE|FT|FI|PT|PI|PIC|TT|TI|LT|LG|LIC)-\d{3}\b")
ISA_FUNCS = {
    "GV", "LV", "PV", "SDV", "CV", "PSV", "ST", "FE", "FT", "FI",
    "PT", "PI", "PIC", "TT", "TI", "LT", "LG", "LIC", "TIC", "FIC",
    "PDT", "PDI", "PDIC"
}


# =============================================================================
# GEOMETRIC & MATH HELPERS
# =============================================================================

def point_to_segment_dist(p: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Hitung jarak terpendek dari titik p ke segmen garis a->b."""
    px, py = p
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    if l2 < 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def point_to_arc_dist(p: Tuple[float, float], arc) -> float:
    """Hitung jarak dari titik p ke busur ARC ezdxf."""
    px, py = p
    cx, cy = float(arc.dxf.center.x), float(arc.dxf.center.y)
    r = float(arc.dxf.radius)
    sa = float(arc.dxf.start_angle) % 360.0
    ea = float(arc.dxf.end_angle) % 360.0

    ang = math.degrees(math.atan2(py - cy, px - cx)) % 360.0
    in_arc = (sa <= ang <= ea) if sa <= ea else (ang >= sa or ang <= ea)

    p_start = (cx + r * math.cos(math.radians(sa)), cy + r * math.sin(math.radians(sa)))
    p_end = (cx + r * math.cos(math.radians(ea)), cy + r * math.sin(math.radians(ea)))

    if in_arc:
        return abs(math.hypot(px - cx, py - cy) - r)
    return min(
        math.hypot(px - p_start[0], py - p_start[1]),
        math.hypot(px - p_end[0], py - p_end[1]),
    )


def point_to_circle_dist(p: Tuple[float, float], circ) -> float:
    """Hitung jarak terpendek dari titik p ke keliling lingkaran CIRCLE ezdxf."""
    px, py = p
    cx, cy = float(circ.dxf.center.x), float(circ.dxf.center.y)
    r = float(circ.dxf.radius)
    return abs(math.hypot(px - cx, py - cy) - r)


def point_to_solid_dist(p: Tuple[float, float], solid) -> float:
    """Hitung jarak dari titik p ke batas/interior entitas SOLID ezdxf."""
    pts = [
        (float(solid.dxf.vtx0.x), float(solid.dxf.vtx0.y)),
        (float(solid.dxf.vtx1.x), float(solid.dxf.vtx1.y)),
        (float(solid.dxf.vtx2.x), float(solid.dxf.vtx2.y)),
    ]
    if hasattr(solid.dxf, "vtx3"):
        p3 = (float(solid.dxf.vtx3.x), float(solid.dxf.vtx3.y))
        if p3 != pts[2]:
            pts.append(p3)

    px, py = p
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-12) + x1):
            inside = not inside
    if inside:
        return 0.0

    min_d = 1e9
    for i in range(n):
        min_d = min(min_d, point_to_segment_dist(p, pts[i], pts[(i + 1) % n]))
    return min_d


def segment_circle_intersections(
    p1: Tuple[float, float], p2: Tuple[float, float], center: Tuple[float, float], r: float
) -> List[Tuple[float, float]]:
    """Cari titik potong antara segmen garis p1->p2 dengan keliling lingkaran (center, r)."""
    (x1, y1), (x2, y2) = p1, p2
    cx, cy = center
    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy
    a = dx * dx + dy * dy
    b = 2.0 * (fx * dx + fy * dy)
    c_val = fx * fx + fy * fy - r * r
    if a < 1e-12:
        return []
    disc = b * b - 4.0 * a * c_val
    if disc < 0.0:
        return []
    sq = math.sqrt(disc)
    t1 = (-b - sq) / (2.0 * a)
    t2 = (-b + sq) / (2.0 * a)
    pts = []
    for t in (t1, t2):
        if 0.0 <= t <= 1.0:
            pts.append((x1 + t * dx, y1 + t * dy))
    return pts


def segment_intersects_aabb(
    p1: Tuple[float, float], p2: Tuple[float, float], box: Tuple[float, float, float, float]
) -> bool:
    """Uji apakah segmen garis p1->p2 menembus AABB (xmin, ymin, xmax, ymax) via Liang-Barsky."""
    xmin, ymin, xmax, ymax = box
    x1, y1 = p1
    x2, y2 = p2

    # Bila salah satu endpoint berada di dalam kotak
    if (xmin <= x1 <= xmax and ymin <= y1 <= ymax) or (xmin <= x2 <= xmax and ymin <= y2 <= ymax):
        return True

    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]

    u1 = 0.0
    u2 = 1.0

    for pi, qi in zip(p, q):
        if abs(pi) < 1e-9:
            if qi < 0:
                return False
        else:
            t = qi / pi
            if pi < 0:
                if t > u2:
                    return False
                if t > u1:
                    u1 = t
            else:
                if t < u1:
                    return False
                if t < u2:
                    u2 = t
    return u1 <= u2


def compute_text_local_box(
    text: str, h: float, att: int = 5, shrink: float = 0.35
) -> Tuple[float, float, float, float]:
    """Hitung bounding box 2D teks di ruang koordinat lokal (terhadap origin teks) dengan shrink margin."""
    lines = text.split("\n")
    max_len = max(len(l) for l in lines) if lines else 1
    num_lines = len(lines)
    w = max_len * 0.62 * h
    total_h = h * (1.0 + 0.25 * (num_lines - 1))

    # Horizontal alignment
    if att in (1, 4, 7):  # Left
        lx0, lx1 = 0.0, w
    elif att in (2, 5, 8):  # Center
        lx0, lx1 = -w / 2.0, w / 2.0
    else:  # Right
        lx0, lx1 = -w, 0.0

    # Vertical alignment
    if att in (1, 2, 3):  # Top
        ly0, ly1 = -total_h, 0.0
    elif att in (4, 5, 6):  # Middle
        ly0, ly1 = -total_h / 2.0, total_h / 2.0
    else:  # Bottom
        ly0, ly1 = 0.0, total_h

    # Terapkan margin shrink agar tidak false positive terhadap garis pipa di dekatnya
    lx0 += shrink
    lx1 -= shrink
    ly0 += shrink
    ly1 -= shrink

    # Clamp batas minimal agar karakter ringkas tidak kolaps
    if lx1 <= lx0:
        mid_x = (lx0 + lx1) / 2.0
        lx0, lx1 = mid_x - 0.1, mid_x + 0.1
    if ly1 <= ly0:
        mid_y = (ly0 + ly1) / 2.0
        ly0, ly1 = mid_y - 0.1, mid_y + 0.1

    return lx0, ly0, lx1, ly1


def get_text_obb_corners(item: Dict[str, Any], shrink: float = 0.15) -> List[Tuple[float, float]]:
    """Dapatkan 4 sudut 2D bounding box teks di ruang koordinat gambar (world coordinates)."""
    t = str(item.get("t", "")).strip()
    x = float(item.get("x", 0.0))
    y = float(item.get("y", 0.0))
    h = float(item.get("h", 2.0))
    rot_deg = float(item.get("rot", 0.0))
    att = int(item.get("att", 5))

    lx0, ly0, lx1, ly1 = compute_text_local_box(t, h, att=att, shrink=shrink)
    rad = math.radians(rot_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    corners = [(lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1)]
    world_corners = []
    for lx, ly in corners:
        wx = x + (lx * cos_a - ly * sin_a)
        wy = y + (lx * sin_a + ly * cos_a)
        world_corners.append((wx, wy))
    return world_corners


def obbs_overlap_sat(v1: List[Tuple[float, float]], v2: List[Tuple[float, float]]) -> bool:
    """Uji tumpang tindih 2 oriented bounding box (OBB) via Separating Axis Theorem (SAT)."""
    axes = [
        (v1[1][0] - v1[0][0], v1[1][1] - v1[0][1]),
        (v1[3][0] - v1[0][0], v1[3][1] - v1[0][1]),
        (v2[1][0] - v2[0][0], v2[1][1] - v2[0][1]),
        (v2[3][0] - v2[0][0], v2[3][1] - v2[0][1]),
    ]
    for ex, ey in axes:
        length = math.hypot(ex, ey)
        if length < 1e-9:
            continue
        nx, ny = -ey / length, ex / length
        p1 = [p[0] * nx + p[1] * ny for p in v1]
        p2 = [p[0] * nx + p[1] * ny for p in v2]
        if max(p1) <= min(p2) or max(p2) <= min(p1):
            return False
    return True


def is_text_in_bubble(item: Dict[str, Any], circle) -> bool:
    """Periksa apakah teks secara sah berada DI DALAM bubble/kotak instrumen.
    
    Teks yang pusatnya di dalam lingkaran berdiameter >= 1.6 x h dan seluruh batasnya
    tidak keluar dari lingkaran dikecualikan dari tabrakan lingkaran.
    """
    x = float(item.get("x", 0.0))
    y = float(item.get("y", 0.0))
    h = float(item.get("h", 2.0))
    cx = float(circle.dxf.center.x)
    cy = float(circle.dxf.center.y)
    r = float(circle.dxf.radius)

    # 1. Diameter lingkaran harus memadai (>= 1.6 * h)
    if 2.0 * r < 1.6 * h:
        return False

    # 2. Titik pusat teks berada di dalam lingkaran
    if math.hypot(x - cx, y - cy) > r:
        return False

    # 3. Seluruh 4 sudut bounding box teks berada di dalam lingkaran (margin aman 0.1 mm)
    corners = get_text_obb_corners(item, shrink=0.0)
    for wx, wy in corners:
        if math.hypot(wx - cx, wy - cy) > r + 0.1:
            return False

    return True


def merge_collinear_lines(
    lines: List[Any], gap_thresh: float = 2.2
) -> Tuple[List[Tuple[float, float, float]], List[Tuple[float, float, float]]]:
    """Gabungkan segmen garis kolinear ortogonal pada layer sinyal (REF-SIG/REF-SIGP).
    
    Hanya menggabungkan segmen dengan celah <= gap_thresh (default 2.2 mm, mencakup gap
    normal dashed 1.6 mm). Celah break resmi 3.0 mm (dashed_brk) tetap terpisah.
    
    Returns:
        (merged_h, merged_v)
        merged_h: list of (x_min, x_max, y)
        merged_v: list of (y_min, y_max, x)
    """
    h_groups: Dict[float, List[Tuple[float, float]]] = {}
    v_groups: Dict[float, List[Tuple[float, float]]] = {}

    for l in lines:
        p1 = l.dxf.start
        p2 = l.dxf.end
        x1, y1 = float(p1.x), float(p1.y)
        x2, y2 = float(p2.x), float(p2.y)

        if abs(y1 - y2) < 0.05:
            y = round((y1 + y2) / 2.0, 2)
            h_groups.setdefault(y, []).append((min(x1, x2), max(x1, x2)))
        elif abs(x1 - x2) < 0.05:
            x = round((x1 + x2) / 2.0, 2)
            v_groups.setdefault(x, []).append((min(y1, y2), max(y1, y2)))

    merged_h: List[Tuple[float, float, float]] = []
    for y, intervals in h_groups.items():
        intervals.sort()
        cur_min, cur_max = intervals[0]
        for mn, mx in intervals[1:]:
            if mn <= cur_max + gap_thresh:
                cur_max = max(cur_max, mx)
            else:
                merged_h.append((cur_min, cur_max, y))
                cur_min, cur_max = mn, mx
        merged_h.append((cur_min, cur_max, y))

    merged_v: List[Tuple[float, float, float]] = []
    for x, intervals in v_groups.items():
        intervals.sort()
        cur_min, cur_max = intervals[0]
        for mn, mx in intervals[1:]:
            if mn <= cur_max + gap_thresh:
                cur_max = max(cur_max, mx)
            else:
                merged_v.append((cur_min, cur_max, x))
                cur_min, cur_max = mn, mx
        merged_v.append((cur_min, cur_max, x))

    return merged_h, merged_v


# =============================================================================
# MANIFEST PARSERS
# =============================================================================

def extract_manifest_texts(manifest_path: Path) -> List[Dict[str, Any]]:
    """Muat manifest teks JSON (baik format list legasi maupun dict {'texts': [...]})."""
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  [WARN] Gagal membaca manifest {manifest_path}: {exc}")
        return []

    if isinstance(data, dict):
        return data.get("texts", [])
    if isinstance(data, list):
        return data
    return []


def extract_tags_and_lines_from_manifest(
    manifest_path: Path,
) -> Tuple[List[str], List[str]]:
    """Ekstrak line numbers dan tags katup/instrumen (termasuk deteksi bubble ISA-5.1 vertikal)."""
    texts = extract_manifest_texts(manifest_path)
    all_raw = " ".join(str(it.get("t", "")) for it in texts)

    # 1. Line numbers berpola 000-XX-0000
    line_numbers = sorted(set(LINE_RE.findall(all_raw)))

    # 2. Tag terformat langsung (mis. GV-101, PSV-101)
    direct_tags = set(TAG_RE.findall(all_raw))

    # 3. Pasangan ISA-5.1 bubble vertikal (Function Code di atas, Tag Number di bawah)
    f_items = [it for it in texts if str(it.get("t", "")).strip() in ISA_FUNCS]
    n_items = [it for it in texts if re.match(r"^\d{3}$", str(it.get("t", "")).strip())]

    isa_pairs = set()
    for f in f_items:
        fx, fy = float(f.get("x", 0.0)), float(f.get("y", 0.0))
        ft = str(f.get("t", "")).strip()
        for n in n_items:
            nx, ny = float(n.get("x", 0.0)), float(n.get("y", 0.0))
            nt = str(n.get("t", "")).strip()
            # Pasangan bubble memiliki x hampir identik dan y function berada di atas y number (1.5 - 6.0 mm)
            if abs(fx - nx) < 0.6 and 1.5 <= (fy - ny) <= 6.0:
                isa_pairs.add(f"{ft}-{nt}")

    all_tags = sorted(direct_tags | isa_pairs)
    return line_numbers, all_tags


# =============================================================================
# MAIN CAD VALIDATOR CLASS
# =============================================================================

class CADValidator:
    """Validator standar CAD perusahaan untuk file DXF dan manifest."""

    def __init__(
        self,
        dxf_path: str,
        texts_json_path: Optional[str] = None,
        mode: str = "auto",
        dangling_severity: str = "auto",
        dangling_tol: float = 0.5,
        dangling_helper_len: float = 3.0,
    ):
        self.dxf_path = Path(dxf_path)
        self.mode = mode
        self.dangling_severity = dangling_severity.lower()
        self.dangling_tol = dangling_tol
        self.dangling_helper_len = dangling_helper_len

        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.dangling_endpoints: List[Tuple[str, Tuple[float, float], float]] = []
        self.signal_crossings: List[Tuple[str, float, float, float, float]] = []
        self.text_collisions: List[Tuple[str, str, Tuple[float, float], str]] = []

        # Otomatis cari texts.json jika tidak disediakan eksplisit
        if texts_json_path:
            self.json_path: Optional[Path] = Path(texts_json_path)
        else:
            cand1 = self.dxf_path.with_suffix(".texts.json")
            cand2 = self.dxf_path.with_name(self.dxf_path.stem + ".manifest.json")
            if cand1.exists():
                self.json_path = cand1
            elif cand2.exists():
                self.json_path = cand2
            else:
                self.json_path = None

        if self.mode == "auto":
            stem = self.dxf_path.stem.lower()
            if "pid" in stem:
                self.mode = "pid"
            elif "iso" in stem:
                self.mode = "iso"
            elif "plan" in stem:
                self.mode = "plan"

    def run_all_checks(self) -> Tuple[int, int]:
        """Jalankan Check 1 s.d. 7 pada file DXF target."""
        print(f"\n{'='*75}")
        print(f" CAD RULES VALIDATION: {self.dxf_path.name} (Mode: {self.mode.upper()})")
        print(f"{'='*75}")

        if not self.dxf_path.exists():
            self.errors.append(f"File DXF tidak ditemukan: {self.dxf_path}")
            return len(self.errors), len(self.warnings)

        try:
            doc = ezdxf.readfile(str(self.dxf_path))
        except Exception as exc:
            self.errors.append(f"Gagal membuka DXF: {exc}")
            return len(self.errors), len(self.warnings)

        msp = doc.modelspace()

        # Check 1: Forbidden entities
        self._check_forbidden_entities(msp)

        # Check 2: MTEXT audit (style & font height)
        self._check_mtext_audit(msp)

        # Check 3: Layer lineweights
        self._check_layer_lineweights(doc)

        # Check 4: Unbroken Orthogonal Process Line Crossings
        self._check_unbroken_crossings(msp)

        # Check 5: Text-to-Line / Text-to-Text Collisions
        self._check_text_collisions(msp)

        # Check 6: Dangling Endpoints (REF-PROC / REF-EQUIP)
        self._check_dangling_endpoints(msp)

        # Check 7: Orthogonal Signal Crossings without break
        self._check_signal_crossings(msp)

        # Ringkasan per-file
        print(f"\n--- Ringkasan Hasil Audit {self.dxf_path.name} ---")
        if self.errors:
            print(f"Status: FAIL ({len(self.errors)} error(s), {len(self.warnings)} warning(s))")
            for err in self.errors:
                print(f"  [ERROR] {err}")
        else:
            print(f"Status: PASS (0 errors, {len(self.warnings)} warning(s))")

        for warn in self.warnings:
            print(f"  [WARN]  {warn}")

        return len(self.errors), len(self.warnings)

    def _check_forbidden_entities(self, msp) -> None:
        """Check 1: Pastikan 0 entitas POLYFACE, MESH, 3DSOLID, dan single-line TEXT."""
        forbidden_types = ["POLYFACE", "MESH", "3DSOLID", "TEXT"]
        found = {}
        for ftype in forbidden_types:
            cnt = len(list(msp.query(ftype)))
            if cnt > 0:
                found[ftype] = cnt

        if found:
            for ftype, cnt in found.items():
                if ftype == "TEXT":
                    self.errors.append(
                        f"Check 1: Ditemukan {cnt} entitas 'TEXT' (single-line). "
                        "Perusahaan mewajibkan seluruh teks menggunakan entitas 'MTEXT'."
                    )
                else:
                    self.errors.append(
                        f"Check 1: Ditemukan {cnt} entitas terlarang '{ftype}' "
                        "(gambar teknik piping adalah 2D murni, dilarang 3D mesh)."
                    )
            print("  Check 1 (Entitas Terlarang)    : FAIL")
        else:
            print("  Check 1 (Entitas Terlarang)    : PASS (0 entitas terlarang)")

    def _check_mtext_audit(self, msp) -> None:
        """Check 2: Semua MTEXT wajib style ARIAL dan char_height dalam 0.5 <= h <= 3.0 mm."""
        mtexts = list(msp.query("MTEXT"))
        if not mtexts:
            self.warnings.append("Check 2: Tidak ditemukan entitas MTEXT pada drawing.")
            print("  Check 2 (Audit MTEXT Font)     : WARN (0 MTEXT)")
            return

        bad_style = []
        bad_height = []
        for mt in mtexts:
            style = mt.dxf.style or ""
            h = float(mt.dxf.char_height or 0.0)
            text_snippet = (mt.text or "")[:15].replace("\n", " ")
            if style.upper() != "ARIAL":
                bad_style.append((style, text_snippet))
            if not (0.5 <= h <= 3.001):
                bad_height.append((h, text_snippet))

        failed = False
        if bad_style:
            self.errors.append(
                f"Check 2: {len(bad_style)} MTEXT tidak menggunakan style 'ARIAL'. "
                f"Contoh: {bad_style[:3]}"
            )
            failed = True
        if bad_height:
            self.errors.append(
                f"Check 2: {len(bad_height)} MTEXT char_height di luar batas 0.5–3.0 mm. "
                f"Contoh: {bad_height[:3]}"
            )
            failed = True

        if failed:
            print("  Check 2 (Audit MTEXT Font)     : FAIL")
        else:
            heights = [m.dxf.char_height for m in mtexts]
            print(
                f"  Check 2 (Audit MTEXT Font)     : PASS ({len(mtexts)} MTEXT, style ARIAL, "
                f"h={min(heights):.1f}..{max(heights):.1f} mm)"
            )

    def _check_layer_lineweights(self, doc) -> None:
        """Check 3: Pastikan layer utama yang ada memiliki lineweight > 0."""
        layers = {l.dxf.name: l.dxf.lineweight for l in doc.layers}
        ref_layers = {k: v for k, v in layers.items() if k.startswith("REF-")}

        missing_lw = []
        for name, lw in ref_layers.items():
            if lw <= 0:
                missing_lw.append(f"{name} (lw={lw})")

        if missing_lw:
            self.errors.append(
                f"Check 3: Layer lineweight belum diset (>0): {', '.join(missing_lw)}. "
                "Jalankan apply_text.py terlebih dahulu."
            )
            print("  Check 3 (Layer Lineweights)    : FAIL")
        else:
            print(
                f"  Check 3 (Layer Lineweights)    : PASS ({len(ref_layers)} layer REF-* berbobot > 0)"
            )

    def _check_unbroken_crossings(self, msp) -> None:
        """Check 4: Deteksi persilangan pipa proses ortogonal tanpa break gap 3 mm."""
        proc_lines = list(msp.query('LINE[layer=="REF-PROC"]'))
        h_lines: List[Tuple[float, float, float, float]] = []
        v_lines: List[Tuple[float, float, float, float]] = []

        for line in proc_lines:
            p1 = line.dxf.start
            p2 = line.dxf.end
            x1, y1 = float(p1.x), float(p1.y)
            x2, y2 = float(p2.x), float(p2.y)
            length = math.hypot(x1 - x2, y1 - y2)

            if abs(y1 - y2) < 0.05:
                h_lines.append((min(x1, x2), max(x1, x2), (y1 + y2) / 2.0, length))
            elif abs(x1 - x2) < 0.05:
                v_lines.append((min(y1, y2), max(y1, y2), (x1 + x2) / 2.0, length))

        crossings = []
        for xmin, xmax, y, lh in h_lines:
            for ymin, ymax, x, lv in v_lines:
                if (xmin < x < xmax) and (ymin < y < ymax):
                    dh = min(x - xmin, xmax - x)
                    dv = min(y - ymin, ymax - y)

                    if dh > 1.35 and dv > 1.35 and min(lh, lv) > 6.0:
                        crossings.append((round(x, 2), round(y, 2), round(dh, 2), round(dv, 2)))

        if crossings:
            self.errors.append(
                f"Check 4: Ditemukan {len(crossings)} persilangan pipa proses (REF-PROC) tanpa break gap: "
                f"{crossings}"
            )
            print("  Check 4 (Line Crossings Break) : FAIL")
        else:
            print(
                f"  Check 4 (Line Crossings Break) : PASS (0 unbroken orthogonal process line crossings)"
            )

    def _check_text_collisions(self, msp) -> None:
        """Check 5: Deteksi tabrakan teks vs LINE/ARC/CIRCLE di REF-PROC/EQUIP/SYM dan teks vs teks (>0.3 mm)."""
        if not self.json_path or not self.json_path.exists():
            self.warnings.append(
                "Check 5: File manifest teks JSON tidak ditemukan, melewati deteksi tabrakan teks."
            )
            print("  Check 5 (Text Collisions)      : SKIP (Manifest JSON tidak ditemukan)")
            return

        texts = extract_manifest_texts(self.json_path)
        valid_texts = [it for it in texts if str(it.get("t", "")).strip()]

        target_layers = ("REF-PROC", "REF-EQUIP", "REF-SYM")
        lines = [l for l in msp.query("LINE") if l.dxf.layer in target_layers]
        arcs = [a for a in msp.query("ARC") if a.dxf.layer in target_layers]
        circles = [c for c in msp.query("CIRCLE") if c.dxf.layer in target_layers]

        collisions: List[Tuple[str, str, Tuple[float, float], str]] = []

        # 1. Text vs LINE / CIRCLE / ARC
        for item in valid_texts:
            t = str(item.get("t", "")).strip()
            x = float(item.get("x", 0.0))
            y = float(item.get("y", 0.0))
            h = float(item.get("h", 2.0))
            rot_deg = float(item.get("rot", 0.0))
            att = int(item.get("att", 5))

            box = compute_text_local_box(t, h, att=att, shrink=0.35)
            rad = math.radians(rot_deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            # (a) Text vs LINE
            for pl in lines:
                p1 = pl.dxf.start
                p2 = pl.dxf.end

                dx1, dy1 = float(p1.x) - x, float(p1.y) - y
                dx2, dy2 = float(p2.x) - x, float(p2.y) - y

                tx1 = dx1 * cos_a + dy1 * sin_a
                ty1 = -dx1 * sin_a + dy1 * cos_a

                tx2 = dx2 * cos_a + dy2 * sin_a
                ty2 = -dx2 * sin_a + dy2 * cos_a

                if segment_intersects_aabb((tx1, ty1), (tx2, ty2), box):
                    collisions.append(("LINE", t, (round(x, 2), round(y, 2)), pl.dxf.layer))
                    break

            # (b) Text vs CIRCLE (kecuali jika teks memang secara sah di dalam bubble instrumen)
            for c in circles:
                if is_text_in_bubble(item, c):
                    continue

                cx, cy = float(c.dxf.center.x), float(c.dxf.center.y)
                r = float(c.dxf.radius)

                tcx = (cx - x) * cos_a + (cy - y) * sin_a
                tcy = -(cx - x) * sin_a + (cy - y) * cos_a

                corners = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])]
                edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
                hit = False
                for ep1, ep2 in edges:
                    if segment_circle_intersections(ep1, ep2, (tcx, tcy), r):
                        collisions.append(("CIRCLE", t, (round(x, 2), round(y, 2)), c.dxf.layer))
                        hit = True
                        break
                if hit:
                    break

            # (c) Text vs ARC
            for a in arcs:
                cx, cy = float(a.dxf.center.x), float(a.dxf.center.y)
                r = float(a.dxf.radius)
                sa_deg = float(a.dxf.start_angle) % 360.0
                ea_deg = float(a.dxf.end_angle) % 360.0

                tcx = (cx - x) * cos_a + (cy - y) * sin_a
                tcy = -(cx - x) * sin_a + (cy - y) * cos_a

                corners = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])]
                edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
                hit = False
                for ep1, ep2 in edges:
                    for ix, iy in segment_circle_intersections(ep1, ep2, (tcx, tcy), r):
                        wx = x + (ix * cos_a - iy * sin_a)
                        wy = y + (ix * sin_a + iy * cos_a)
                        ang = math.degrees(math.atan2(wy - cy, wx - cx)) % 360.0
                        in_arc = (sa_deg <= ang <= ea_deg) if sa_deg <= ea_deg else (ang >= sa_deg or ang <= ea_deg)
                        if in_arc:
                            collisions.append(("ARC", t, (round(x, 2), round(y, 2)), a.dxf.layer))
                            hit = True
                            break
                    if hit:
                        break
                if hit:
                    break

        # 2. Text vs Text (Bounding Box tumpang tindih > 0.3 mm)
        obbs = [(it, get_text_obb_corners(it, shrink=0.15)) for it in valid_texts]
        for i in range(len(obbs)):
            for j in range(i + 1, len(obbs)):
                if obbs_overlap_sat(obbs[i][1], obbs[j][1]):
                    t1 = str(obbs[i][0].get("t", "")).strip()
                    t2 = str(obbs[j][0].get("t", "")).strip()
                    pt1 = (round(float(obbs[i][0].get("x", 0.0)), 2), round(float(obbs[i][0].get("y", 0.0)), 2))
                    collisions.append(("TEXT", f"'{t1}' bertumpuk dengan '{t2}'", pt1, "REF-TEXT"))

        self.text_collisions = collisions
        if collisions:
            sample = [(c[0], c[1][:25], c[2], c[3]) for c in collisions[:5]]
            self.errors.append(
                f"Check 5: Ditemukan {len(collisions)} tabrakan teks: {sample}"
            )
            print("  Check 5 (Text Collisions)      : FAIL")
        else:
            print("  Check 5 (Text Collisions)      : PASS (0 text collisions)")

    def _check_dangling_endpoints(self, msp) -> None:
        """Check 6: Deteksi floating/dangling endpoint pada LINE layer REF-PROC dan REF-EQUIP."""
        lines = list(msp.query("LINE"))
        arcs = list(msp.query("ARC"))
        circles = list(msp.query("CIRCLE"))
        solids = list(msp.query("SOLID"))
        mtexts = list(msp.query("MTEXT"))

        target_lines = [l for l in lines if l.dxf.layer in ("REF-PROC", "REF-EQUIP")]
        cand_layers = ("REF-PROC", "REF-EQUIP", "REF-SYM", "REF-FRAME", "REF-TITLE")
        cand_lines = [l for l in lines if l.dxf.layer in cand_layers]
        cand_arcs = [a for a in arcs if a.dxf.layer in cand_layers]
        cand_circs = [c for c in circles if c.dxf.layer in cand_layers]
        cand_solids = [s for s in solids if s.dxf.layer in cand_layers]

        def pt_connected(pt: Tuple[float, float], this_line: Any, tol: float = 0.5) -> bool:
            for ol in cand_lines:
                if ol is this_line:
                    continue
                op1 = (float(ol.dxf.start.x), float(ol.dxf.start.y))
                op2 = (float(ol.dxf.end.x), float(ol.dxf.end.y))
                if point_to_segment_dist(pt, op1, op2) <= tol:
                    return True
            for a in cand_arcs:
                if point_to_arc_dist(pt, a) <= tol:
                    return True
            for c in cand_circs:
                if point_to_circle_dist(pt, c) <= tol:
                    return True
            for s in cand_solids:
                if point_to_solid_dist(pt, s) <= tol:
                    return True
            return False

        def is_valve_symbol_node(pt: Tuple[float, float], this_line: Any, tol: float = 0.5) -> bool:
            """Uji apakah titik pt berada pada simpul simbol katup/aktuator/pompa.
            
            Simpul simbol dikenali jika terhubung ke garis diagonal (segitiga katup / kaki pompa)
            atau ke ARC / CIRCLE pada layer REF-PROC / REF-SYM.
            BUKAN bila menempel pada garis lurus ortogonal REF-EQUIP (seperti standpipe, weir, shell).
            """
            for ol in cand_lines:
                if ol is this_line:
                    continue
                if ol.dxf.layer in ("REF-PROC", "REF-SYM"):
                    op1 = (float(ol.dxf.start.x), float(ol.dxf.start.y))
                    op2 = (float(ol.dxf.end.x), float(ol.dxf.end.y))
                    if point_to_segment_dist(pt, op1, op2) <= tol:
                        # Garis diagonal (seperti segitiga katup atau kaki pompa)
                        if abs(op1[0] - op2[0]) > 0.1 and abs(op1[1] - op2[1]) > 0.1:
                            return True
            for a in cand_arcs:
                if a.dxf.layer in ("REF-PROC", "REF-SYM") and point_to_arc_dist(pt, a) <= max(tol, 1.5):
                    return True
            for c in cand_circs:
                if c.dxf.layer in ("REF-PROC", "REF-SYM") and point_to_circle_dist(pt, c) <= max(tol, 1.5):
                    return True
            return False

        def is_break_gap_endpoint(pt: Tuple[float, float], this_line: Any) -> bool:
            px, py = pt
            is_h = abs(float(this_line.dxf.start.y) - float(this_line.dxf.end.y)) < 0.05
            is_v = abs(float(this_line.dxf.start.x) - float(this_line.dxf.end.x)) < 0.05
            for ol in cand_lines:
                if ol is this_line:
                    continue
                op1 = (float(ol.dxf.start.x), float(ol.dxf.start.y))
                op2 = (float(ol.dxf.end.x), float(ol.dxf.end.y))
                if is_h and abs(op1[0] - op2[0]) < 0.05:
                    ox = (op1[0] + op2[0]) / 2.0
                    if min(op1[1], op2[1]) - 0.5 <= py <= max(op1[1], op2[1]) + 0.5 and 1.0 <= abs(px - ox) <= 2.0:
                        return True
                elif is_v and abs(op1[1] - op2[1]) < 0.05:
                    oy = (op1[1] + op2[1]) / 2.0
                    if min(op1[0], op2[0]) - 0.5 <= px <= max(op1[0], op2[0]) + 0.5 and 1.0 <= abs(py - oy) <= 2.0:
                        return True
            return False

        def is_dashed_segment(this_line: Any) -> bool:
            p1 = (float(this_line.dxf.start.x), float(this_line.dxf.start.y))
            p2 = (float(this_line.dxf.end.x), float(this_line.dxf.end.y))
            is_h = abs(p1[1] - p2[1]) < 0.05
            for ol in cand_lines:
                if ol is this_line:
                    continue
                op1 = (float(ol.dxf.start.x), float(ol.dxf.start.y))
                op2 = (float(ol.dxf.end.x), float(ol.dxf.end.y))
                if is_h and abs(op1[1] - op2[1]) < 0.05 and abs(p1[1] - op1[1]) < 0.05:
                    mn_p, mx_p = min(p1[0], p2[0]), max(p1[0], p2[0])
                    mn_o, mx_o = min(op1[0], op2[0]), max(op1[0], op2[0])
                    if (0 <= mn_p - mx_o <= 2.2) or (0 <= mn_o - mx_p <= 2.2):
                        return True
                elif (not is_h) and abs(op1[0] - op2[0]) < 0.05 and abs(p1[0] - op1[0]) < 0.05:
                    mn_p, mx_p = min(p1[1], p2[1]), max(p1[1], p2[1])
                    mn_o, mx_o = min(op1[1], op2[1]), max(op1[1], op2[1])
                    if (0 <= mn_p - mx_o <= 2.2) or (0 <= mn_o - mx_p <= 2.2):
                        return True
            return False

        def has_interior_connections(this_line: Any) -> bool:
            p1 = (float(this_line.dxf.start.x), float(this_line.dxf.start.y))
            p2 = (float(this_line.dxf.end.x), float(this_line.dxf.end.y))
            for ol in cand_lines:
                if ol is this_line:
                    continue
                for opt in [(float(ol.dxf.start.x), float(ol.dxf.start.y)), (float(ol.dxf.end.x), float(ol.dxf.end.y))]:
                    if point_to_segment_dist(opt, p1, p2) <= 0.5:
                        d1 = math.hypot(opt[0] - p1[0], opt[1] - p1[1])
                        d2 = math.hypot(opt[0] - p2[0], opt[1] - p2[1])
                        if d1 > 0.5 and d2 > 0.5:
                            return True
            return False

        def is_vessel_weir(this_line: Any) -> bool:
            p1 = (float(this_line.dxf.start.x), float(this_line.dxf.start.y))
            p2 = (float(this_line.dxf.end.x), float(this_line.dxf.end.y))
            if pt_connected(p1, this_line) or pt_connected(p2, this_line):
                for mt in mtexts:
                    if "WEIR" in (mt.text or ""):
                        ip = (float(mt.dxf.insert.x), float(mt.dxf.insert.y))
                        if min(math.hypot(p1[0] - ip[0], p1[1] - ip[1]), math.hypot(p2[0] - ip[0], p2[1] - ip[1])) < 10.0:
                            return True
            return False

        dangling_err: List[Tuple[str, Tuple[float, float], float]] = []
        dangling_warn: List[Tuple[str, Tuple[float, float], float]] = []

        for l in target_lines:
            p1 = (float(l.dxf.start.x), float(l.dxf.start.y))
            p2 = (float(l.dxf.end.x), float(l.dxf.end.y))
            length = round(math.hypot(p2[0] - p1[0], p2[1] - p1[1]), 2)

            # 1. Garis bantu pendek (<= 3.0 mm) selalu dikecualikan
            if length <= self.dangling_helper_len:
                continue

            p1_conn = pt_connected(p1, l, tol=self.dangling_tol)
            p2_conn = pt_connected(p2, l, tol=self.dangling_tol)

            # (a) Titik tengahnya menempel garis lain (tick flange / orifice plate / double flange <= 12.5 mm)
            mid = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
            mid_conn = pt_connected(mid, l, tol=self.dangling_tol)
            if length <= 12.5 and mid_conn:
                continue

            # (b) Ujung menempel berada di titik simpul simbol katup/aktuator/pompa
            # HANYA untuk garis pendek < 8.0 mm (panjang tepat >= 8.0 mm TIDAK dikecualikan!)
            if length < 8.0 - 1e-4:
                if (p1_conn and is_valve_symbol_node(p1, l, tol=self.dangling_tol)) or (
                    p2_conn and is_valve_symbol_node(p2, l, tol=self.dangling_tol)
                ):
                    continue
                if is_valve_symbol_node(p1, l, tol=1.5) or is_valve_symbol_node(p2, l, tol=1.5):
                    continue

            # Segmen dashed peralatan (dash <= 5.0 mm)
            if length <= 5.0 and is_dashed_segment(l):
                continue

            # Garis di area legenda/title (x >= 650 mm)
            if min(p1[0], p2[0]) >= 650.0:
                continue

            # Proksimitas fitting/strainer basket (tol <= 1.2 mm)
            if pt_connected(p1, l, tol=1.2) and pt_connected(p2, l, tol=1.2):
                continue

            # Base plate / footing line dengan koneksi interior dari kaki peralatan
            if has_interior_connections(l):
                continue

            # Weir plate bejana tekan
            if is_vessel_weir(l):
                continue

            for pt in (p1, p2):
                if pt_connected(pt, l, tol=self.dangling_tol):
                    continue
                if is_break_gap_endpoint(pt, l):
                    continue

                # Klasifikasi keparahan:
                # Default ('auto' dan 'error'): seluruh temuan dangling tanpa perkecualian sah adalah ERROR
                # 'warning': hanya bila dikonfigurasi spesifik sebagai warning
                if self.dangling_severity == "warning":
                    dangling_warn.append((l.dxf.layer, (round(pt[0], 2), round(pt[1], 2)), length))
                else:
                    dangling_err.append((l.dxf.layer, (round(pt[0], 2), round(pt[1], 2)), length))

        self.dangling_endpoints = dangling_err + dangling_warn

        if dangling_err:
            sample_coords = [d[1] for d in dangling_err[:8]]
            self.errors.append(
                f"Check 6: Ditemukan {len(dangling_err)} ujung garis dangling: {sample_coords}"
            )
            print(f"  Check 6 (Dangling Endpoints)   : FAIL ({len(dangling_err)} error(s), {len(dangling_warn)} warning(s))")

        if dangling_warn:
            sample_coords = [d[1] for d in dangling_warn[:8]]
            self.warnings.append(
                f"Check 6: Ditemukan {len(dangling_warn)} ujung dangling WARN (LINE < 8 mm): {sample_coords}"
            )
            if not dangling_err:
                print(f"  Check 6 (Dangling Endpoints)   : WARN ({len(dangling_warn)} dangling warnings)")

        if not dangling_err and not dangling_warn:
            print("  Check 6 (Dangling Endpoints)   : PASS (0 dangling endpoints)")

    def _check_signal_crossings(self, msp) -> None:
        """Check 7: Deteksi garis sinyal REF-SIG/REF-SIGP ortogonal yang menembus pipa/peralatan tanpa break."""
        sig_lines = list(msp.query('LINE[layer=="REF-SIG"]')) + list(msp.query('LINE[layer=="REF-SIGP"]'))
        if not sig_lines:
            print("  Check 7 (Signal Line Crossing) : PASS (0 signal lines)")
            return

        proc_lines = list(msp.query('LINE[layer=="REF-PROC"]')) + list(msp.query('LINE[layer=="REF-EQUIP"]'))

        # Gabungkan segmen dashed sinyal yang kolinear dengan gap <= 2.2 mm (break 3 mm tetap terpisah)
        sig_h, sig_v = merge_collinear_lines(sig_lines, gap_thresh=2.2)

        # Ekstrak garis proses/peralatan horizontal & vertikal
        proc_h: List[Tuple[float, float, float]] = []
        proc_v: List[Tuple[float, float, float]] = []
        for pl in proc_lines:
            p1 = pl.dxf.start
            p2 = pl.dxf.end
            x1, y1 = float(p1.x), float(p1.y)
            x2, y2 = float(p2.x), float(p2.y)
            if abs(y1 - y2) < 0.05:
                proc_h.append((min(x1, x2), max(x1, x2), (y1 + y2) / 2.0))
            elif abs(x1 - x2) < 0.05:
                proc_v.append((min(y1, y2), max(y1, y2), (x1 + x2) / 2.0))

        crossings: List[Tuple[str, float, float, float, float]] = []

        # Kasus A: Sinyal Horizontal memotong Pipa/Peralatan Vertikal
        for sx1, sx2, sy in sig_h:
            for py1, py2, px in proc_v:
                if (sx1 < px < sx2) and (py1 < sy < py2):
                    dh = min(px - sx1, sx2 - px)
                    dv = min(sy - py1, py2 - sy)
                    if dh > 1.35 and dv > 1.35:
                        crossings.append(("SigH x ProcV", round(px, 2), round(sy, 2), round(dh, 2), round(dv, 2)))

        # Kasus B: Sinyal Vertikal memotong Pipa/Peralatan Horizontal
        for sy1, sy2, sx in sig_v:
            for px1, px2, py in proc_h:
                if (px1 < sx < px2) and (sy1 < py < sy2):
                    dh = min(sx - px1, px2 - sx)
                    dv = min(py - sy1, sy2 - py)
                    if dh > 1.35 and dv > 1.35:
                        crossings.append(("SigV x ProcH", round(sx, 2), round(py, 2), round(dh, 2), round(dv, 2)))

        self.signal_crossings = crossings
        if crossings:
            self.errors.append(
                f"Check 7: Ditemukan {len(crossings)} persilangan sinyal (REF-SIG/REF-SIGP) "
                f"menembus interior pipa/peralatan tanpa break gap: {crossings[:5]}"
            )
            print("  Check 7 (Signal Line Crossing) : FAIL")
        else:
            print("  Check 7 (Signal Line Crossing) : PASS (0 unbroken signal crossings)")


# =============================================================================
# CROSS-DISCIPLINE QA AUDIT
# =============================================================================

def run_cross_check(manifest_paths: List[str]) -> int:
    """Audit konsistensi lintas disiplin antara P&ID dan gambar turunannya."""
    print(f"\n{'='*75}")
    print(" CROSS-DISCIPLINE QA AUDIT: P&ID vs ISOMETRIC & PIPING PLAN")
    print(f"{'='*75}")

    if len(manifest_paths) < 2:
        print("[ERROR] Minimal 2 file manifest diperlukan untuk cross-check: <pid.json> <iso1.json> ...")
        return 1

    pid_path = Path(manifest_paths[0])
    downstream_paths = [Path(p) for p in manifest_paths[1:]]

    if not pid_path.exists():
        print(f"[ERROR] File acuan P&ID tidak ditemukan: {pid_path}")
        return 1

    pid_lines, pid_tags = extract_tags_and_lines_from_manifest(pid_path)
    pid_lines_set = set(pid_lines)
    pid_tags_set = set(pid_tags)

    print(f"P&ID Acuan: {pid_path.name}")
    print(f"  Total Line Numbers : {len(pid_lines)} ({', '.join(pid_lines)})")
    print(f"  Total Tags Terdata : {len(pid_tags)}")

    total_errors = 0

    # 1. Tabel Audit Line Numbers
    print(f"\n--- 1. Tabel Konsistensi Nomor Pipa (Line Numbers) ---")
    print(f"{'Line Number':<16} | {'P&ID':<6} | {'Terdaftar di Dokumen Downstream':<35} | {'Status'}")
    print("-" * 75)

    all_downstream_lines: Dict[str, List[str]] = {}
    for dpath in downstream_paths:
        if not dpath.exists():
            print(f"  [WARN] File {dpath} tidak ditemukan.")
            continue
        d_lines, _ = extract_tags_and_lines_from_manifest(dpath)
        for ln in d_lines:
            all_downstream_lines.setdefault(ln, []).append(dpath.name)

    all_distinct_lines = sorted(pid_lines_set | set(all_downstream_lines.keys()))
    for ln in all_distinct_lines:
        in_pid = "YA" if ln in pid_lines_set else "TIDAK"
        docs = ", ".join(all_downstream_lines.get(ln, [])) or "-"
        if in_pid == "TIDAK":
            status = "ERROR (Tidak ada di P&ID)"
            total_errors += 1
        elif not all_downstream_lines.get(ln):
            status = "OK (Hanya di P&ID)"
        else:
            status = "MATCH (Konsisten)"
        print(f"{ln:<16} | {in_pid:<6} | {docs:<35} | {status}")

    # 2. Tabel Audit Valve & Instrument Tags
    print(f"\n--- 2. Tabel Konsistensi Tag Katup & Instrumen (ISA-5.1 & Valves) ---")
    print(f"{'Tag Identifier':<16} | {'P&ID':<6} | {'Terdaftar di Dokumen Downstream':<35} | {'Status'}")
    print("-" * 75)

    all_downstream_tags: Dict[str, List[str]] = {}
    for dpath in downstream_paths:
        if not dpath.exists():
            continue
        _, d_tags = extract_tags_and_lines_from_manifest(dpath)
        for tg in d_tags:
            all_downstream_tags.setdefault(tg, []).append(dpath.name)

    all_distinct_tags = sorted(pid_tags_set | set(all_downstream_tags.keys()))
    for tg in all_distinct_tags:
        in_pid = "YA" if tg in pid_tags_set else "TIDAK"
        docs = ", ".join(all_downstream_tags.get(tg, [])) or "-"
        if in_pid == "TIDAK":
            status = "ERROR (Tidak ada di P&ID)"
            total_errors += 1
        elif not all_downstream_tags.get(tg):
            status = "OK (Hanya di P&ID)"
        else:
            status = "MATCH (Konsisten)"
        print(f"{tg:<16} | {in_pid:<6} | {docs:<35} | {status}")

    print(f"\n--- Hasil QA Lintas Disiplin ---")
    if total_errors > 0:
        print(f"Status: FAIL ({total_errors} tag/line di downstream tidak terdaftar pada P&ID)")
    else:
        print("Status: PASS (100% Line Numbers & Tags downstream sinkron dengan P&ID)")

    return total_errors


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="CAD Linter & Cross-Discipline QA for Company Engineering Drawings."
    )
    parser.add_argument("dxf_path", nargs="?", default=None, help="Path ke file DXF target.")
    parser.add_argument("texts_json_path", nargs="?", default=None, help="Path opsional ke manifest texts JSON.")
    parser.add_argument(
        "--mode",
        choices=["auto", "pid", "iso", "plan"],
        default="auto",
        help="Mode drawing (default: auto)",
    )
    parser.add_argument(
        "--cross-check",
        nargs="+",
        metavar="JSON",
        help="Lakukan QA audit konsistensi tag/line lintas dokumen: <pid_json> <iso1_json> ...",
    )
    parser.add_argument(
        "--dangling-severity",
        choices=["auto", "warning", "error"],
        default="auto",
        help="Tingkat keparahan temuan dangling endpoints: auto (>=8mm ERROR, <8mm WARN), warning, atau error",
    )
    parser.add_argument(
        "--dangling-tol",
        type=float,
        default=0.5,
        help="Toleransi jarak koneksi endpoint ke entitas lain (default: 0.5 mm)",
    )
    parser.add_argument(
        "--dangling-helper-len",
        type=float,
        default=3.0,
        help="Batas panjang garis bantu pendek yang dikecualikan (default: 3.0 mm)",
    )

    args = parser.parse_args()

    total_errors = 0

    # 1. Audit single DXF jika dxf_path diberikan
    if args.dxf_path:
        validator = CADValidator(
            args.dxf_path,
            args.texts_json_path,
            mode=args.mode,
            dangling_severity=args.dangling_severity,
            dangling_tol=args.dangling_tol,
            dangling_helper_len=args.dangling_helper_len,
        )
        errs, _ = validator.run_all_checks()
        total_errors += errs

    # 2. Audit Cross-check jika diberikan
    if args.cross_check:
        cc_errs = run_cross_check(args.cross_check)
        total_errors += cc_errs

    if not args.dxf_path and not args.cross_check:
        parser.print_help()
        return 1

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
