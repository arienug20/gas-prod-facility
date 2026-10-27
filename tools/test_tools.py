"""Uji: title block, revdiff, export_xlsx harus bereaksi pada input rusak."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(script, *args, cwd=None):
    r = subprocess.run([sys.executable, str((cwd or REPO) / "tools" / script),
                        *args], capture_output=True, text=True, cwd=cwd or REPO,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return r.returncode, r.stdout + r.stderr


def fresh():
    dst = Path(tempfile.mkdtemp(prefix="gpf-tools-")) / "repo"
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(
        ".git", "*.png", "dist", "__pycache__"))
    return dst


def main():
    total = ok = 0

    def case(label, fn):
        nonlocal total, ok
        total += 1
        try:
            passed, detail = fn()
        except Exception as exc:
            passed, detail = False, f"exception: {exc}"
        ok += passed
        print(f"[{'PASS' if passed else 'FAIL'}] {label:<52} {detail[:50]}")

    # ---- baseline
    case("titleblock: repo bersih exit 0",
         lambda: (run("titleblock_check.py")[0] == 0,
                  "ok" if run("titleblock_check.py")[0] == 0 else "gagal"))

    def tb_missing_field():
        repo = fresh()
        m = repo / "cad" / "pid_v101.texts.json"
        d = json.loads(m.read_text(encoding="utf-8"))
        # Lembar ini memuat 7 bentuk tanggal (riwayat revisi + tanggal terbit).
        # Menghapus sebagian saja membuat test tidak representatif.
        import re
        date_re = re.compile(
            r"\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)"
            r"\s+\d{2,4}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}", re.I)
        before = len(d["texts"])
        d["texts"] = [t for t in d["texts"] if not date_re.search(t["t"])]
        removed = before - len(d["texts"])
        m.write_text(json.dumps(d, indent=2), encoding="utf-8")
        code, out = run("titleblock_check.py", cwd=repo)
        shutil.rmtree(repo.parent, ignore_errors=True)
        return code == 1 and "date_of_issue" in out, f"{removed} teks dihapus"
    case("titleblock: tanggal dihapus -> exit 1", tb_missing_field)

    def tb_dup_docno():
        repo = fresh()
        p = repo / "tools" / "documents.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["documents"][0]["sheet"] = "A3"   # registri salah ukuran
        p.write_text(json.dumps(d, indent=2), encoding="utf-8")
        code, out = run("titleblock_check.py", cwd=repo)
        shutil.rmtree(repo.parent, ignore_errors=True)
        return code == 1 and "ukuran lembar" in out, "ukuran registri salah"
    case("titleblock: ukuran registri salah -> exit 1", tb_dup_docno)

    # ---- revdiff
    # Kasus revdiff hanya bermakna bila ada riwayat git. Pada arsip tanpa
    # .git, revdiff sengaja melewati (exit 0) dan kasus ini tidak dinilai.
    has_git = (REPO / ".git").exists()

    if has_git:
        case("revdiff: rentang sama -> exit 0",
             lambda: (run("revdiff.py", "--all", "HEAD", "HEAD")[0] == 0, "ok"))
        case("revdiff: revisi salah -> exit 2",
             lambda: (run("revdiff.py", "--all", "BOGUS", "HEAD")[0] == 2,
                      "ditolak"))
        case("revdiff: lembar salah -> exit 2",
             lambda: (run("revdiff.py", "lembar_palsu")[0] == 2, "ditolak"))
    else:
        case("revdiff: tanpa git -> dilewati (exit 0)",
             lambda: (run("revdiff.py", "--all")[0] == 0
                      and "DILEWATI" in run("revdiff.py", "--all")[1],
                      "dilewati dengan benar"))

    # ---- export_xlsx
    def xlsx_ok():
        repo = fresh()
        code, out = run("export_xlsx.py", "-o", str(repo / "dist" / "t.xlsx"),
                        cwd=repo)
        exists = (repo / "dist" / "t.xlsx").is_file()
        shutil.rmtree(repo.parent, ignore_errors=True)
        return code == 0 and exists, "berkas dibuat" if exists else "tidak ada"
    case("export_xlsx: menghasilkan berkas", xlsx_ok)

    def xlsx_content():
        from openpyxl import load_workbook
        repo = fresh()
        out_p = repo / "dist" / "t.xlsx"
        run("export_xlsx.py", "-o", str(out_p), cwd=repo)
        wb = load_workbook(out_p)
        need = {"BOM per Lembar", "Komponen Gabungan", "Line List",
                "Instrument Index", "Equipment Register", "Register Dokumen"}
        got = set(wb.sheetnames)
        # minimal ada baris data
        rows = wb["BOM per Lembar"].max_row - 1
        shutil.rmtree(repo.parent, ignore_errors=True)
        return need <= got and rows > 0, f"{len(got)} sheet, {rows} baris BOM"
    case("export_xlsx: sheet & data lengkap", xlsx_content)

    print("-" * 72)
    print(f"HASIL TOOLS TEST: {ok}/{total}")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
