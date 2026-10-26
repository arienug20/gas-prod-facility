"""Reusable Instrument & Utility Air System Symbol Library (air_system_common.py).

Versi 1.0.0 (Modul Udara Instrumen & Utilitas — GPF-00-PM-PLN-0008 Bagian III.2).

Standar acuan:
  - ISO 8573-1 (Udara tekan — kelas kemurnian; Class 1.2.1, PDP <= -40 C)
  - ISA-7.0.01 (Quality Standard for Instrument Air)
  - ASME Sec. VIII Div. 1 (Air receiver — bejana tekan)
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Graphical symbols for chemical & petrochemical industry)

Mewarisi pid_common.PIDContext: primitif garis, katup, instrumen, panah aliran,
auto-trimming pipe_run_h/pipe_run_v, manifest TEXTS/SOLIDS, dan layer REF-*
dipakai apa adanya agar 100% konsisten dengan P&ID lain proyek GPF.

Komponen khas sistem udara tekan (semua simbol "self-connected" — setiap ujung
garis menempel pada entitas lain sehingga lulus Check 6 dangling endpoints):
  1.  compressor_screw      — paket rotary screw (casing + 2 rotor heliks + motor M + skid)
  2.  aftercooler_h         — aftercooler inline (shell + zigzag tube + CW in/out)
  3.  moisture_trap_cyclone — pemisah kondensat siklon + auto drain
  4.  air_receiver_v        — receiver vertikal ASME VIII (kaki, pondasi, auto drain)
  5.  filter_body_h         — filter inline (intake/pre/coalescer/dust) + auto drain
  6.  desiccant_tower       — menara desiccant twin-tower (bed berarsir 45 deg)
  7.  plc_timer             — kotak PLC timer penukar menara pengering
  8.  control_valve_v       — control valve vertikal (dome actuator samping)
  9.  priority_valve_v      — PCV priority sustaining valve (menutup UA < 5.5 barg)
  10. switching_valve_v     — katup pengalih menara (ter-daftar ke schedule MTO)
  11. auto_drain_v          — auto drain trap (float) + cap
  12. orifice_plate_v       — pelat orifice purge (FO) untuk pipa vertikal
  13. muffler_vent_h / vent_cap_h — ventilasi/relief ke atmosfer
  14. head_circle/dome_y_at — utilitas head elipsoidal untuk nozzle tembus kepala
"""

from __future__ import annotations

import math

from cadgen import build123d as bd

from pid_common import (
    PIDContext,
    arc,
    arc3,
    circle,
    dashed,
    hatch45,
    line,
    rect,
)


# =============================================================================
# UTILITAS GEOMETRI HEAD ELIPSOIDAL (untuk nozzle yang menembus kepala bejana)
# =============================================================================
def head_circle(p1: tuple[float, float], pm: tuple[float, float], p2: tuple[float, float]):
    """Lingkaran (cx, cy, r) melalui 3 titik head bejana (sama dengan math arc3)."""
    ax, ay = p1
    bx, by = pm
    cx, cy = p2
    d1x, d1y = bx - ax, by - ay
    d2x, d2y = cx - ax, cy - ay
    e1 = (bx * bx + by * by) - (ax * ax + ay * ay)
    e2 = (cx * cx + cy * cy) - (ax * ax + ay * ay)
    det = d1x * d2y - d2x * d1y
    if abs(det) < 1e-9:
        return ((ax + cx) / 2.0, (ay + cy) / 2.0, 1.0)
    ux = (e1 * d2y - e2 * d1y) / (2.0 * det)
    uy = (d1x * e2 - d2x * e1) / (2.0 * det)
    return (ux, uy, math.hypot(ax - ux, ay - uy))


def dome_y_at(x: float, circ: tuple[float, float, float], upper: bool = True) -> float:
    """Ordinat lengkung head pada absis x (upper=True untuk kepala atas)."""
    cx, cy, r = circ
    dx2 = r * r - (x - cx) ** 2
    if dx2 < 0.0:
        dx2 = 0.0
    dy = math.sqrt(dx2)
    return cy + dy if upper else cy - dy


def chord(cx: float, cy: float, r: float, a1: float, a2: float) -> bd.Edge:
    """Tali busur lingkaran — kedua ujung tepat ON keliling (aman Check 6)."""
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy + r * math.sin(math.radians(a1))
    x2 = cx + r * math.cos(math.radians(a2))
    y2 = cy + r * math.sin(math.radians(a2))
    return line(x1, y1, x2, y2)


# =============================================================================
# KELAS KONTEKS SISTEM UDARA (AirSystemContext)
# =============================================================================
class AirSystemContext(PIDContext):
    """Konteks P&ID Sistem Udara Instrumen & Utilitas (ISO 8573-1 / ISA-7.0.01).

    Mewarisi seluruh primitif PIDContext (teks manifest MTEXT ARIAL, panah
    aliran SOLID, katup, bubble instrumen, pipe_run auto-trim, export manifest).
    """

    # -------------------------------------------------------------------------
    # AUTO DRAIN TRAP (FLOAT) — stub + bodi bulat + cap
    # -------------------------------------------------------------------------
    def auto_drain_v(self, x: float, y_top: float, arrow: bool = False) -> list[bd.Edge]:
        """Auto drain condensate trap vertikal dari titik (x, y_top) ke bawah.

        Stub 6 mm -> bodi float r=2.5 -> stub -> cap 6 mm. Semua ujung terhubung.
        """
        out = [
            line(x, y_top, x, y_top - 6.0),
            circle(x, y_top - 8.5, 2.5),
            line(x, y_top - 11.0, x, y_top - 15.0),
            line(x - 3.0, y_top - 15.0, x + 3.0, y_top - 15.0),
        ]
        self.proc += out
        if arrow:
            self.flow_arrow_v(x, y_top - 3.0, direction=-1, size=2.0)
        return out

    # -------------------------------------------------------------------------
    # FILTER INLINE (INTAKE / PRE-FILTER / COALESCER / DUST FILTER)
    # -------------------------------------------------------------------------
    def filter_body_h(
        self,
        cx: float,
        cy: float,
        w: float = 26.0,
        h: float = 14.0,
        tag: str = "",
        desc: str = "",
        drain: bool = False,
    ) -> list[bd.Edge]:
        """Bodi filter inline horizontal: kapsul tertutup + mesh diagonal.

        Pipa proses diarahkan BERAKHIRI pada dinding kiri/kanan bodi (lihat
        demo) sehingga tidak ada garis menembus simbol. Tag di atas bodi
        (2.5 mm, kategori equipment) + deskripsi (1.8 mm).
        """
        hw, hh = w / 2.0, h / 2.0
        x0, x1 = cx - hw, cx + hw
        y0, y1 = cy - hh, cy + hh
        out = rect(x0, y0, x1, y1)
        n = max(2, int(w / 4.5))
        for k in range(1, n):
            xs = x0 + w * k / n
            out.append(line(xs, y0, min(xs + hh, x1), y1))
        self.proc += out
        if drain:
            self.auto_drain_v(cx, y0)
        if tag:
            self.text(tag, cx, y1 + 5.2, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "INLINE FILTER (PARTICULATE / COALESCING / DUST)",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        if desc:
            self.text(desc, cx, y1 + 10.6, size=1.8)
        return out

    # -------------------------------------------------------------------------
    # PAKET KOMPRESOR ROTARY SCREW + FILTER HISAP + MOTOR
    # -------------------------------------------------------------------------
    def compressor_screw(
        self,
        cx: float,
        cy: float,
        tag: str = "K-501",
        desc: str = "ROTARY SCREW AIR COMPRESSOR (OIL-FREE)",
        motor_up: bool = True,
    ) -> list[bd.Edge]:
        """Paket kompresor rotary screw: casing + 2 rotor heliks + motor 'M'.

        Casing 45x30 (cx±22.5, cy±15) dengan dua rotor lingkar r=7.2 di
        (cx±7.5, cy) berisi tali busur heliks. Motor lingkar r=8 tergantung di
        atas casing lewat poros (motor_up=True) agar jalur hisap-tekan
        horizontal pada cy tidak menembus simbol motor. Kaki + pondasi tertutup.
        """
        out = rect(cx - 22.5, cy - 15.0, cx + 22.5, cy + 15.0)
        for rx in (cx - 7.5, cx + 7.5):
            out.append(circle(rx, cy, 7.2))
            out.append(chord(rx, cy, 7.2, 160.0, 340.0))
            out.append(chord(rx, cy, 7.2, 20.0, 200.0))
        # Poros motor vertikal di tengah casing
        out.append(line(cx, cy + 15.0, cx, cy + 23.0))       # ujung bawah ON casing, atas ON motor
        out.append(circle(cx, cy + 31.0, 8.0))               # motor (pusat 8 di atas ujung poros)
        self.text("M", cx, cy + 31.0, size=2.5)
        # Kaki & pondasi (dua-duanya terhubung: kaki ON dinding casing & pondasi)
        out += [
            line(cx - 14.0, cy - 15.0, cx - 14.0, cy - 19.5),
            line(cx + 14.0, cy - 15.0, cx + 14.0, cy - 19.5),
        ]
        out += rect(cx - 18.0, cy - 21.5, cx + 18.0, cy - 19.5)
        self.equip += out
        if tag:
            self.text(tag, cx, cy - 27.0, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "ROTARY SCREW AIR COMPRESSOR PACKAGE",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        if desc:
            self.text(desc, cx, cy - 32.5, size=1.8)
        return out

    # -------------------------------------------------------------------------
    # AFTERCOOLER INLINE (SHELL & TUBE RINGKAS, CW IN/OUT)
    # -------------------------------------------------------------------------
    def aftercooler_h(
        self,
        cx: float,
        cy: float,
        w: float = 40.0,
        h: float = 14.0,
        tag: str = "E-501",
        desc: str = "AFTERCOOLER",
    ) -> list[bd.Edge]:
        """Aftercooler inline: kapsul + zigzag tube + nozzle CW atas/bawah."""
        hw, hh = w / 2.0, h / 2.0
        out = rect(cx - hw, cy - hh, cx + hw, cy + hh)
        # Zigzag bundle: ujung ON dinding kiri/kanan
        pts = [
            (cx - hw, cy), (cx - hw / 2.0, cy + 4.0), (cx, cy - 4.0),
            (cx + hw / 2.0, cy + 4.0), (cx + hw, cy),
        ]
        for i in range(len(pts) - 1):
            out.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]))
        # Nozzle CW: stub + flange crossbar (mid ON stub)
        out += [
            line(cx - 10.0, cy + hh, cx - 10.0, cy + hh + 8.0),
            line(cx - 13.5, cy + hh + 8.0, cx - 6.5, cy + hh + 8.0),
            line(cx + 10.0, cy - hh, cx + 10.0, cy - hh - 8.0),
            line(cx + 6.5, cy - hh - 8.0, cx + 13.5, cy - hh - 8.0),
        ]
        self.equip += out
        self.text("CW IN", cx - 10.0, cy + hh + 11.3, size=1.8)
        self.text("CW OUT", cx + 10.0, cy - hh - 11.3, size=1.8)
        if tag:
            self.text(tag, cx, cy + hh + 16.5, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "AFTERCOOLER (SHELL & TUBE)",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        if desc:
            self.text(desc, cx, cy + hh + 21.7, size=1.8)
        return out

    # -------------------------------------------------------------------------
    # MOISTURE TRAP SIKLON + AUTO DRAIN
    # -------------------------------------------------------------------------
    def moisture_trap_cyclone(
        self,
        cx: float,
        y_top: float,
        r: float = 8.0,
        shell_h: float = 32.0,
        cone_h: float = 10.0,
        tag: str = "S-501",
        tag_y: float | None = None,
        drain: bool = True,
    ) -> list[bd.Edge]:
        """Pemisah kondensat siklon: silinder + head atas + kerucut bawah +
        swirl vortex + auto drain di apex kerucut."""
        y0 = y_top - shell_h
        apex = y0 - cone_h
        out = [
            line(cx - r, y0, cx - r, y_top),
            line(cx + r, y0, cx + r, y_top),
            arc3((cx - r, y_top), (cx, y_top + r * 0.5), (cx + r, y_top)),
            line(cx - r, y0, cx, apex),
            line(cx + r, y0, cx, apex),
            arc(cx, y_top - 6.0, 3.0, 20.0, 290.0),  # swirl vortex
        ]
        self.equip += out
        if drain:
            self.auto_drain_v(cx, apex, arrow=True)
        if tag:
            ty = tag_y if tag_y is not None else apex - 20.0
            self.text(tag, cx, ty, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "CYCLONE MOISTURE SEPARATOR",
                "x": round(cx, 3),
                "y": round((y0 + y_top) / 2.0, 3),
            })
        return out

    # -------------------------------------------------------------------------
    # AIR RECEIVER VERTIKAL (ASME SEC. VIII DIV. 1)
    # -------------------------------------------------------------------------
    def air_receiver_v(
        self,
        cx: float,
        y_bot: float,
        y_top: float,
        r: float = 14.0,
        tag: str = "",
        tag_y: float | None = None,
        drain: bool = True,
    ) -> list[bd.Edge]:
        """Receiver vertikal: shell + head 2:1 ellipsoidal + seam putus-putus +
        2 kaki + pondasi tertutup + auto drain di apex head bawah."""
        out = [
            line(cx - r, y_bot, cx - r, y_top),
            line(cx + r, y_bot, cx + r, y_top),
            arc3((cx - r, y_top), (cx, y_top + r * 0.5), (cx + r, y_top)),
            arc3((cx - r, y_bot), (cx, y_bot - r * 0.5), (cx + r, y_bot)),
        ]
        out += dashed(cx - r + 1.0, y_top, cx + r - 1.0, y_top, dash=3.0, gap=1.5)
        out += dashed(cx - r + 1.0, y_bot, cx + r - 1.0, y_bot, dash=3.0, gap=1.5)
        # Kaki (ujung atas ON dinding shell, bawah ON pondasi) + pondasi tertutup
        out += [
            line(cx - (r - 3.0), y_bot, cx - (r - 3.0), y_bot - 8.0),
            line(cx + (r - 3.0), y_bot, cx + (r - 3.0), y_bot - 8.0),
        ]
        out += rect(cx - r - 3.0, y_bot - 10.0, cx + r + 3.0, y_bot - 8.0)
        self.equip += out
        if drain:
            self.auto_drain_v(cx, y_bot - r * 0.5, arrow=True)
        if tag:
            ty = tag_y if tag_y is not None else y_bot - r * 0.5 - 20.0
            self.text(tag, cx, ty, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "VERTICAL AIR RECEIVER (ASME SEC. VIII DIV. 1)",
                "x": round(cx, 3),
                "y": round((y_bot + y_top) / 2.0, 3),
                "y_bot": round(y_bot, 3),
                "y_top": round(y_top, 3),
                "radius": round(r, 3),
            })
        return out

    # -------------------------------------------------------------------------
    # MENARA DESICCANT (TWIN-TOWER DRYER)
    # -------------------------------------------------------------------------
    def desiccant_tower(
        self,
        cx: float,
        y_bot: float,
        y_top: float,
        r: float = 10.0,
        tag: str = "",
        tag_y: float | None = None,
        bed: float = 10.0,
    ) -> list[bd.Edge]:
        """Menara desiccant: shell + head 2:1 + seam + bed adsorben berarsir.

        Bed dibatasi garis putus-putus di y_bot+bed dan y_top-bed, diarsir 45
        derajat pada layer REF-HATCH (label menara di luar simbol).
        """
        out = [
            line(cx - r, y_bot, cx - r, y_top),
            line(cx + r, y_bot, cx + r, y_top),
            arc3((cx - r, y_top), (cx, y_top + r * 0.5), (cx + r, y_top)),
            arc3((cx - r, y_bot), (cx, y_bot - r * 0.5), (cx + r, y_bot)),
        ]
        out += dashed(cx - r + 1.0, y_top, cx + r - 1.0, y_top, dash=3.0, gap=1.5)
        out += dashed(cx - r + 1.0, y_bot, cx + r - 1.0, y_bot, dash=3.0, gap=1.5)
        out += dashed(cx - r + 1.0, y_bot + bed, cx + r - 1.0, y_bot + bed, dash=3.0, gap=1.5)
        out += dashed(cx - r + 1.0, y_top - bed, cx + r - 1.0, y_top - bed, dash=3.0, gap=1.5)
        self.equip += out
        self.hatch += hatch45(cx - r + 1.0, y_bot + bed + 0.5, cx + r - 1.0, y_top - bed - 0.5, spacing=3.0)
        if tag:
            ty = tag_y if tag_y is not None else y_top + r * 0.5 + 6.5
            self.text(tag, cx, ty, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "DESICCANT TOWER (ACTIVATED ALUMINA / MOLECULAR SIEVE)",
                "x": round(cx, 3),
                "y": round((y_bot + y_top) / 2.0, 3),
            })
        return out

    # -------------------------------------------------------------------------
    # PLC SEQUENCE TIMER (KOTAK REF-SYM)
    # -------------------------------------------------------------------------
    def plc_timer(self, cx: float, cy: float, w: float = 16.0, h: float = 8.0, tag: str = "PLC") -> list[bd.Edge]:
        out = rect(cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0)
        self.sym += out
        if tag:
            self.text(tag, cx, cy + 0.2, size=1.8)
        return out

    # -------------------------------------------------------------------------
    # CONTROL VALVE VERTIKAL + PCV PRIORITY SUSTAINING VALVE
    # -------------------------------------------------------------------------
    def control_valve_v(
        self,
        cx: float,
        cy: float,
        w: float = 6.0,
        h: float = 10.0,
        tag: str = "",
        tag_pos: tuple[float, float] | None = None,
        act: int = 1,
    ) -> list[bd.Edge]:
        """Control valve pada pipa vertikal: bowtie + dot + stem samping +
        dome diafragma setengah lingkaran (ISA-5.1). act=+1 dome ke kanan."""
        hw, hh = w / 2.0, h / 2.0
        out = [
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            line(cx - hw - 0.8, cy - hh - 1.2, cx + hw + 0.8, cy - hh - 1.2),
            line(cx - hw - 0.8, cy + hh + 1.2, cx + hw + 0.8, cy + hh + 1.2),
        ]
        xd = cx + act * (hw + 5.0)
        out += [
            line(cx + act * hw, cy, xd, cy),
            arc(xd, cy, 2.2, 270.0, 90.0) if act > 0 else arc(xd, cy, 2.2, 90.0, 270.0),
            line(xd, cy - 2.2, xd, cy + 2.2),
        ]
        self.proc += out
        self.solid_dot(cx, cy, r=1.1, layer="REF-PROC")
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "PRIORITY SUSTAINING VALVE (PCV)",
                "orientation": "V",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
            if tag_pos is not None:
                self.text(tag, tag_pos[0], tag_pos[1], size=2.2)
        return out

    def priority_valve_v(
        self,
        cx: float,
        cy: float,
        tag: str = "PCV-501",
        tag_pos: tuple[float, float] | None = None,
        act: int = 1,
        note: str = "",
        note_pos: tuple[float, float] | None = None,
    ) -> list[bd.Edge]:
        """Priority sustaining valve (pisah IA/UA): control valve + anotasi
        ambang penutupan (default proyek: menutup UA pada < 5.5 barg)."""
        out = self.control_valve_v(cx, cy, tag=tag, tag_pos=tag_pos, act=act)
        if note and note_pos is not None:
            self.text(note, note_pos[0], note_pos[1], size=1.8)
        return out

    # -------------------------------------------------------------------------
    # KATUP PENGALIH MENARA (SWITCHING VALVE, TER-DAFTAR MTO)
    # -------------------------------------------------------------------------
    def switching_valve_v(
        self,
        cx: float,
        cy: float,
        tag: str = "",
        tag_pos: tuple[float, float] | None = None,
        nc: bool = False,
    ) -> list[bd.Edge]:
        """Katup pengalih menara pengering (gate vertikal, bisa NC solid)."""
        out = self.valve_gate_v(cx, cy, w=6.0, h=10.0, nc=nc, flanged=True, tag=tag)
        self.proc += out
        if tag and tag_pos is not None:
            self.text(tag, tag_pos[0], tag_pos[1], size=1.8)
        return out

    # -------------------------------------------------------------------------
    # ORIFICE PLATE VERTIKAL (PURGE) — kotak pipih tertutup melintang pipa
    # -------------------------------------------------------------------------
    def orifice_plate_v(self, x: float, y: float, half: float = 4.5, gap: float = 1.2) -> list[bd.Edge]:
        out = rect(x - half, y - gap, x + half, y + gap)
        self.proc += out
        return out

    # -------------------------------------------------------------------------
    # VENT / MUFFLER KE ATMOSFER
    # -------------------------------------------------------------------------
    def muffler_vent_h(self, x: float, y: float) -> list[bd.Edge]:
        """Simbol muffler/vent: V terbuka + crossbar, terhubung di (x, y)."""
        out = [
            line(x, y, x + 4.0, y + 3.0),
            line(x, y, x + 4.0, y - 3.0),
            line(x + 4.0, y - 3.0, x + 4.0, y + 3.0),
        ]
        self.proc += out
        return out

    def vent_cap_h(self, x: float, y: float) -> list[bd.Edge]:
        """Crossbar penutup ujung tail relief (mid tepat pada ujung garis)."""
        out = [line(x - 3.0, y, x + 3.0, y)]
        self.proc += out
        return out
