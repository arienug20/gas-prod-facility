#!/usr/bin/env python3
"""quality_gate.py — gate mutu deterministik gas-prod-facility.

Satu perintah, satu hasil, dipakai LOKAL dan di CI (GitHub Actions):

    python tools/quality_gate.py              # gate penuh
    python tools/quality_gate.py --lint-only  # hanya sweep linter (cepat)
    python tools/quality_gate.py --json       # keluaran terstruktur

Yang dijalankan:
  1. environment  - versi Python & ketersediaan backend CAD (cadbackend)
  2. lint         - validate_cad_rules.py pada SEMUA *.dxf di cad/
  3. build        - opsional (--build): bangun ulang DXF via backend lalu lint
  4. tests        - pytest bila tersedia

Exit code 0 hanya bila semua langkah wajib lulus. Dirancang agar TIDAK pernah
menggantung: setiap subprocess punya timeout.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAD = REPO / "cad"
LINTER = CAD / "validate_cad_rules.py"

# Drawing yang WAJIB ada & WAJIB lulus (16 sheet paket GPF).
EXPECTED = {
    "pid_v101", "routing_plan", "iso_go1002", "iso_co1003", "iso_co1004",
    "wellhead_demo", "compression_demo", "powergen_demo", "air_system_demo",
    "metering_demo", "lbcv_demo", "underground_demo", "supports_demo",
    "alignment_demo", "pid_recip_booster", "pid_centrifugal",
}

# File kerja/sisa yang tidak boleh ikut di-gate (dan sebaiknya tidak di-commit).
IGNORE_PREFIXES = ("test_opt", "test_drawing", "test_pid_common")


def step_hygiene() -> Result:
    """Laporkan artefak yang seharusnya tidak di-commit.

    Gate tidak gagal karena file ini (bisa jadi sengaja ada saat debug),
    tetapi engineer diberi tahu supaya tidak menumpuk diam-diam di repo.
    """
    t0 = time.perf_counter()
    stray = sorted(p.name for p in CAD.glob("*.dxf")
                   if p.name.startswith(IGNORE_PREFIXES))
    big = sorted(f"{p.name} ({p.stat().st_size // 1024} KB)"
                 for p in CAD.glob("*.dxf") if p.stat().st_size > 400 * 1024)
    parts = []
    if stray:
        parts.append(f"file kerja diabaikan: {', '.join(stray)}")
    if big:
        parts.append(f"DXF besar (>400 KB): {', '.join(big)}")
    return Result("hygiene", True, "; ".join(parts) or "bersih",
                  warnings=stray, seconds=time.perf_counter() - t0)


@dataclass
class Result:
    name: str
    ok: bool
    detail: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    seconds: float = 0.0


def _run(cmd, cwd=None, timeout=600):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout)


def step_environment() -> Result:
    t0 = time.perf_counter()
    detail = [f"python {sys.version.split()[0]} ({sys.executable})"]
    ok = True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from cadbackend import resolve  # noqa: PLC0415
        be = resolve(need="build")
        detail.append(be.summary())
        detail.extend(f"note: {n}" for n in be.notes)
    except Exception as exc:
        detail.append(f"backend: TIDAK ADA ({exc})")
        ok = False
    try:
        import ezdxf  # noqa: F401, PLC0415
        detail.append(f"ezdxf {ezdxf.__version__}")
    except ImportError:
        detail.append("ezdxf: TIDAK TERPASANG")
        ok = False
    return Result("environment", ok, "\n".join(detail),
                  seconds=time.perf_counter() - t0)


def _dxf_files() -> list[Path]:
    return sorted(p for p in CAD.glob("*.dxf")
                  if not p.name.startswith(IGNORE_PREFIXES))


def step_lint(mode: str | None = None) -> list[Result]:
    results: list[Result] = []
    if not LINTER.is_file():
        return [Result("lint", False, f"linter tidak ditemukan: {LINTER}")]
    for dxf in _dxf_files():
        t0 = time.perf_counter()
        manifest = dxf.with_suffix(".texts.json").name
        man = CAD / manifest
        cmd = [sys.executable, str(LINTER), str(dxf)]
        if man.is_file():
            cmd.append(str(man))
        try:
            r = _run(cmd, cwd=CAD, timeout=900)
        except subprocess.TimeoutExpired:
            results.append(Result(f"lint:{dxf.name}", False, "TIMEOUT",
                                  seconds=time.perf_counter() - t0))
            continue
        out = r.stdout or ""
        errs = [ln.strip() for ln in out.splitlines() if "[ERROR]" in ln]
        warns = [ln.strip() for ln in out.splitlines() if "[WARN]" in ln]
        status = next((ln.strip() for ln in out.splitlines()
                       if ln.startswith("Status:")), "(tanpa status)")
        ok = r.returncode == 0 and "Status: PASS" in out
        results.append(Result(f"lint:{dxf.stem}", ok, status, errs, warns,
                              time.perf_counter() - t0))
    return results


def step_build() -> list[Result]:
    """Bangun ulang DXF lalu jalankan apply_text.py (rantai build lengkap).

    URUTAN WAJIB sesuai AGENTS.md §2:
        build -> apply_text.py (MTEXT + DIM + SOLID + pens) -> validasi
    Tanpa apply_text.py, Check 3 (lineweight) dan Check 2 (MTEXT) pasti gagal.
    """
    shim = REPO / "cadshim.py"
    if not shim.is_file():
        return [Result("build", False, "cadshim.py tidak ditemukan "
                                       "(lewati: tidak ada backend build)")]
    results = []
    for name in sorted(EXPECTED):
        src = CAD / f"{name}.py"
        if not src.is_file():
            results.append(Result(f"build:{name}", False, "skrip sumber tidak ada"))
            continue
        t0 = time.perf_counter()
        out_dxf = CAD / f"{name}.dxf"
        try:
            r = _run([sys.executable, str(shim), str(src), str(out_dxf)], cwd=CAD)
        except subprocess.TimeoutExpired:
            results.append(Result(f"build:{name}", False, "TIMEOUT"))
            continue
        tail = (r.stdout or r.stderr).strip().splitlines()
        if r.returncode != 0:
            results.append(Result(f"build:{name}", False,
                                  tail[-1] if tail else "build gagal"))
            continue

        # --- RANTAI BUILD: apply_text.py (jangan dilewati) ------------------
        man = CAD / f"{name}.texts.json"
        if not man.is_file():
            results.append(Result(f"build:{name}", False,
                                  "manifest .texts.json tidak dihasilkan"))
            continue
        try:
            a = _run([sys.executable, str(_apply_text_hub()), str(out_dxf),
                      str(man)], cwd=CAD)
        except subprocess.TimeoutExpired:
            results.append(Result(f"build:{name}", False, "apply_text TIMEOUT"))
            continue
        if a.returncode != 0:
            atail = (a.stdout or a.stderr).strip().splitlines()
            results.append(Result(f"build:{name}", False,
                                  f"apply_text gagal: {atail[-1] if atail else ''}"))
            continue
        results.append(Result(f"build:{name}", True,
                              "build + apply_text OK",
                              seconds=time.perf_counter() - t0))
    return results


def _apply_text_hub() -> Path:
    """Skrip kecil: pasang shim cadgen lalu jalankan cad/apply_text.py apa adanya.

    apply_text.py mengimpor `cadgen.drawing_checks`; hub ini menyediakan modul
    tersebut dari cadshim sehingga rantai build tidak bergantung pada cadgen.
    """
    hub = Path(tempfile.mkdtemp(prefix="gpf-gate-")) / "_apply_text_hub.py"
    hub.write_text(
        "import runpy, sys\n"
        f"sys.path.insert(0, r'{REPO}')\n"
        "import cadshim; cadshim.install()\n"
        "sys.argv = ['apply_text.py', sys.argv[1], sys.argv[2]]\n"
        f"sys.path.insert(0, r'{CAD}')\n"
        f"runpy.run_path(r'{CAD / 'apply_text.py'}', run_name='__main__')\n",
        encoding="utf-8")
    return hub


def step_tests() -> Result:
    if not shutil.which(sys.executable):
        return Result("tests", False, "interpreter hilang")
    has_pytest = _run([sys.executable, "-c", "import pytest"]).returncode == 0
    if not has_pytest:
        return Result("tests", True, "pytest tidak terpasang (DILEWATI)")
    t0 = time.perf_counter()
    try:
        r = _run([sys.executable, "-m", "pytest", "-q", "--no-header",
                  str(CAD), str(REPO / "tests")], cwd=REPO, timeout=1800)
    except subprocess.TimeoutExpired:
        return Result("tests", False, "TIMEOUT")
    tail = (r.stdout or r.stderr).strip().splitlines()
    detail = " | ".join(tail[-3:]) if tail else ""
    return Result("tests", r.returncode == 0, detail,
                  seconds=time.perf_counter() - t0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lint-only", action="store_true", help="hanya sweep linter")
    ap.add_argument("--build", action="store_true", help="bangun ulang DXF dulu")
    ap.add_argument("--json", action="store_true", help="keluaran JSON")
    ap.add_argument("--strict-warnings", action="store_true",
                    help="warning dianggap gagal")
    args = ap.parse_args(argv)

    results: list[Result] = []
    results.append(step_environment())
    results.append(step_hygiene())
    if args.build and not args.lint_only:
        results.extend(step_build())
    results.extend(step_lint())
    if not args.lint_only:
        results.append(step_tests())

    # --- verifikasi cakupan: 16 sheet wajib ada -----------------------------
    present = {r.name.split(":", 1)[1] for r in results if r.name.startswith("lint:")}
    missing = EXPECTED - present
    if missing:
        results.append(Result("coverage", False,
                              f"drawing wajib tidak ditemukan: {sorted(missing)}"))

    if args.strict_warnings:
        for r in results:
            if r.warnings and r.ok:
                r.ok = False
                r.detail += " (warning diperlakukan sebagai error)"

    failed = [r for r in results if not r.ok]
    total_s = sum(r.seconds for r in results)

    if args.json:
        print(json.dumps({
            "ok": not failed,
            "total_seconds": round(total_s, 1),
            "results": [asdict(r) for r in results],
        }, indent=2, ensure_ascii=False))
    else:
        print("=" * 78)
        print("GPF QUALITY GATE")
        print("=" * 78)
        for r in results:
            mark = "PASS" if r.ok else "FAIL"
            print(f"[{mark}] {r.name:<26} {r.seconds:6.2f}s  {r.detail}")
            for e in r.errors:
                print(f"          {e}")
        print("-" * 78)
        npass = sum(1 for r in results if r.ok)
        print(f"HASIL: {npass}/{len(results)} lulus  ({total_s:.1f}s)")
        if failed:
            print("GAGAL:", ", ".join(r.name for r in failed))
        else:
            print("SEMUA GATE LULUS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
