"""Ambil log job GitHub Actions yang gagal."""
import json
import sys
import urllib.request
import zipfile
import io
import re

REPO = "arienug20/gas-prod-facility"


def get(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "gpf", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def main():
    runs = get(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=3")
    run = runs["workflow_runs"][0]
    print(f"run: {run['id']} {run['conclusion']}")
    jobs = get(f"https://api.github.com/repos/{REPO}/actions/runs/{run['id']}/jobs")
    job = next((j for j in jobs["jobs"] if "3.13" in j["name"]), jobs["jobs"][0])
    print(f"job: {job['name']} -> {job['conclusion']}")
    print(f"job_id={job['id']}")

    # log zip
    url = f"https://api.github.com/repos/{REPO}/actions/jobs/{job['id']}/logs"
    req = urllib.request.Request(url, headers={"User-Agent": "gpf"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            txt = "\n".join(z.read(n).decode("utf-8", "replace")
                            for n in z.namelist())
    except Exception as exc:
        print("tidak bisa unduh log (butuh token?):", exc)
        return 1

    # cetak bagian relevan
    lines = txt.splitlines()
    keep = []
    for i, ln in enumerate(lines):
        if re.search(r"FAIL|Error|error:|Traceback|Execution failed|##\[error\]|"
                     r"HASIL:|GAGAL:|No such|not found", ln):
            keep.append(i)
    show = set()
    for i in keep:
        for d in range(-1, 4):
            if 0 <= i + d < len(lines):
                show.add(i + d)
    for i in sorted(show):
        print(lines[i][:300])
    return 0


if __name__ == "__main__":
    sys.exit(main())
