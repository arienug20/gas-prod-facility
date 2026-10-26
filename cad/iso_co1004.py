"""PIPE ISOMETRIC - 080-CO-1004 DN80 (P-101 DISCHARGE -> T-101 N1).

GPF-00-PI-ISO-0005 Rev A6, A3 420x297, NTS (dimensions govern).
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


def build_iso_co1004(ctx: IsoContext) -> None:
    # ---------------- Geometry Vertices (True Isometric) ----------------
    # A = P-101 Discharge Flange DN65, BOP.EL. +0800
    A = (42.0, 95.0)
    # B = Riser bottom elbow DN80 (1.2 m East -> 36 mm sheet)
    B = addp(A, mulp(EX, 36.0))  # (73.177, 113.0)
    # C = Riser top elbow DN80, BOP.EL. +5000 (4.2 m Up -> 28 mm sheet)
    C = (B[0], B[1] + 28.0)      # (73.177, 141.0)
    # D = Elbow DN80 (3.5 m North -> 18 mm sheet)
    D = addp(C, mulp(NX, 18.0))  # (57.588, 150.0)
    # E = Elbow DN80 (20.0 m East -> 52 mm sheet)
    E = addp(D, mulp(EX, 52.0))  # (102.622, 176.0)
    # F = Elbow DN80, BOP.EL. +1200 (3.8 m Down -> 26 mm sheet)
    F = (E[0], E[1] - 26.0)      # (102.622, 150.0)
    # G = Elbow DN80 (23.0 m East -> 62 mm sheet)
    G = addp(F, mulp(EX, 62.0))  # (156.315, 181.0)
    # H = Riser bottom elbow DN80 (1.5 m North -> 15 mm sheet)
    H = addp(G, mulp(NX, 15.0))  # (143.325, 188.5)
    # I = Riser top elbow DN80, BOP.EL. +6700 (5.5 m Up -> 30 mm sheet)
    I = (H[0], H[1] + 30.0)      # (143.325, 218.5)
    # J = Elbow DN80 (1.7 m South -> 16 mm sheet)
    J = addp(I, mulp(SX, 16.0))  # (157.181, 210.5)
    # K = T-101 N1 Flange DN80, BOP.EL. +6150 (0.55 m Down -> 12 mm sheet)
    K = (J[0], J[1] - 12.0)      # (157.181, 198.5)

    # In-line stations
    P_CV = addp(A, mulp(EX, 9.0))     # CV-101
    P_GV2 = addp(A, mulp(EX, 18.0))   # GV-102
    P_RED1 = addp(A, mulp(EX, 27.0))  # RED 65x80

    P_PS201 = addp(D, mulp(EX, 14.0))  # PS-201 RESTING
    P_FE2 = addp(D, mulp(EX, 26.0))    # FE-142

    P_LV = addp(F, mulp(EX, 11.0))     # LV-121
    P_PS202 = addp(F, mulp(EX, 32.0))  # PS-202 RESTING
    P_GV3 = addp(F, mulp(EX, 53.0))    # GV-103

    P_PS203 = (H[0], H[1] + 15.0)      # PS-203 GUIDE

    # ---------------- 1. Pipe Runs (REF-PROC) ----------------
    ctx.add_pipe_run(A, B)
    ctx.add_pipe_run(B, C)
    ctx.add_pipe_run(C, D)
    ctx.add_pipe_run(D, E)
    ctx.add_pipe_run(E, F)
    ctx.add_pipe_run(F, G)
    ctx.add_pipe_run(G, H)
    ctx.add_pipe_run(H, I)
    ctx.add_pipe_run(I, J)
    ctx.add_pipe_run(J, K)

    # ---------------- 2. Symbols & In-line Equipment (REF-SYM) ----------------
    # Flange at A (P-101 Discharge)
    ctx.flange(A, EX, half=2.0)
    ctx.stacked_bubbles(A, NX, [5, 7, 9], r=1.85, dist_first=7.0)
    p_term_a = addp(A, mulp(DNX, 22.0))
    ctx.sym_edges += dashed_line(A, p_term_a)
    ctx.text("CONT. FROM P-101 DISCHARGE", p_term_a[0] + 2.5, p_term_a[1] + 1.0, size=1.4, left=True, att=4)
    ctx.text("DRW NO. GPF-00-PI-PID-0001", p_term_a[0] + 2.5, p_term_a[1] - 2.4, size=1.4, left=True, att=4)
    ctx.text("SHEET 03 OF 03", p_term_a[0] + 2.5, p_term_a[1] - 5.8, size=1.4, left=True, att=4)

    # CV-101 Check Valve DN65
    ctx.check_valve(P_CV, EX, L=3.2, W=1.8)
    ctx.text("CV-101", P_CV[0] - 2.0, P_CV[1] + 5.0, size=1.5, att=5)
    ctx.part_bubble(addp(P_CV, mulp(NX, 9.0)), P_CV, 11)

    # GV-102 Gate Valve DN80
    ctx.gate(P_GV2, EX, L=3.4, W=1.8)
    ctx.text("GV-102", P_GV2[0] - 2.0, P_GV2[1] + 5.0, size=1.5, att=5)
    ctx.part_bubble(addp(P_GV2, mulp(NX, 9.0)), P_GV2, 12)

    # Reducer DN65x80
    ctx.reducer(P_RED1, EX, L=2.6, W1=1.2, W2=2.2)
    ctx.part_bubble(addp(P_RED1, mulp(NX, 9.0)), P_RED1, 4)

    # Pipe Callout Balloon 1 (DN65) near A
    ctx.part_bubble(addp(A, (-6.0, 8.0)), addp(A, mulp(EX, 4.0)), 1)

    # Elbow at B
    ctx.part_bubble(addp(B, mulp(SX, 8.0)), B, 3)

    # Elbow at C
    ctx.part_bubble(addp(C, mulp(EX, 9.0)), C, 3)

    # Elbow at D
    ctx.part_bubble(addp(D, mulp(WX, 9.0)), D, 3)

    # PS-201 RESTING along D-E (leader goes up-left into clear space)
    ctx.pipe_support(P_PS201, EX, "PS-201", "RESTING", leader_vec=(-6.0, 9.0), shelf_len=-15.0)

    # FE-142 Orifice Flange + FT-142 (lead goes straight UP into clear space)
    ctx.orifice(P_FE2, EX, half=3.8, tag="FT-142", lead_dir=UX)
    ctx.part_bubble(addp(P_FE2, (10.0, 14.0)), P_FE2, 13)

    # Pipe Callout Balloon 2 (DN80) along D-E
    p_pipe2 = addp(D, mulp(EX, 42.0))
    ctx.part_bubble(addp(p_pipe2, (0.0, 10.0)), p_pipe2, 2)

    # Elbow at E
    ctx.part_bubble(addp(E, (7.0, 5.0)), E, 3)

    # Elbow at F
    ctx.part_bubble(addp(F, (-6.0, -7.0)), F, 3)

    # LV-121 Globe Control Valve with Actuator along F-G
    ctx.globe(P_LV, EX, L=3.6, W=2.0, has_actuator=True, act_tag="LV-121")
    ctx.part_bubble(addp(P_LV, (11.0, 10.0)), P_LV, 14)

    # PS-202 RESTING along F-G
    ctx.pipe_support(P_PS202, EX, "PS-202", "RESTING", leader_vec=(0.0, -9.0), shelf_len=15.0)

    # GV-103 Gate Valve along F-G
    ctx.gate(P_GV3, EX, L=3.4, W=1.8)
    ctx.text("GV-103", P_GV3[0] - 2.0, P_GV3[1] + 5.0, size=1.5, att=5)
    ctx.part_bubble(addp(P_GV3, mulp(NX, 10.0)), P_GV3, 15)

    # Elbow at G
    ctx.part_bubble(addp(G, mulp(EX, 8.0)), G, 3)

    # Elbow at H
    ctx.part_bubble(addp(H, mulp(WX, 8.0)), H, 3)

    # PS-203 GUIDE along H-I (leader to the left)
    ctx.pipe_support(P_PS203, UX, "PS-203", "GUIDE", leader_vec=(-12.0, 0.0), shelf_len=-15.0)

    # Elbow at I
    ctx.part_bubble(addp(I, mulp(EX, 8.0)), I, 3)

    # Elbow at J
    ctx.part_bubble(addp(J, mulp(EX, 8.0)), J, 3)

    # Flange at K (T-101 N1 nozzle)
    ctx.flange(K, DNX, half=2.2)
    ctx.stacked_bubbles(K, EX, [6, 8, 10], r=1.85, dist_first=7.0)
    # Continuation dashed line goes along SX into open space on the right
    p_term_k = addp(K, mulp(SX, 14.0))
    ctx.sym_edges += dashed_line(K, p_term_k)
    ctx.text("CONT. TO STORAGE TANK T-101 N1", p_term_k[0] + 2.0, p_term_k[1] - 1.0, size=1.4, left=True, att=4)
    ctx.text("DRW NO. GPF-00-PI-PID-0001", p_term_k[0] + 2.0, p_term_k[1] - 4.4, size=1.4, left=True, att=4)
    ctx.text("SHEET 03 OF 03", p_term_k[0] + 2.0, p_term_k[1] - 7.8, size=1.4, left=True, att=4)

    # Flow arrows
    ctx.flow_arrow(addp(A, mulp(EX, 32.0)), EX)
    ctx.flow_arrow((B[0], B[1] + 14.0), UX)
    ctx.flow_arrow(addp(C, mulp(NX, 8.0)), NX)
    ctx.flow_arrow(addp(D, mulp(EX, 10.0)), EX)
    ctx.flow_arrow((E[0], E[1] - 12.0), DNX)
    ctx.flow_arrow(addp(F, mulp(EX, 22.0)), EX)
    ctx.flow_arrow((H[0], H[1] + 8.0), UX)

    # Field welds (SW)
    ctx.sw(addp(B, mulp(UX, 4.0)), UX, txtoff=(-3.0, 0.0))
    ctx.sw(addp(C, mulp(NX, 4.0)), NX, txtoff=(-2.5, 2.5))
    ctx.sw(addp(D, mulp(EX, 4.0)), EX, txtoff=(0.0, 3.2))
    ctx.sw((E[0], E[1] - 4.0), DNX, txtoff=(-3.0, 0.0))
    ctx.sw(addp(F, mulp(EX, 4.0)), EX, txtoff=(0.0, 3.2))
    ctx.sw(addp(G, mulp(NX, 4.0)), NX, txtoff=(-2.5, 2.5))
    ctx.sw((H[0], H[1] + 4.0), UX, txtoff=(-3.0, 0.0))

    # Line Callout Labels with Leaders
    # Callout 1 attached to riser B-C (placed in open window between A-B and C-D)
    ctx.line_callout((B[0], 127.0), (32.0, 132.0),
                     "080-CO-1004 DN80", "BOP.EL. +5000", shelf_len=28.0)
    # Callout 2 near I (placed above I)
    ctx.line_callout(I, (120.0, 235.0),
                     "080-CO-1004 DN80", "BOP.EL. +6700", shelf_len=28.0)

    # BOP.EL. labels (placed in clean clear zones)
    ctx.text("BOP.EL. +0800", A[0] + 4.0, A[1] - 5.0, size=1.4, left=True, att=4)
    ctx.text("BOP.EL. +1200", F[0] + 8.0, F[1] - 3.5, size=1.4, left=True, att=4)
    ctx.text("BOP.EL. +6150", K[0] + 2.4, K[1] - 10.2, size=1.4, left=True, att=4)  # OPT-3 A6: below continuation dashes

    # ---------------- 3. Dimensions with Oblique Extension Lines ----------------
    dim_y_off = -20.0
    # Dim 1: A -> B (1200 mm)
    ctx.dimrec(A, B, "1200", 30.0, addp(A, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 2: Riser B -> C (4200 mm)
    ctx.dimrec(B, C, "4200", 90.0, addp(B, mulp(WX, 8.0)), oblique=120.0)

    # Dim 3: C -> D (3500 mm, North run, pulled down-left below C-D into clear window)
    ctx.dimrec(C, D, "3500", -30.0, addp(C, (0.0, -9.0)), oblique=-60.0)

    # Dim 4: Chained D -> FE2 (10000 mm, pulled +24 mm above D-E so it clears FT-142)
    ctx.dimrec(D, P_FE2, "10000", 30.0, addp(D, (0.0, 22.0)), oblique=60.0)

    # Dim 5: Chained FE2 -> E (10000 mm, pulled +22 mm above D-E)
    ctx.dimrec(P_FE2, E, "10000", 30.0, addp(P_FE2, (0.0, 22.0)), oblique=60.0)

    # Dim 6: Riser F -> E (3800 mm)
    ctx.dimrec(F, E, "3800", 90.0, addp(F, mulp(WX, 8.0)), oblique=120.0)

    # Dim 7: Chained F -> LV (4000 mm)
    ctx.dimrec(F, P_LV, "4000", 30.0, addp(F, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 8: Chained LV -> GV3 (17000 mm)
    ctx.dimrec(P_LV, P_GV3, "17000", 30.0, addp(P_LV, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 9: Chained GV3 -> G (2000 mm)
    ctx.dimrec(P_GV3, G, "2000", 30.0, addp(P_GV3, (0.0, dim_y_off)), oblique=-120.0)

    # Dim 10: G -> H (1500 mm, North run)
    ctx.dimrec(G, H, "1500", -30.0, addp(G, (0.0, -11.0)), oblique=-60.0)

    # Dim 11: Riser H -> I (5500 mm)
    ctx.dimrec(H, I, "5500", 90.0, addp(H, mulp(WX, 7.0)), oblique=120.0)

    # Dim 12: I -> J (1700 mm, South run)
    ctx.dimrec(I, J, "1700", -30.0, addp(I, (0.0, 10.0)), oblique=120.0)

    # Dim 13: Riser K -> J (550 mm, pulled to the left WX so it clears K stacked bubbles)
    ctx.dimrec(K, J, "550", 90.0, addp(K, mulp(WX, 6.0)), oblique=120.0)

    # ---------------- 4. Furniture (FNKT-10 3-Column Layout) ----------------
    bom_items = [
        (1, "PIPE", "PIPE SCH 40 CS ASTM A106-B SMLS", "DN65", "1.2 M"),
        (2, "PIPE", "PIPE SCH 40 CS ASTM A106-B SMLS", "DN80", "68.0 M"),
        (3, "FITTING", "90 ELL LR BW SCH 40 ASTM A234-WPB", "DN80", "9 EA"),
        (4, "FITTING", "CONCENTRIC REDUCER BW", "DN65x80", "1 EA"),
        (5, "FLANGE", "FLANGE WN 150# RF SCH 40 A105", "DN65", "1 EA"),
        (6, "FLANGE", "FLANGE WN 150# RF SCH 40 A105", "DN80", "3 EA"),
        (7, "GASKET", "GASKET SPWD 150# RF SS316/GRAFOIL", "DN65", "1 EA"),
        (8, "GASKET", "GASKET SPWD 150# RF SS316/GRAFOIL", "DN80", "3 EA"),
        (9, "BOLT", "STUD BOLT A193-B7 W/2H NUTS", "5/8\"x90", "8 EA"),
        (10, "BOLT", "STUD BOLT A193-B7 W/2H NUTS", "5/8\"x90", "24 EA"),
        (11, "VALVE", "CHECK VALVE 150# RF (CV-101)", "DN65", "1 EA"),
        (12, "VALVE", "GATE VALVE 150# RF (GV-102)", "DN80", "1 EA"),
        (13, "VALVE", "ORIFICE FLANGE ASSY (FE-142)", "DN80", "1 EA"),
        (14, "VALVE", "GLOBE CONTROL VALVE FC (LV-121)", "DN80", "1 EA"),
        (15, "VALVE", "GATE VALVE 150# RF (GV-103)", "DN80", "1 EA"),
    ]

    notes = [
        "1. ALL DIMENSIONS ARE IN MILLIMETERS,",
        "   UNLESS NOTED OTHERWISE.",
        "2. NTS — DIMENSIONS GOVERN.",
        "3. PIPING SPEC A1A (CS, RF #150).",
        "4. FIELD WELDS MARKED SW.",
        "5. CRUDE OIL TRANSFER LINE TO STORAGE TANK T-101.",
    ]

    ctx.build_furniture(
        sheet_no=3, total_sheets=3,
        drw_no="GPF-00-PI-ISO-0005",
        line_no="080-CO-1004 DN80",
        service="CRUDE OIL TO STORAGE TANK",
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
def iso_co1004():
    global CTX
    CTX = IsoContext()
    build_iso_co1004(CTX)
    return CTX.get_layers()


if __name__ == "__main__":
    iso_co1004()
    iso_co1004.__cadgen_model__.func()
    CTX.save_manifest("cad/iso_co1004.texts.json")
