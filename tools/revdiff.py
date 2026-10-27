#!/usr/bin/env python3
"""revdiff.py — bandingkan isi drawing antar revisi (dari riwayat git).

Masalah: `dokumen/04-review-log.md` mencatat setiap ronde revisi
(A0 -> A1 -> A2 -> ...) beserta deskripsi perubahannya, tetapi tidak ada
cara otomatis untuk membuktikan APA yang benar-benar berubah pada satu
lembar, dan apakah nomor revisinya ikut naik.

Script ini membandingkan manifest teks (`cad/<sheet>.texts.json`) antara
dua revisi git:

  ADDED    teks baru (fitur/label yang ditambahkan)
  REMOVED  teks hilang (fitur/label yang dibuang)
  MOVED    teks sama, koordinat bergeser > toleransi
  unchanged  teks sama, posisi sama

Penting: di repo ini banyak teks berupa nomor urut grid (1, 2, 3, ...)
dan sel revisi. Pergeseran massal label grid BUKAN perubahan engineering,
sehingga teks bernomor pendek dipisahkan ke bucket "noise" agar tidak
menenggelamkan perubahan yang berarti.

Pemakaian:
    python tools/revdiff.py                           # semua, HEAD~1 -> HEAD
    python tools/revdiff.py pid_v101
    python tools/revdiff.py --all 095ead8 HEAD
    python tools/revdiff.py pid_v101 HEAD~3 HEAD --json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST_DIR = "cad"
MOVE_TOL_MM = 0.5          # ambang pergeseran agar dianggap "dipindah"

# Teks yang dianggap "noise" bila bergeser: nomor/angka pendek & sel revisi.
NOISE_RE = re.compile(r"^(\d{1,3}|[A-Z]\d|[A-Z])$")


@dataclass
class SheetDiff:
    sheet: str
    rev_old: str = ""
    rev_new: str = ""
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    moved: list[tuple[str, float, float]] = field(default_factory=list)
    unchanged: int = 0
    noise_added: int = 0
    noise_removed: int = 0
    noise_moved: int = 0

    @property
    def changed(self) -> bool:
        return bool(self.added or self.removed or self.moved or
                    self.noise_added or self.noise_removed or self.noise_moved)

    @property
    def meaningful(self) -> bool:
        """Perubahan yang bukan sekadar label grid/revisi."""
        return bool(self.added or self.removed or self.moved)


def git(args: list[str]) -> str | None:
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def rev_ok(rev: str) -> bool:
    return git(["rev-parse", "--verify", rev]) is not None


def load_manifest(blob: str) -> list[dict]:
    data = json.loads(blob)
    texts = data["texts"] if isinstance(data, dict) else data
    out = []
    for t in texts:
        if isinstance(t, dict):
            out.append({"t": str(t.get("t", "")).strip(),
                        "x": float(t.get("x", 0.0)),
                        "y": float(t.get("y", 0.0))})
        else:
            out.append({"t": str(t).strip(), "x": 0.0, "y": 0.0})
    return out


def detect_rev(texts: list[dict]) -> str:
    cells = [t["t"] for t in texts if re.fullmatch(r"[A-Z]\d", t["t"])]
    if not cells:
        return ""
    return max(cells, key=lambda c: (ord(c[0]) - 65, int(c[1:])))


def diff_sheet(sheet: str, old: str, new: str) -> SheetDiff | None:
    path = f"{MANIFEST_DIR}/{sheet}.texts.json"
    old_blob = git(["show", f"{old}:{path}"])
    new_blob = git(["show", f"{new}:{path}"])
    if old_blob is None or new_blob is None:
        return None
    old_t, new_t = load_manifest(old_blob), load_manifest(new_blob)

    d = SheetDiff(sheet)
    d.rev_old, d.rev_new = detect_rev(old_t), detect_rev(new_t)

    old_c = Counter(t["t"] for t in old_t)
    new_c = Counter(t["t"] for t in new_t)
    for t, n in (new_c - old_c).items():
        if NOISE_RE.match(t):
            d.noise_added += n
        else:
            d.added.extend([t] * n)
    for t, n in (old_c - new_c).items():
        if NOISE_RE.match(t):
            d.noise_removed += n
        else:
            d.removed.extend([t] * n)

    common = old_c & new_c
    # Teks yang sama bisa muncul LEBIH DARI SEKALI di posisi berbeda
    # (mis. nomor grid 1..12 di tepi atas DAN bawah border). Pemetaan
    # tunggal {teks: posisi} membuang kemunculan kedua sehingga muncul
    # "dipindah" palsu sepanjang tinggi lembar (~572 mm). Karena itu tiap
    # kemunculan dipasangkan ke posisi terdekat yang belum terpakai.
    old_entries: dict[str, list[tuple[float, float]]] = {}
    for t in old_t:
        old_entries.setdefault(t["t"], []).append((t["x"], t["y"]))

    for t in new_t:
        s = t["t"]
        if s not in common:
            continue
        cand = old_entries.get(s)
        if not cand:
            continue
        best = min(cand, key=lambda p: abs(p[0] - t["x"]) + abs(p[1] - t["y"]))
        cand.remove(best)
        dx, dy = t["x"] - best[0], t["y"] - best[1]
        if abs(dx) > MOVE_TOL_MM or abs(dy) > MOVE_TOL_MM:
            if NOISE_RE.match(s):
                d.noise_moved += 1
            else:
                d.moved.append((s, round(dx, 2), round(dy, 2)))
        else:
            d.unchanged += 1
    d.added.sort()
    d.removed.sort()
    return d


def all_sheets() -> list[str]:
    return sorted(f.name.replace(".texts.json", "")
                  for f in (REPO / MANIFEST_DIR).glob("*.texts.json")
                  if not f.name.startswith(("test_", "test_opt")))


def _looks_like_rev(tok: str) -> bool:
    if tok.upper().startswith("HEAD"):
        return True
    if re.fullmatch(r"[0-9a-f]{7,40}", tok):
        return True
    return "~" in tok or "^" in tok


def _is_known_sheet(tok: str) -> bool:
    """Token dianggap nama lembar hanya bila manifest-nya BENAR-BENAR ada.

    Sebelumnya token apa pun yang tidak berpola revisi langsung diperlakukan
    sebagai nama lembar, sehingga revisi salah tulis (mis. "BADREV") diam-diam
    menjadi nama lembar: manifest tidak ditemukan, lalu alat melaporkan
    'tidak ada perubahan' - kesimpulan yang menyesatkan.
    """
    return (REPO / MANIFEST_DIR / f"{tok}.texts.json").is_file()


def _in_git_repo() -> bool:
    """Apakah direktori ini berada dalam repo git yang punya riwayat?"""
    if not (REPO / ".git").exists():
        return False
    return git(["rev-parse", "--is-inside-work-tree"]) is not None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("args", nargs="*", help="[lembar] [old] [new]")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)

    # Tanpa riwayat git, perbandingan revisi TIDAK MUNGKIN dilakukan.
    # Laporkan sebagai "dilewati" (exit 0), bukan gagal: menjalankan dari
    # arsip tanpa .git bukan kesalahan engineering.
    if not _in_git_repo():
        msg = ("riwayat git tidak tersedia — revdiff DILEWATI "
               "(jalankan dari clone git untuk membandingkan revisi)")
        if ns.json:
            print(json.dumps({"skipped": True, "reason": msg}, indent=2))
        else:
            print(msg)
        return 0

    rest = list(ns.args)
    sheet = None
    old, new = "HEAD~1", "HEAD"
    if rest and _is_known_sheet(rest[0]):
        sheet = rest.pop(0)
    elif rest and not _looks_like_rev(rest[0]) and len(rest) == 1:
        # satu argumen yang bukan lembar dan bukan revisi -> kemungkinan
        # nama lembar salah tulis; tetap anggap lembar agar pesannya jelas
        sheet = rest.pop(0)
    if len(rest) >= 2:
        old, new = rest[0], rest[1]
    elif len(rest) == 1:
        new = rest[0]

    # Validasi revisi lebih awal: bila gagal, JANGAN tampilkan diff palsu.
    for rev in (old, new):
        if not rev_ok(rev):
            print(f"revisi tidak dikenal: {rev}", file=sys.stderr)
            return 2

    # Validasi nama lembar: nama yang tidak dikenal harus GAGAL, bukan
    # dilaporkan sebagai "tidak ada perubahan".
    if sheet and not _is_known_sheet(sheet):
        print(f"lembar tidak dikenal: {sheet}", file=sys.stderr)
        return 2

    sheets = all_sheets() if (ns.all or not sheet) else [sheet]
    results, missing = [], []
    for s in sheets:
        d = diff_sheet(s, old, new)
        (results.append(d) if d else missing.append(s))

    # Manifest yang hilang pada salah satu revisi = kesalahan, bukan "diam".
    if missing and not ns.json:
        print(f"manifest tidak ada pada salah satu revisi: {', '.join(missing)}",
              file=sys.stderr)
        return 2

    if ns.json:
        print(json.dumps({
            "old": old, "new": new,
            "sheets": [{
                "sheet": d.sheet, "rev_old": d.rev_old, "rev_new": d.rev_new,
                "added": d.added, "removed": d.removed,
                "moved": [{"text": t, "dx": dx, "dy": dy}
                          for t, dx, dy in d.moved],
                "unchanged": d.unchanged,
                "noise": {"added": d.noise_added, "removed": d.noise_removed,
                          "moved": d.noise_moved},
            } for d in results],
            "missing": missing,
        }, indent=2, ensure_ascii=False))
        return 0

    print("=" * 78)
    print(f"REVISION DIFF  {old} -> {new}")
    print("=" * 78)
    if missing:
        print(f"manifest tidak ada pada salah satu revisi: {', '.join(missing)}")
        print()

    changed = [d for d in results if d.changed]
    if not changed:
        print(f"tidak ada perubahan pada {len(results)} lembar")
        return 0

    meaningful = [d for d in changed if d.meaningful]
    print(f"{len(changed)} dari {len(results)} lembar berubah "
          f"({len(meaningful)} dengan perubahan isi bermakna)\n")
    for d in changed:
        tag = "" if d.meaningful else "  [hanya label grid/revisi]"
        print(f"--- {d.sheet}  [{d.rev_old or '?'} -> {d.rev_new or '?'}]{tag}")
        if d.added:
            print(f"  + {len(d.added)} teks ditambahkan:")
            for t in d.added[:10]:
                print(f"      + {t[:66]}")
            if len(d.added) > 10:
                print(f"      ... ({len(d.added) - 10} lagi)")
        if d.removed:
            print(f"  - {len(d.removed)} teks dihapus:")
            for t in d.removed[:10]:
                print(f"      - {t[:66]}")
            if len(d.removed) > 10:
                print(f"      ... ({len(d.removed) - 10} lagi)")
        if d.moved:
            print(f"  ~ {len(d.moved)} teks dipindah:")
            for t, dx, dy in d.moved[:8]:
                print(f"      ~ {t[:45]:<45} dx={dx:+7.2f} dy={dy:+7.2f}")
            if len(d.moved) > 8:
                print(f"      ... ({len(d.moved) - 8} lagi)")
        if d.noise_added or d.noise_removed or d.noise_moved:
            print(f"  (noise: {d.noise_added} label ditambah, "
                  f"{d.noise_removed} dihapus, {d.noise_moved} dipindah)")
        print(f"  = {d.unchanged} teks tidak berubah")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
