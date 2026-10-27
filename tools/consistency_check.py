#!/usr/bin/env python3
"""consistency_check.py — konsistensi Design Basis <-> Drawing & Title Block.

Memvalidasi hal yang TIDAK bisa ditangkap linter geometri
(validate_cad_rules.py) karena bukan soal geometri, melainkan kesesuaian
isi antar dokumen:

  D1  Nomor dokumen di title block cocok dengan registri (tools/documents.json)
  D2  Nomor dokumen unik — satu nomor tidak dipakai dua file
  D3  Registri <-> manifest saling cocok (tidak ada file liar / entri basi)
  R1  Sel revisi tertinggi == deklarasi "REV: Xn"
  R2  Revisi monoton tanpa celah (A0,A1,A3 -> gagal)
  T1  Tag equipment design basis muncul di P&ID
  T2  Nomor line design basis muncul di drawing + DN cocok
  T3  Tag instrumen design basis muncul di P&ID
  X1  Tag di P&ID yang tidak dikenal design basis (WARNING; modul di luar
      DB memang sah — lihat review log ROUND ROADMAP-08)

Catatan penting soal bubble ISA: di P&ID, instrumen disimpan sebagai DUA
teks terpisah — fungsi ("LIC") dan nomor loop ("121") berjarak ~4,4 mm di
dalam bubble. Validator menyatukannya kembali berdasarkan kedekatan,
bukan sekadar regex, supaya tidak salah lapor "tag hilang".

Pemakaian:
    python tools/consistency_check.py
    python tools/consistency_check.py --json
    python tools/consistency_check.py --strict   # warning = gagal
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
REGISTRY = Path(__file__).resolve().parent / "documents.json"

DOCNO_RE = re.compile(r"^GPF-\d{2}-[A-Z]{2}-[A-Z]{3}-\d{4}$")
DOCNO_ANY = re.compile(r"GPF-\d{2}-[A-Z]{2}-[A-Z]{3}-\d{4}")
TAG_RE = re.compile(r"\b([A-Z]{1,4}(?:/[A-Z]{1,4})?)-(\d{3}[A-Z]?)\b")
LINE_RE = re.compile(r"\b(\d{3}-[A-Z]{2}-\d{4})\b")
REV_CELL = re.compile(r"^[A-Z]\d$")
LOOP_NUM = re.compile(r"^\d{3}$")

# Fungsi instrumen ISA yang boleh muncul di dalam bubble
ISA_FUNCS = {"PT", "PI", "PIC", "TT", "TI", "TIC", "LT", "LIC", "LG", "FI",
             "FT", "FE", "FY"}
# Jarak maksimum (mm pada lembar) fungsi<->nomor di dalam satu bubble.
BUBBLE_RADIUS_MM = 13.0

IGNORE_PREFIX = {
    "GPF", "ISO", "ASME", "API", "ANSI", "ISA", "NPS", "DN", "SCH", "ASTM",
    "CS", "BW", "RF", "EA", "MAWP", "PSIG", "BARG", "NTS", "DCS", "SIS",
    "ESD", "BL", "NOTE", "REF",
}

# Drawing inti yang tunduk pada design basis GPF-00-DB-0001
CORE_FILES = ("pid_v101", "routing_plan", "iso_go1002", "iso_co1003",
              "iso_co1004")


@dataclass
class Finding:
    rule: str
    level: str          # ERROR | WARN
    subject: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def err(self, rule, subject, msg):
        self.findings.append(Finding(rule, "ERROR", subject, msg))

    def warn(self, rule, subject, msg):
        self.findings.append(Finding(rule, "WARN", subject, msg))

    @property
    def errors(self):
        return [f for f in self.findings if f.level == "ERROR"]

    @property
    def warnings(self):
        return [f for f in self.findings if f.level == "WARN"]


# --------------------------------------------------------------------------- load
def load_manifest(path: Path) -> list[dict]:
    """Normalisasi manifest ke list {"t","x","y"}; format dict & list lama."""
    data = json.loads(path.read_text(encoding="utf-8"))
    texts = data["texts"] if isinstance(data, dict) else data
    out = []
    for t in texts:
        if isinstance(t, dict):
            s = t.get("t")
            out.append({"t": str(s).strip() if s is not None else "",
                        "x": float(t.get("x", 0.0)),
                        "y": float(t.get("y", 0.0))})
        else:
            out.append({"t": str(t).strip(), "x": 0.0, "y": 0.0})
    return out


def parse_design_basis(path: Path) -> dict:
    md = path.read_text(encoding="utf-8")
    out = {"equipment": [], "lines": {}, "instruments": [], "doc_no": None,
           "rev": None, "ok": False}
    try:
        sec3 = md.split("## 3. DAFTAR EQUIPMENT")[1].split("## 4.")[0]
        out["equipment"] = re.findall(r"^\|\s*([A-Z]-\d{3})\s*\|", sec3, re.M)
        sec4 = md.split("## 4. LINE LIST")[1].split("## 5.")[0]
        for no, dn in re.findall(
                r"^\|\s*(\d{3}-[A-Z]{2}-\d{4})\s*\|\s*(\d+)\s*\|", sec4, re.M):
            out["lines"][no] = int(dn)
        sec5 = md.split("## 5. INSTRUMENT INDEX")[1].split("## 6.")[0]
        out["instruments"] = re.findall(
            r"^\|\s*\d*\s*\|\s*([A-Z]+(?:/[A-Z]+)?-\d{3})\s*\|", sec5, re.M)
        out["ok"] = True
    except IndexError:
        pass
    m = re.search(r"Dok\s*:\s*(GPF-[\w-]+),\s*Rev\s*(\w+)", md)
    if m:
        out["doc_no"], out["rev"] = m.group(1), m.group(2)
    return out


# --------------------------------------------------------------------------- tags
def collect_tags(texts: list[dict]) -> set[str]:
    """Kumpulkan tag; satukan pasangan bubble ISA (fungsi + nomor loop).

    Dua pola penulisan yang sah di repo ini:
      * gabungan   : "FE-141", "LIC-121"  (satu string)
      * bubble ISA : fungsi "LIC" + nomor "121" berdekatan (<13 mm)
      * tag majemuk: design basis menulis "FE/FT-141" sementara drawing
                     memisah menjadi "FE-141" + "FI-141" (ISA 5.1: FE =
                     element, FT/FI = transmitter/indicator). Keduanya
                     dianggap memenuhi.
    """
    tags: set[str] = set()
    for t in texts:
        for pre, num in TAG_RE.findall(t["t"]):
            if pre not in IGNORE_PREFIX:
                tags.add(f"{pre}-{num}")

    # Pasangan bubble: fungsi berdiri sendiri + nomor 3 digit berdekatan.
    funcs = [t for t in texts if t["t"] in ISA_FUNCS]
    nums = [t for t in texts if LOOP_NUM.match(t["t"])]
    for f in funcs:
        for n in nums:
            if math.dist((f["x"], f["y"]), (n["x"], n["y"])) <= BUBBLE_RADIUS_MM:
                tags.add(f"{f['t']}-{n['t']}")

    # Tag majemuk "FE/FT-141" -> terpenuhi bila salah satu komponennya ada.
    for t in texts:
        for pre, num in re.findall(
                r"\b([A-Z]+(?:/[A-Z]+)?)-(\d{3}[A-Z]?)\b", t["t"]):
            if "/" not in pre:
                continue
            if any(f"{p}-{num}" in tags for p in pre.split("/")):
                tags.add(f"{pre}-{num}")
    return tags


def collect_lines(texts: list[dict]) -> set[str]:
    return {m.group(1) for t in texts for m in LINE_RE.finditer(t["t"])}


def tag_satisfied(tag: str, drawn: set[str]) -> bool:
    """Apakah tag design basis terpenuhi oleh tag yang digambar?

    Design basis menulis tag majemuk seperti "FE/FT-141" (ISA 5.1: FE =
    element, FT = transmitter). Drawing sah bila memuat salah satu
    komponennya — "FE-141" atau "FT-141" (bahkan "FI-141" sebagai indikator).
    """
    if tag in drawn:
        return True
    if "/" not in tag.split("-")[0]:
        return False
    pre, num = tag.rsplit("-", 1)
    return any(f"{p}-{num}" in drawn for p in pre.split("/"))


# --------------------------------------------------------------------------- rules
def check_doc_no(reg, manifests, rep: Report):
    by_file = {d["file"]: d for d in reg["documents"]}

    for f in sorted(set(manifests) - set(by_file)):
        rep.err("D3", f, "ada di cad/ tetapi TIDAK terdaftar di documents.json")
    for f in sorted(set(by_file) - set(manifests)):
        rep.warn("D3", f, "terdaftar di documents.json tetapi manifest tidak ada")

    seen: dict[str, str] = {}
    for d in reg["documents"]:
        no = d.get("doc_no", "")
        if not DOCNO_RE.match(no):
            rep.err("D1", d["file"],
                    f"format nomor tidak sah: {no!r} (pola GPF-NN-XX-XXX-NNNN)")
        if no in seen:
            rep.err("D2", d["file"], f"nomor {no} sudah dipakai {seen[no]}")
        else:
            seen[no] = d["file"]

    for d in reg["documents"]:
        f, no = d["file"], d["doc_no"]
        texts = manifests.get(f)
        if texts is None:
            continue
        # Nomor dokumen sering ditulis berprefiks label: "DOC NO: GPF-00-..."
        # -> cari pola di dalam teks, bukan hanya fullmatch.
        found: set[str] = set()
        for t in texts:
            found.update(DOCNO_ANY.findall(t["t"]))
        if not found:
            rep.err("D1", f, f"tidak ada nomor dokumen pada title block "
                             f"(diharapkan {no})")
        elif no not in found:
            rep.err("D1", f, f"title block memuat {sorted(found)} "
                             f"tetapi registri mengharapkan {no}")


def check_revision(file: str, texts: list[dict], rep: Report):
    strs = [t["t"] for t in texts]
    cells = [s for s in strs if REV_CELL.match(s)]
    if not cells:
        rep.warn("R1", file, "tidak ditemukan sel revisi (A0/A1/...)")
        return

    # R1: sel tertinggi harus sama dengan deklarasi "REV: Xn"
    decl = [s for s in strs if re.match(r"^REV\s*:", s, re.I)]
    if decl:
        m = re.search(r"\b([A-Z]\d)\b", decl[-1])
        if m:
            top = fmtid(max(sortid(c) for c in cells))
            if m.group(1) != top:
                rep.err("R1", file, f"sel revisi tertinggi {top} != deklarasi "
                                    f"'REV: {m.group(1)}'")

    # R2: berurutan tanpa celah, mulai A0
    ids = sorted({sortid(c) for c in cells})
    if ids[0] != (0, 0):
        rep.err("R2", file, f"revisi tidak dimulai A0 (mulai {fmtid(ids[0])})")
    for a, b in zip(ids, ids[1:]):
        contiguous = ((b[0] == a[0] and b[1] == a[1] + 1)
                      or (b[0] == a[0] + 1 and b[1] == 0))
        if not contiguous:
            rep.err("R2", file, f"celah revisi: {fmtid(a)} -> {fmtid(b)}")


def sortid(cell: str) -> tuple[int, int]:
    return (ord(cell[0]) - ord("A"), int(cell[1:]))


def fmtid(t: tuple[int, int]) -> str:
    return f"{chr(ord('A') + t[0])}{t[1]}"


def check_design_basis(db, reg, manifests, rep: Report):
    if not db["ok"]:
        rep.err("T0", "design basis", "gagal mem-parse tabel design basis")
        return
    by_file = {d["file"]: d for d in reg["documents"]}

    # Cakupan equipment per lembar. P&ID area separator memang TIDAK memuat
    # flare stack F-101 dan KO drum V-102 — keduanya domain routing plan.
    # Tanpa pemetaan ini, validator akan melaporkan false positive.
    EQUIP_SCOPE = {
        "pid_v101": {"V-101", "P-101", "T-101"},
        "routing_plan": set(db["equipment"]),
    }
    INSTR_SCOPE_PID = set(db["instruments"])

    for f in CORE_FILES:
        texts = manifests.get(f)
        if texts is None:
            rep.err("T0", f, "manifest tidak ada — konsistensi tak dapat dicek")
            continue
        drawn = collect_tags(texts)
        dtype = by_file.get(f, {}).get("type", "")

        if dtype == "P&ID":
            expect = (EQUIP_SCOPE.get(f, set(db["equipment"]))
                      | INSTR_SCOPE_PID)
            for tag in sorted(expect):
                if tag_satisfied(tag, drawn):
                    continue
                rep.err("T1", f, f"tag {tag} ada di design basis "
                                 f"tetapi tidak ditemukan di drawing")

        drawn_lines = collect_lines(texts)
        for no in sorted(db["lines"]):
            if no in drawn_lines:
                continue
            if dtype == "ISOMETRIC":
                continue  # iso memang hanya memuat line-nya sendiri
            rep.err("T2", f, f"line {no} ada di design basis "
                             f"tetapi tidak ditemukan di drawing")

        for t in texts:
            for no, dn in db["lines"].items():
                if not t["t"].startswith(no):
                    continue
                m = re.search(r"DN\s*(\d+)", t["t"])
                if m and int(m.group(1)) != dn:
                    rep.err("T2", f, f"{no}: DN{m.group(1)} di drawing vs "
                                     f"DN{dn} di design basis")

    pid = manifests.get("pid_v101")
    if pid:
        known = (set(db["equipment"]) | INSTR_SCOPE_PID
                 | EQUIP_SCOPE.get("pid_v101", set()))
        drawn = collect_tags(pid)
        # FE/FT-141 sah bila FE-141 atau FT-141 dikenal (pola tag majemuk)
        unknown = []
        for t in sorted(drawn):
            pre, num = t.rsplit("-", 1)
            if pre in IGNORE_PREFIX or t in known:
                continue
            if any(f"{p}-{num}" in known for p in pre.split("/")):
                continue
            unknown.append(t)
        if unknown:
            rep.warn("X1", "pid_v101",
                     f"{len(unknown)} tag tidak ada di design basis: "
                     + ", ".join(unknown[:12])
                     + (" ..." if len(unknown) > 12 else ""))


# --------------------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="warning dianggap gagal")
    args = ap.parse_args(argv)

    rep = Report()
    if REGISTRY.is_file():
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    else:
        reg = {"documents": []}
        rep.err("D0", "documents.json", f"registri tidak ditemukan: {REGISTRY}")

    manifests: dict[str, list[dict]] = {}
    for p in sorted(CAD.glob("*.texts.json")):
        if p.name.startswith(("test_", "test_opt")):
            continue
        try:
            manifests[p.name.replace(".texts.json", "")] = load_manifest(p)
        except Exception as exc:
            rep.err("D0", p.name, f"manifest tidak bisa dibaca: {exc}")

    check_doc_no(reg, manifests, rep)

    for d in reg["documents"]:
        texts = manifests.get(d["file"])
        if texts is not None:
            check_revision(d["file"], texts, rep)

    db_file = reg.get("design_basis", {}).get("file",
                                             "dokumen/01-design-basis.md")
    db_path = REPO / db_file
    if db_path.is_file():
        db = parse_design_basis(db_path)
        check_design_basis(db, reg, manifests, rep)
        expect = reg.get("design_basis", {}).get("doc_no")
        if db.get("doc_no") and expect and db["doc_no"] != expect:
            rep.err("D1", "design basis",
                    f"nomor {db['doc_no']} != registri {expect}")
    else:
        db = {"equipment": [], "lines": {}, "instruments": []}
        rep.err("T0", "design basis", f"tidak ditemukan: {db_path}")

    failed = bool(rep.errors) or (args.strict and bool(rep.warnings))
    if args.json:
        print(json.dumps({
            "ok": not failed,
            "errors": [f.__dict__ for f in rep.errors],
            "warnings": [f.__dict__ for f in rep.warnings],
            "design_basis": {"equipment": len(db["equipment"]),
                             "lines": len(db["lines"]),
                             "instruments": len(db["instruments"])},
        }, indent=2, ensure_ascii=False))
    else:
        print("=" * 78)
        print("KONSISTENSI DESIGN BASIS <-> DRAWING")
        print("=" * 78)
        print(f"design basis : {db_path.name} ({len(db['equipment'])} equipment, "
              f"{len(db['lines'])} line, {len(db['instruments'])} instrument)")
        print(f"manifest     : {len(manifests)} drawing")
        print("-" * 78)
        for f in rep.errors:
            print(f"[ERROR] {f.rule:<4} {f.subject:<20} {f.message}")
        for f in rep.warnings:
            print(f"[WARN ] {f.rule:<4} {f.subject:<20} {f.message}")
        print("-" * 78)
        print(f"HASIL: {len(rep.errors)} error, {len(rep.warnings)} warning")
        print("KONSISTEN" if not failed else "TIDAK KONSISTEN")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
