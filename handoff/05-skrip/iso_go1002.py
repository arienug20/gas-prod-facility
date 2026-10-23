"""PIPE ISOMETRIC - 100-GO-1002 DN100 -> 100-FL-1005 DN150.

GPF-00-PI-ISO-0003 Rev A5, A3 420x297, NTS (dimensions govern).
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


def build_iso_go1002(ctx: IsoContext) -> None:
    # ---------------- Geometry Vertices (True Isometric) ----------------
    # A = V-101 N2 Flange DN100, BOP.EL. +4150
    A = (78.0, 92.0)
    # B = Riser top elbow DN100, BOP.EL. +5000 (dz = +850 mm -> 16 mm sheet)
    B = (78.0, 108.0)
    # C = Tee + Reducer DN100x150 (35 m East -> 84 mm sheet)
    C = addp(B, mulp(EX, 84.0))  # (150.746, 150.0)
    # Branch stub to PSV-101 tail (15 mm North)
    P_BR = addp(C, mulp(NX, 15.0))  # (137.756, 157.5)
    # D = Elbow DN150 (8 m East -> 22 mm sheet)
    D = addp(C, mulp(EX, 22.0))  # (169.799, 161.0)
    # E = Elbow DN150 (11 m North -> 36 mm sheet)
    E = addp(D, mulp(NX, 36.0))  # (138.622, 179.0)
    # F = Elbow DN150 (12.5 m East -> 34 mm sheet)
    F = addp(E, mulp(EX, 34.0))  # (168.067, 196.0)
    # G = V-102 N1 Flange DN150, BOP.EL. +1150 (dz = -3850 mm -> 26 mm sheet)
    G = (F[0], F[1] - 26.0)  # (168.067, 170.0)

    # In-line stations along B -> C
    P_PS1 = addp(B, mulp(EX, 18.0))
    P_PV = addp(B, mulp(EX, 36.0))   # PV-101 @ 17 m
    P_GV = addp(B, mulp(EX, 56.0))   # GV-141 @ 25 m
    P_FE = addp(B, mulp(EX, 72.0))   # FE-141 @ 32 m

    # In-line stations along C -> D, D -> E, E -> F
    P_PS2 = addp(C, mulp(EX, 11.0))  # PS-002 GUIDE
    P_X = addp(D, mulp(NX, 18.0))    # Road crossing mid D-E
    P_PS3 = addp(E, mulp(EX, 17.0))  # PS-003 RESTING

    # ---------------- 1. Pipe Runs (REF-PROC) ----------------
    ctx.add_pipe_run(A, B)
    ctx.add_pipe_run(B, C)
    ctx.add_pipe_run(C, D)
    ctx.add_pipe_run(D, E)
    ctx.add_pipe_run(E, F)
    ctx.add_pipe_run(F, G)
    ctx.add_pipe_run(C, P_BR)

    # ---------------- 2. Symbols & In-line Equipment (REF-SYM) ----------------
    # Flange at A (V-101 N2 nozzle)
    ctx.flange(A, UX, half=2.2)
    ctx.stacked_bubbles(A, WX, [7, 9, 11], r=1.85, dist_first=7.0)
    ctx.continuation(A, DNX, ["CONT. FROM SEPARATOR V-101 N2",
                              "DRW NO. GPF-00-PI-PID-0001",
                              "SHEET 01 OF 03"], length=14.0)

    # Elbow at B
    ctx.part_bubble(addp(B, mulp(NX, 9.0)), B, 3)

    # PS-001 RESTING along B-C (leader down 9 mm, sits above dim string)
    ctx.pipe_support(P_PS1, EX, "PS-001", "RESTING", leader_vec=(0.0, -9.0), shelf_len=16.0)

    # PV-101 Globe Control Valve with Actuator
    ctx.globe(P_PV, EX, L=3.6, W=2.0, has_actuator=True, act_tag="PV-101")
    ctx.part_bubble(addp(P_PV, (-6.5, 10.0)), P_PV, 13)

    # GV-141 Gate Valve DN150
    ctx.gate(P_GV, EX, L=3.4, W=1.8)
    ctx.text("GV-141", P_GV[0] - 2.0, P_GV[1] + 5.0, size=1.5, att=5)
    ctx.part_bubble(addp(P_GV, mulp(NX, 10.0)), P_GV, 14)

    # FE-141 Orifice Flange + FT-141 Transmitter Bubble
    ctx.orifice(P_FE, EX, half=3.8, tag="FT-141", lead_dir=UX)
    ctx.part_bubble(addp(P_FE, (-8.0, 12.0)), P_FE, 15)

    # Pipe Callout Balloon (DN100) along B-C
    p_pipe1 = addp(B, mulp(EX, 22.0))
    ctx.part_bubble(addp(p_pipe1, (0.0, 11.0)), p_pipe1, 1)

    # Reducer + Tee at C
    p_red = subp(C, mulp(EX, 3.5))
    ctx.reducer(p_red, EX, L=2.6, W1=1.2, W2=2.2)
    ctx.part_bubble(addp(p_red, (-4.0, -9.0)), p_red, 6)
    ctx.part_bubble(addp(C, (4.0, -9.0)), C, 5)

    # Branch continuation at P_BR (text placed to the left of P_BR in clear space)
    p_term_br = addp(P_BR, mulp(NX, 12.0))
    ctx.sym_edges += dashed_line(P_BR, p_term_br)
    ctx.text("CONT. TO PSV-101 TAIL", p_term_br[0] - 2.0, p_term_br[1] + 2.0, size=1.4, att=6)
    ctx.text("DRW NO. GPF-00-PI-PID-0001", p_term_br[0] - 2.0, p_term_br[1] - 1.4, size=1.4, att=6)

    # PS-002 GUIDE along C-D (leader goes straight down, above dim string)
    ctx.pipe_support(P_PS2, EX, "PS-002", "GUIDE", leader_vec=(0.0, -9.0), shelf_len=14.0)

    # Elbow at D
    ctx.part_bubble(addp(D, (9.0, 2.0)), D, 4)

    # Road crossing band along D-E (layer REF-ROAD)
    r_w = 4.5
    ctx.road_edges += [
        line(P_X[0] - 12.0 * EX[0] - r_w * NX[0], P_X[1] - 12.0 * EX[1] - r_w * NX[1],
             P_X[0] + 12.0 * EX[0] - r_w * NX[0], P_X[1] + 12.0 * EX[1] - r_w * NX[1]),
        line(P_X[0] - 12.0 * EX[0] + r_w * NX[0], P_X[1] - 12.0 * EX[1] + r_w * NX[1],
             P_X[0] + 12.0 * EX[0] + r_w * NX[0], P_X[1] + 12.0 * EX[1] + r_w * NX[1]),
    ]
    # Road text placed to the left of D-E run in clear space
    p_rtxt = addp(P_X, (-14.0, -3.5))
    ctx.text("ROAD CROSSING EL +6.5", p_rtxt[0], p_rtxt[1], size=1.35, rot=-30.0, att=5)

    # Pipe Callout Balloon (DN150) along E-F
    p_pipe2 = addp(E, mulp(EX, 24.0))
    ctx.part_bubble(addp(p_pipe2, (0.0, 9.0)), p_pipe2, 2)

    # Elbow at E
    ctx.part_bubble(addp(E, mulp(WX, 8.0)), E, 4)

    # PS-003 RESTING along E-F (leader goes up-left into clear space)
    ctx.pipe_support(P_PS3, EX, "PS-003", "RESTING", leader_vec=(-6.0, 9.0), shelf_len=-15.0)

    # Elbow at F
    ctx.part_bubble(addp(F, mulp(EX, 7.0)), F, 4)

    # Flange at G (V-102 N1 nozzle)
    ctx.flange(G, DNX, half=2.4)
    ctx.stacked_bubbles(G, EX, [8, 10, 12], r=1.85, dist_first=7.0)
    p_term_g = addp(G, mulp(DNX, 14.0))
    ctx.sym_edges += dashed_line(G, p_term_g)
    ctx.text("CONT. TO FLARE KO DRUM V-102 N1", p_term_g[0] + 3.0, p_term_g[1] - 1.0, size=1.4, left=True, att=4)
    ctx.text("DRW NO. GPF-00-PI-PID-0001", p_term_g[0] + 3.0, p_term_g[1] - 4.4, size=1.4, left=True, att=4)
    ctx.text("SHEET 01 OF 03", p_term_g[0] + 3.0, p_term_g[1] - 7.8, size=1.4, left=True, att=4)

    # Flow arrows
    ctx.flow_arrow(addp(B, mulp(EX, 10.0)), EX)
    ctx.flow_arrow(addp(D, mulp(NX, 10.0)), NX)
    ctx.flow_arrow(addp(E, mulp(EX, 8.0)), EX)

    # Field welds (SW)
    ctx.sw(addp(B, mulp(EX, 3.0)), EX, txtoff=(0.0, 3.2))
    ctx.sw(subp(C, mulp(EX, 6.0)), EX, txtoff=(0.0, 3.2))
    ctx.sw(addp(D, mulp(NX, 3.0)), NX, txtoff=(3.0, 2.0))
    ctx.sw(addp(E, mulp(EX, 3.0)), EX, txtoff=(0.0, 3.2))

    # Line Callout Labels with Leaders
    # Callout 1 near B (shifted left into clear space)
    ctx.line_callout(addp(B, mulp(EX, 6.0)), (56.0, 126.0),
                     "100-GO-1002 DN100", "BOP.EL. +5000", shelf_len=28.0)
    # Callout 2 for 100-FL-1005 DN150 (placed vertically up from E-F into clear top area)
    p_pipe_ef = addp(E, mulp(EX, 8.0))
    ctx.line_callout(p_pipe_ef, (p_pipe_ef[0], 216.0),
                     "100-FL-1005 DN150", "BOP.EL. +5000", shelf_len=28.0)

    # BOP.EL. at A and G
    ctx.text("BOP.EL. +4150", A[0] + 5.0, A[1] - 1.0, size=1.4, left=True, att=4)
    ctx.text("BOP.EL. +1150", G[0] + 4.5, G[1] - 2.0, size=1.4, left=True, att=4)

    # ---------------- 3. Dimensions with Oblique Extension Lines ----------------
    # Dim 1: Riser A -> B (dz = 850 mm)
    # angle=90.0, oblique=120.0 pulls along WX
    ctx.dimrec(A, B, "850", 90.0, addp(A, mulp(WX, 8.0)), oblique=120.0)

    # Chained dimension string along East run B -> C -> D (placed at -18 mm so PS sits above it)
    dim_y_off = -18.0
    # Dim 2: Chained B -> PV (17000 mm)
    ctx.dimrec(B, P_PV, "17000", 30.0, addp(B, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 3: Chained PV -> GV (8000 mm)
    ctx.dimrec(P_PV, P_GV, "8000", 30.0, addp(P_PV, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 4: Chained GV -> C (10000 mm)
    ctx.dimrec(P_GV, C, "10000", 30.0, addp(P_GV, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 5: C -> D (8000 mm)
    ctx.dimrec(C, D, "8000", 30.0, addp(C, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 6: D -> E (11000 mm, North run)
    ctx.dimrec(D, E, "11000", -30.0, addp(D, (0.0, -11.0)), oblique=-60.0)

    # Dim 7: E -> F (12500 mm, East run)
    ctx.dimrec(E, F, "12500", 30.0, addp(E, (0.0, 11.0)), oblique=60.0)

    # Dim 8: Riser G -> F (3850 mm)
    # Pulled along WX into the open loop (between D-E and F-G)
    ctx.dimrec(G, F, "3850", 90.0, addp(G, mulp(WX, 8.0)), oblique=120.0)

    # ---------------- 4. Furniture (FNKT-10 3-Column Layout) ----------------
    bom_items = [
        (1, "PIPE", "PIPE SCH 40 CS ASTM A106-B SMLS", "DN100", "35.0 M"),
        (2, "PIPE", "PIPE SCH 40 CS ASTM A106-B SMLS", "DN150", "32.5 M"),
        (3, "FITTING", "90 ELL LR BW SCH 40 ASTM A234-WPB", "DN100", "1 EA"),
        (4, "FITTING", "90 ELL LR BW SCH 40 ASTM A234-WPB", "DN150", "3 EA"),
        (5, "FITTING", "TEE EQUAL BW ASTM A234-WPB", "DN150", "1 EA"),
        (6, "FITTING", "CONCENTRIC REDUCER BW", "DN100x150", "1 EA"),
        (7, "FLANGE", "FLANGE WN 150# RF SCH 40 A105", "DN100", "2 EA"),
        (8, "FLANGE", "FLANGE WN 150# RF SCH 40 A105", "DN150", "2 EA"),
        (9, "GASKET", "GASKET SPWD 150# RF SS316/GRAFOIL", "DN100", "2 EA"),
        (10, "GASKET", "GASKET SPWD 150# RF SS316/GRAFOIL", "DN150", "2 EA"),
        (11, "BOLT", "STUD BOLT A193-B7 W/2H NUTS", "5/8\"x90", "16 EA"),
        (12, "BOLT", "STUD BOLT A193-B7 W/2H NUTS", "3/4\"x100", "16 EA"),
        (13, "VALVE", "GLOBE CONTROL VALVE FC (PV-101)", "DN100", "1 EA"),
        (14, "VALVE", "GATE VALVE 150# RF (GV-141)", "DN150", "1 EA"),
        (15, "VALVE", "ORIFICE FLANGE ASSY (FE-141)", "DN100", "1 EA"),
    ]

    notes = [
        "1. ALL DIMENSIONS ARE IN MILLIMETERS,",
        "   UNLESS NOTED OTHERWISE.",
        "2. NTS — DIMENSIONS GOVERN.",
        "3. PIPING SPEC A1A (CS, RF #150).",
        "4. FIELD WELDS MARKED SW.",
        "5. SLOPE 1:500 TO FLARE KO DRUM V-102.",
    ]

    ctx.build_furniture(
        sheet_no=1, total_sheets=3,
        drw_no="GPF-00-PI-ISO-0003",
        line_no="100-GO-1002 DN100 / 100-FL-1005 DN150",
        service="GAS TO FLARE HEADER",
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
def iso_go1002():
    global CTX
    CTX = IsoContext()
    build_iso_go1002(CTX)
    return CTX.get_layers()


if __name__ == "__main__":
    iso_go1002()
    iso_go1002.__cadgen_model__.func()
    CTX.save_manifest("cad/iso_go1002.texts.json")
