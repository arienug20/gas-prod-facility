"""Build a shareable Windows package from tracked, reusable repository assets."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

root = Path(__file__).resolve().parents[2]
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
paths = [p for p in tracked if p and (p.startswith(('skills/company-cad-standard/', 'skills/skills-patches/dxf-company/', 'tools/')) or p in ('requirements.txt', 'requirements-cadgen.txt', 'DEPENDENCIES.md'))]
paths += ['skills/install/install-windows.ps1', 'skills/install/INSTALL-ENGINEER.md']
paths = sorted(set(paths))
out = root / 'dist' / 'gpf-windows-skills.zip'
out.parent.mkdir(exist_ok=True)
manifest = {'source_revision': revision, 'note': 'Contents reflect working tree; hashes identify exact files.', 'files': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths}}
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
    for p in paths:
        archive.write(root / p, 'gpf-windows/' + p)
    archive.writestr('gpf-windows/manifest.json', json.dumps(manifest, indent=2) + '\n')
print(out)
