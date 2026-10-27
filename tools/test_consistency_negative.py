"""Uji negatif: validator konsistensi HARUS mendeteksi kerusakan yang disuntikkan."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(r"C:\Users\Reka Elang\AppData\Local\Temp\gas-prod-facility")
TOOLS = REPO / "tools"


def run(cwd):
    r = subprocess.run([sys.executable, str(Path(cwd) / "tools" / "consistency_check.py")],
                       capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout


def fresh_copy():
    dst = Path(tempfile.mkdtemp(prefix="gpf-neg-")) / "repo"
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", "*.png"))
    return dst


def patch_json(path: Path, fn):
    d = json.loads(path.read_text(encoding="utf-8"))
    fn(d if isinstance(d, dict) else d)
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


CASES = []


def case(name, expect_rule):
    def deco(fn):
        CASES.append((name, expect_rule, fn))
        return fn
    return deco


@case("D2: nomor dokumen ganda", "D2")
def _(repo):
    p = repo / "tools" / "documents.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["documents"][1]["doc_no"] = d["documents"][0]["doc_no"]  # PLN-0002 -> PID-0001
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")


@case("D1: doc no title block salah", "D1")
def _(repo):
    m = repo / "cad" / "wellhead_demo.texts.json"
    d = json.loads(m.read_text(encoding="utf-8"))
    for t in d["texts"]:
        if t["t"] == "GPF-00-PI-PID-0011":
            t["t"] = "GPF-00-PI-PID-9999"
    m.write_text(json.dumps(d, indent=2), encoding="utf-8")


@case("R2: celah revisi (A0,A1,A3)", "R2")
def _(repo):
    m = repo / "cad" / "pid_recip_booster.texts.json"
    d = json.loads(m.read_text(encoding="utf-8"))
    d["texts"].append({"t": "A3", "x": 1, "y": 1, "h": 2, "rot": 0,
                       "layer": "REF-TITLE", "att": 5})
    for t in d["texts"]:
        if t["t"] == "A0":
            t["t"] = "A0"
    m.write_text(json.dumps(d, indent=2), encoding="utf-8")


@case("R1: deklarasi REV tidak cocok", "R1")
def _(repo):
    m = repo / "cad" / "pid_centrifugal.texts.json"
    d = json.loads(m.read_text(encoding="utf-8"))
    for t in d["texts"]:
        if t["t"].startswith("REV:"):
            t["t"] = "REV: A7"
            break
    m.write_text(json.dumps(d, indent=2), encoding="utf-8")


@case("T1: tag equipment hilang dari P&ID", "T1")
def _(repo):
    m = repo / "cad" / "pid_v101.texts.json"
    d = json.loads(m.read_text(encoding="utf-8"))
    d["texts"] = [t for t in d["texts"] if "V-101" not in t["t"]]
    m.write_text(json.dumps(d, indent=2), encoding="utf-8")


@case("T2: DN salah untuk line di drawing", "T2")
def _(repo):
    m = repo / "cad" / "pid_v101.texts.json"
    d = json.loads(m.read_text(encoding="utf-8"))
    for t in d["texts"]:
        if t["t"] == "100-PF-1001 DN150":
            t["t"] = "100-PF-1001 DN100"
    m.write_text(json.dumps(d, indent=2), encoding="utf-8")


@case("D3: manifest tanpa entri registri", "D3")
def _(repo):
    m = repo / "cad" / "supports_demo.texts.json"
    shutil.copy(m, repo / "cad" / "orphan_drawing.texts.json")


def main():
    total = ok = 0
    for name, expect, fn in CASES:
        total += 1
        repo = fresh_copy()
        try:
            fn(repo)
            code, out = run(repo)
            hit = f"[ERROR] {expect}" in out
            status = "PASS" if (code == 1 and hit) else "FAIL"
            if status == "PASS":
                ok += 1
            detail = next((ln.strip() for ln in out.splitlines()
                           if ln.startswith(f"[ERROR] {expect}")), "-")
            print(f"[{status}] {name:<40} exit={code} {detail[:70]}")
        finally:
            shutil.rmtree(repo.parent, ignore_errors=True)

    # baseline: repo bersih harus lolos
    total += 1
    code, out = run(REPO)
    status = "PASS" if code == 0 else "FAIL"
    if status == "PASS":
        ok += 1
    print(f"[{status}] {'baseline repo bersih (harus exit 0)':<40} exit={code}")

    print("-" * 70)
    print(f"HASIL NEGATIVE TEST: {ok}/{total}")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
