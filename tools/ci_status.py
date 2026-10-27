"""Pantau status GitHub Actions untuk repo gas-prod-facility."""
import json
import sys
import time
import urllib.request

REPO = "arienug20/gas-prod-facility"


def get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "gpf-monitor",
                         "Accept": "application/vnd.github+json"},
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # jaringan lambat / rate limit
            last = exc
            if i < tries - 1:
                time.sleep(5 * (i + 1))
    raise SystemExit(f"Gagal menghubungi GitHub API: {last}")


def main():
    runs = get(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=10")
    wf = runs.get("workflow_runs", [])
    if not wf:
        print("Belum ada workflow run untuk repo ini.")
        return 0

    print(f"Total run terlihat: {len(wf)}\n")
    for r in wf[:4]:
        print(f"[{r['name']}] {r['status']}/{r['conclusion']} "
              f"sha={r['head_sha'][:7]} branch={r['head_branch']}")
        print(f"   {r['html_url']}")
        jobs = get(f"https://api.github.com/repos/{REPO}/actions/runs/{r['id']}/jobs")
        for j in jobs.get("jobs", []):
            mark = j["conclusion"] or j["status"]
            print(f"     - {j['name']:<38} {mark}")
            for step in j.get("steps", []):
                if step.get("conclusion") not in (None, "success", "skipped"):
                    print(f"         LANGKAH GAGAL: {step['name']} "
                          f"({step['conclusion']})")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
