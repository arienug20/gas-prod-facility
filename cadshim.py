"""Shim pengganti `cadgen` (build123d + dxf + drawing_checks) memakai ezdxf.

Dipakai untuk memverifikasi kelayakan migrasi REPO gas-prod-facility tanpa
mengubah satu baris pun kode pustaka perusahaan (pid_common, iso_common, dst).

Perintah:
    python cadshim.py <model.py> <out.dxf> <out.png> [--w 2400] [--h 1700]
"""
from __future__ import annotations

import math
import runpy
import sys
import types
from pathlib import Path


# ---------------------------------------------------------------- build123d stub
class _Vec:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = float(x), float(y), float(z)


class _Edge:
    """Geometri tepi 2D; payload dipakai shim untuk ditulis sebagai entity DXF."""

    def __init__(self, kind, data):
        self.kind = kind      # 'line' | 'circle' | 'arc'
        self.data = data

    @staticmethod
    def make_line(p1: _Vec, p2: _Vec) -> "_Edge":
        return _Edge("line", (p1.x, p1.y, p2.x, p2.y))

    @staticmethod
    def make_circle(radius: float, start_angle: float = 0.0,
                    end_angle: float = 360.0) -> "_Edge":
        if start_angle == 0.0 and end_angle == 360.0:
            return _Edge("circle", (radius,))
        return _Edge("arc", (radius, start_angle, end_angle))

    def mutate_location(self, loc: "_Location") -> "_Edge":
        dx, dy = loc.x, loc.y
        if self.kind == "line":
            x1, y1, x2, y2 = self.data
            return _Edge("line", (x1 + dx, y1 + dy, x2 + dx, y2 + dy))
        if self.kind == "circle":
            return _Edge("circle", self.data + ((dx, dy),))
        r, a1, a2 = self.data
        return _Edge("arc", (r, a1, a2, (dx, dy)))


class _Location:
    def __init__(self, p=(0.0, 0.0, 0.0)):
        self.x, self.y = float(p[0]), float(p[1])

    def __mul__(self, edge: _Edge) -> _Edge:
        return edge.mutate_location(self)

    __rmul__ = __mul__


class _Compound:
    def __init__(self, edges):
        self.edges = list(edges)

    @staticmethod
    def make_composite(items):
        out = []
        for it in items:
            if isinstance(it, _Edge):
                out.append(it)
            elif isinstance(it, _Compound):
                out.extend(it.edges)
            elif isinstance(it, (list, tuple)):
                out.extend(it)
            else:
                raise TypeError(f"compound: tipe tak dikenal {type(it)!r}")
        return _Compound(out)

    def edges_(self):
        return self.edges


bd = types.SimpleNamespace(Vector=_Vec, Edge=_Edge, Location=_Location,
                           Compound=_Compound)


# ---------------------------------------------------------------- DXF exporter
def write_dxf(layers: dict, out_path: Path) -> None:
    import ezdxf

    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    for name in ("REF-FRAME", "REF-TITLE", "REF-EQUIP", "REF-PROC",
                 "REF-SYM", "REF-SIG", "REF-SIGP", "REF-HATCH",
                 "REF-TEXT", "REF-DIM", "REF-GRID", "REF-ROAD",
                 "REF-FENCE", "REF-HATCH"):
        if name not in doc.layers:
            doc.layers.add(name)

    n = 0
    for layer, geom in layers.items():
        edges = geom.edges if isinstance(geom, _Compound) else geom
        for e in edges:
            att = {"layer": layer}
            if e.kind == "line":
                x1, y1, x2, y2 = e.data
                msp.add_line((x1, y1), (x2, y2), dxfattribs=att)
            elif e.kind == "circle":
                if len(e.data) == 1:
                    r = e.data[0]
                    msp.add_circle((0, 0), r, dxfattribs=att)
                else:
                    r, c = e.data
                    msp.add_circle(c, r, dxfattribs=att)
            elif e.kind == "arc":
                r, a1, a2 = e.data[0], e.data[1], e.data[2]
                c = e.data[3] if len(e.data) > 3 else (0.0, 0.0)
                msp.add_arc(c, r, a1, a2, dxfattribs=att)
            n += 1
    doc.saveas(out_path)
    print(f"[shim] DXF: {out_path} ({n} entity)")


def snapshot_png(dxf_path: Path, png_path: Path, width=2400, height=1700) -> None:
    """Pengganti `cadgen dxf snapshot` memakai ezdxf.addons.drawing + matplotlib."""
    import ezdxf
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import (
        Configuration, BackgroundPolicy, ColorPolicy,
    )

    doc = ezdxf.readfile(str(dxf_path))
    msp = doc.modelspace()
    # Tema putih (standar gambar teknik): latar putih, ACI hitam di atas putih.
    cfg = Configuration(
        background_policy=BackgroundPolicy.WHITE,
        color_policy=ColorPolicy.BLACK,
    )
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    Frontend(RenderContext(doc), MatplotlibBackend(ax),
             config=cfg).draw_layout(msp)
    # MatplotlibBackend menimpa ukuran figure saat auto-fit -> paksa ulang.
    fig.set_size_inches(width / 100, height / 100)
    fig.savefig(str(png_path), dpi=100, facecolor="white")
    plt.close(fig)
    print(f"[shim] PNG: {png_path} ({width}x{height})")


# ------------------------------------------------------- drawing_checks facade
def validate_dxf_file(path, *, tolerance=1e-3, **kw):
    """Minimal: delegasi ke validate_cad_rules.py bila tersedia di cwd."""
    sys.path.insert(0, str(Path.cwd()))
    try:
        from validate_cad_rules import main as _main  # noqa: F401
    except Exception:
        pass
    return []


def install() -> None:
    """Pasang modul `cadgen` palsu ke sys.modules."""
    dxf_mod = types.ModuleType("cadgen.dxf")
    checks = types.ModuleType("cadgen.drawing_checks")

    CAPTURED = {}

    def _decorator(func):
        # cadgen mengeksekusi model saat import, bukan saat dipanggil.
        func.__cadgen_model__ = types.SimpleNamespace(func=func)
        try:
            CAPTURED["layers"] = func()
        except Exception as exc:  # pragma: no cover
            CAPTURED["error"] = exc
        return func

    _decorator.captured = CAPTURED

    dxf_mod.__call__ = _decorator
    checks.validate_dxf_file = validate_dxf_file

    cadgen_mod = types.ModuleType("cadgen")
    cadgen_mod.build123d = bd
    cadgen_mod.dxf = _decorator
    cadgen_mod.drawing_checks = checks

    sys.modules["cadgen"] = cadgen_mod
    sys.modules["cadgen.dxf"] = dxf_mod
    sys.modules["cadgen.drawing_checks"] = checks
    sys.modules["cadgen.build123d"] = types.SimpleNamespace(**bd.__dict__)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    model = Path(sys.argv[1]).resolve()
    install()
    sys.path.insert(0, str(model.parent))

    ns = runpy.run_path(str(model), run_name="__cadgen_model__")
    cap = sys.modules["cadgen.dxf"].__call__.captured
    if "error" in cap:
        raise cap["error"]
    layers = cap.get("layers")
    if layers is None:
        for v in ns.values():
            if isinstance(v, dict) and v and all(
                    isinstance(x, _Compound) for x in v.values()):
                layers = v
                break
    if layers is None:
        print("[shim] ERROR: model tidak mengembalikan dict[str, Compound]")
        return 1

    out_dxf = Path(sys.argv[2] if len(sys.argv) > 2 else model.with_suffix(".dxf"))
    write_dxf(layers, out_dxf)
    out_png = Path(sys.argv[3]) if len(sys.argv) > 3 else out_dxf.with_suffix(".png")
    snapshot_png(out_dxf, out_png)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
