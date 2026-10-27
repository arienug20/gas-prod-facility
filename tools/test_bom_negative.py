"""Uji negatif bom_extract: BOM yang salah HARUS terdeteksi (exit 1)."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(repo):
    r = subprocess.run([sys.executable, str(repo / "tools" / "bom_extract.py")],
                       capture_output=True, text=True, cwd=repo)
    return r.returncode, r.stdout


def fresh_copy():
    dst = Path(tempfile.mkdtemp(prefix="gpf-bomneg-")) / "repo"
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", "*.png"))
    return dst


def set_bom_qty(repo: Path, sheet: str, new_qty: str):
    """Ubah kuantitas baris elbow pertama pada lembar iso."""
    import ezdxf
    p = repo / "cad" / f"{sheet}.dxf"
    doc = ezdxf.readfile(str(p))
    msp = doc.modelspace()
    texts = list(msp.query("MTEXT"))
    # cari baris BOM elbow: kolom NO (x 272..277)
    for t in texts:
        if not (272 <= t.dxf.insert.x <= 277):
            continue
        y = t.dxf.insert.y
        desc = next((s for s in texts if abs(s.dxf.insert.y - y) < 0.6
                     and 276 <= s.dxf.insert.x <= 300), None)
        if desc and "ELL" in desc.text.upper():
            qty = next((s for s in texts if abs(s.dxf.insert.y - y) < 0.6
                        and 340 <= s.dxf.insert.x <= 360), None)
            if qty:
                qty.text = f"{new_qty} EA"
                doc.saveas(str(p))
                return True
    return False


def main():
    total = ok = 0

    # 1. baseline: repo bersih harus exit 0
    total += 1
    code, out = run(REPO)
    status = "PASS" if code == 0 else "FAIL"
    ok += status == "PASS"
    print(f"[{status}] {'baseline repo bersih (harus exit 0)':<48} exit={code}")

    cases = [
        ("elbow BOM terlalu sedikit (go1002: 4 -> 3)", "iso_go1002", "3"),
        ("elbow BOM terlalu banyak (co1004: 9 -> 12)", "iso_co1004", "12"),
        ("elbow BOM di-nol-kan (co1003: 2 -> 0)", "iso_co1003", "0"),
    ]
    for label, sheet, new_qty in cases:
        total += 1
        repo = fresh_copy()
        try:
            if not set_bom_qty(repo, sheet, new_qty):
                print(f"[FAIL] {label:<48} baris BOM tidak ditemukan")
                continue
            code, out = run(repo)
            hit = any(ln.startswith("[ERROR]") for ln in out.splitlines())
            status = "PASS" if (code == 1 and hit) else "FAIL"
            ok += status == "PASS"
            detail = next((ln.strip() for ln in out.splitlines()
                           if ln.startswith("[ERROR]")), "-")
            print(f"[{status}] {label:<48} exit={code} {detail[:60]}")
        finally:
            shutil.rmtree(repo.parent, ignore_errors=True)

    print("-" * 72)
    print(f"HASIL NEGATIVE TEST BOM: {ok}/{total}")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
