# Models

| Script | Output | Purpose |
| --- | --- | --- |
| piping_3d.py | step/piping_3d.step | Model 3D routing piping + equipment (assembly, mm) |

Build: `python src/piping_3d.py` dari root proyek. Model tidak berubah = no-op.

Renders: `render/render_iso.png` (kamera isometrik), `render/render_top.png`
(cek posisi tampak atas). Folder `cad/` adalah drawing 2D — tidak diubah model ini.

Sumber koordinat: `dokumen/01-design-basis.md` (GPF-00-DB-0001 Rev A0).
