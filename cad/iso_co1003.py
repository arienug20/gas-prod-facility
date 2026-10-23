"""PIPE ISOMETRIC - 080-CO-1003 DN80 (V-101 N3 -> P-101 SUCTION).

GPF-00-PI-ISO-0004 Rev A5, A3 420x297, NTS (dimensions govern).
True Piping Isometric (30°/150°/90°) & 3-Column FNKT-10 Layout.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure cad dir is in sys.path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from cadgen import dxf
from iso_common import (
    DNX,
    EX,
    NX,
    SX,
    UX,
    WX,
    IsoContext,
    addp,
    dashed_line,
    line,
    mulp,
    subp,
)

CTX = IsoContext()


def build_iso_co1003(ctx: IsoContext) -> None:
    # ---------------- Geometry Vertices (True Isometric) ----------------
    # A = V-101 N3 Flange DN80, BOP.EL. +2200
    A = (55.0, 145.0)
    # B = Elbow DN80 (4.2 m East -> 84 mm sheet)
    B = addp(A, mulp(EX, 84.0))  # (127.746, 187.0)
    # B2 = Elbow DN80 (2.3 m South -> 40 mm sheet)
    B2 = addp(B, mulp(SX, 40.0))  # (162.387, 167.0)
    # C = P-101 Suction Flange DN65, BOP.EL. +0600 (1.6 m Down -> 44 mm sheet)
    C = (B2[0], B2[1] - 44.0)  # (162.387, 123.0)

    # In-line stations along A -> B
    P_GV = addp(A, mulp(EX, 34.0))   # GV-101 @ 1.7 m
    P_ST = addp(A, mulp(EX, 64.0))   # ST-101 @ 3.2 m

    # Support along B -> B2
    P_PS101 = addp(B, mulp(SX, 20.0))  # PS-101 RESTING

    # Reducer along B2 -> C
    P_RED = (B2[0], B2[1] - 22.0)

    # ---------------- 1. Pipe Runs (REF-PROC) ----------------
    ctx.add_pipe_run(A, B)
    ctx.add_pipe_run(B, B2)
    ctx.add_pipe_run(B2, C)

    # ---------------- 2. Symbols & In-line Equipment (REF-SYM) ----------------
    # Flange at A (V-101 N3 nozzle)
    ctx.flange(A, EX, half=2.2)
    ctx.stacked_bubbles(A, NX, [5, 7, 9], r=1.85, dist_first=7.0)
    # Continuation dashed line goes WX; text placed further left so it clears extension line at X=55
    p_term_a = addp(A, mulp(WX, 14.0))
    ctx.sym_edges += dashed_line(A, p_term_a)
    ctx.text("CONT. FROM SEPARATOR V-101 N3", p_term_a[0] - 2.0, p_term_a[1] - 1.0, size=1.4, att=6)
    ctx.text("DRW NO. GPF-00-PI-PID-0001", p_term_a[0] - 2.0, p_term_a[1] - 4.4, size=1.4, att=6)
    ctx.text("SHEET 02 OF 03", p_term_a[0] - 2.0, p_term_a[1] - 7.8, size=1.4, att=6)

    # Pipe Callout Balloon 1 (DN80) along A-B
    p_pipe1 = addp(A, mulp(EX, 16.0))
    ctx.part_bubble(addp(p_pipe1, mulp(NX, 10.0)), p_pipe1, 1)

    # GV-101 Gate Valve DN80
    ctx.gate(P_GV, EX, L=3.4, W=1.8)
    ctx.text("GV-101", P_GV[0] - 2.0, P_GV[1] + 5.0, size=1.5, att=5)
    ctx.part_bubble(addp(P_GV, mulp(NX, 10.0)), P_GV, 11)

    # ST-101 Y-Strainer DN80
    ctx.strainer(P_ST, EX, L=3.6, W=2.0)
    ctx.text("ST-101", P_ST[0] - 2.0, P_ST[1] + 5.0, size=1.5, att=5)
    ctx.part_bubble(addp(P_ST, mulp(NX, 10.0)), P_ST, 12)

    # Elbow at B
    ctx.part_bubble(addp(B, mulp(NX, 9.0)), B, 3)

    # PS-101 RESTING along B-B2
    ctx.pipe_support(P_PS101, SX, "PS-101", "RESTING", leader_vec=(8.0, 7.0), shelf_len=16.0)

    # Elbow at B2
    ctx.part_bubble(addp(B2, mulp(EX, 8.0)), B2, 3)

    # Reducer DN80x65 along B2-C
    ctx.reducer(P_RED, DNX, L=2.6, W1=2.2, W2=1.2)
    ctx.part_bubble(addp(P_RED, mulp(WX, 8.0)), P_RED, 4)

    # Pipe Callout Balloon 2 (DN65) along B2-C
    p_pipe2 = (P_RED[0], P_RED[1] - 12.0)
    ctx.part_bubble(addp(p_pipe2, mulp(WX, 8.0)), p_pipe2, 2)

    # Flange at C (P-101 Suction nozzle)
    ctx.flange(C, DNX, half=2.0)
    ctx.stacked_bubbles(C, SX, [6, 8, 10], r=1.85, dist_first=7.0)
    ctx.continuation(C, DNX, ["CONT. TO P-101 SUCTION",
                              "DRW NO. GPF-00-PI-PID-0001",
                              "SHEET 02 OF 03"], length=14.0)

    # Flow arrows
    ctx.flow_arrow(addp(A, mulp(EX, 48.0)), EX)
    ctx.flow_arrow(addp(B, mulp(SX, 10.0)), SX)
    ctx.flow_arrow((B2[0], B2[1] - 8.0), DNX)

    # Field welds (SW)
    ctx.sw(addp(A, mulp(EX, 4.0)), EX, txtoff=(0.0, 3.2))
    ctx.sw(subp(B, mulp(EX, 4.0)), EX, txtoff=(0.0, 3.2))
    ctx.sw(addp(B, mulp(SX, 4.0)), SX, txtoff=(2.5, 2.5))
    ctx.sw((B2[0], B2[1] - 4.0), DNX, txtoff=(-3.0, 0.0))

    # Line Callout Labels with Leaders
    # Callout near B
    ctx.line_callout(addp(B, mulp(WX, 4.0)), (124.0, 210.0),
                     "080-CO-1003 DN80", "BOP.EL. +2200", shelf_len=28.0)

    # BOP.EL. at A and C (offset into clear space)
    ctx.text("BOP.EL. +2200", A[0] + 4.0, A[1] - 4.5, size=1.4, left=True, att=4)
    ctx.text("BOP.EL. +0600", C[0] - 14.0, C[1] - 1.0, size=1.4, att=5)

    # ---------------- 3. Dimensions with Oblique Extension Lines ----------------
    dim_y_off = -22.0
    # Dim 1: Chained A -> GV (1700 mm)
    ctx.dimrec(A, P_GV, "1700", 30.0, addp(A, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 2: Chained GV -> ST (1600 mm)
    ctx.dimrec(P_GV, P_ST, "1600", 30.0, addp(P_GV, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 3: Chained ST -> B (900 mm)
    ctx.dimrec(P_ST, B, "900", 30.0, addp(P_ST, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 4: B -> B2 (2300 mm, South run)
    # angle=-30.0, oblique=120.0 pulls vertically up (+90°), offset by 20 mm for PS clearance
    ctx.dimrec(B, B2, "2300", -30.0, addp(B, (0.0, 20.0)), oblique=120.0)

    # Dim 5: Riser C -> B2 (1600 mm)
    # angle=90.0, oblique=-60.0 pulls along EX to the right
    ctx.dimrec(C, B2, "1600", 90.0, addp(C, mulp(EX, 10.0)), oblique=-60.0)

    # ---------------- 4. Furniture (FNKT-10 3-Column Layout) ----------------
    bom_items = [
        (1, "PIPE", "PIPE SCH 40 CS ASTM A106-B SMLS", "DN80", "6.5 M"),
        (2, "PIPE", "PIPE SCH 40 CS ASTM A106-B SMLS", "DN65", "1.6 M"),
        (3, "FITTING", "90 ELL LR BW SCH 40 ASTM A234-WPB", "DN80", "2 EA"),
        (4, "FITTING", "CONCENTRIC REDUCER BW", "DN80x65", "1 EA"),
        (5, "FLANGE", "FLANGE WN 150# RF SCH 40 A105", "DN80", "1 EA"),
        (6, "FLANGE", "FLANGE WN 150# RF SCH 40 A105", "DN65", "1 EA"),
        (7, "GASKET", "GASKET SPWD 150# RF SS316/GRAFOIL", "DN80", "1 EA"),
        (8, "GASKET", "GASKET SPWD 150# RF SS316/GRAFOIL", "DN65", "1 EA"),
        (9, "BOLT", "STUD BOLT A193-B7 W/2H NUTS", "5/8\"x90", "8 EA"),
        (10, "BOLT", "STUD BOLT A193-B7 W/2H NUTS", "5/8\"x90", "8 EA"),
        (11, "VALVE", "GATE VALVE 150# RF (GV-101)", "DN80", "1 EA"),
        (12, "VALVE", "Y-STRAINER 150# RF (ST-101)", "DN80", "1 EA"),
    ]

    notes = [
        "1. ALL DIMENSIONS ARE IN MILLIMETERS,",
        "   UNLESS NOTED OTHERWISE.",
        "2. NTS — DIMENSIONS GOVERN.",
        "3. PIPING SPEC A1A (CS, RF #150).",
        "4. FIELD WELDS MARKED SW.",
        "5. SUCTION LINE TO CRUDE OIL PUMP P-101.",
    ]

    ctx.build_furniture(
        sheet_no=2, total_sheets=3,
        drw_no="GPF-00-PI-ISO-0004",
        line_no="080-CO-1003 DN80",
        service="CRUDE OIL SUCTION",
        code="ASME B31.3",
        pipe_class="A1A",
        design_temp="60 °C",
        design_press="17.2 BARG",
        op_temp="40 °C",
        op_press="10.0 BARG",
        bom_items=bom_items,
        notes=notes,
    )


@dxf
def iso_co1003():
    global CTX
    CTX = IsoContext()
    build_iso_co1003(CTX)
    return CTX.get_layers()


if __name__ == "__main__":
    iso_co1003()
    iso_co1003.__cadgen_model__.func()
    CTX.save_manifest("cad/iso_co1003.texts.json")
