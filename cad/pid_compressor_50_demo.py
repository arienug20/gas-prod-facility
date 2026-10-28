"""Concept demonstration only: 2 x 50% centrifugal compressor, A0."""
from pathlib import Path
from cadgen import dxf
from pid_common import PIDContext, line, rect, comp, dashed, pipe_run_h, pipe_run_v, pneu
from compression_common import CompressionContext

@dxf
def pid_compressor_50_demo():
    c=CompressionContext()
    c.frame += rect(10,7,831,587)+rect(20,15,823,579)
    for i in range(1,12):
        x=20+(823-20)*i/12
        c.frame += [line(x,7,x,15),line(x,579,x,587)]
    for i in range(12):
        x=20+(823-20)*(i+0.5)/12
        c.text(str(i+1),x,11,size=2); c.text(str(i+1),x,583,size=2)
    for i in range(1,8):
        y=15+(579-15)*i/8
        c.frame += [line(10,y,20,y),line(823,y,831,y)]
    for i in range(8):
        y=579-(579-15)*(i+0.5)/8
        c.text('ABCDEFGH'[i],15,y,size=2); c.text('ABCDEFGH'[i],827,y,size=2)
    c.frame += [line(655,15,655,579),line(655,435,823,435),line(655,567,823,567),line(655,195,823,195),line(655,148,823,148),line(655,116,823,116)]
    c.text('NOTES',739,573,size=2.5)
    notes=[
        '1. CONCEPT DEMONSTRATION; NOT FOR CONSTRUCTION.',
        '2. 2 X 50% = 50 MMSCFD TOTAL; 25 MMSCFD / TRAIN',
        '   ASSUMED. STANDARD VOLUME REFERENCE TBD.',
        '3. INLET 300 PSI; OUTLET 450 PSI. PRESSURE',
        '   BASIS PSIG / PSIA TO BE CONFIRMED.',
        '4. RANGE 60-110% PER TRAIN IS A TARGET ONLY;',
        '   VALIDATE COMPRESSOR MAP, DRIVER AND CONTROL.',
        '5. GAS COMPOSITION, TEMPERATURE, MOLECULAR WEIGHT,',
        '   Z, MATERIAL, LINE SIZES AND DESIGN P/T: TBD.',
        '6. ASV RECYCLE, RELIEF, BLOWDOWN, ESD, SEALS AND',
        '   AUXILIARIES REQUIRE VENDOR / PROCESS DESIGN.',
        '7. LSHH OR DISCHARGE PSHH: CLOSE SDV / TRIP TRAIN;',
        '   C&E, TRIP SOLVER AND FINAL ACTIONS TO BE VERIFIED.',
        '8. PSV SIZING, SET PRESSURE AND RELIEF BASIS: TBD.',
        '9. ALL TAGS ARE DEMO; OUTSIDE GPF-00-DB-0001.',
        '10. SCHEMATIC, NOT TO SCALE; NOT VENDOR APPROVED.'
    ]
    for i,t in enumerate(notes): c.text(t,659,560-i*6,size=1.8,left=True)
    c.text('LEGEND / INTERFACES',739,425,size=2.5)
    legend=['PROCESS: SOLID','ELECTRICAL SIGNAL: DASHED',
            'PNEUMATIC SIGNAL: LINE WITH SLASHES',
            'FIELD INSTRUMENT: CIRCLE','DCS / CONTROL: CIRCLE IN BOX',
            'FC: FAIL CLOSED; FO: FAIL OPEN',
            'TBD: TO BE DETERMINED','ESD SHOWN AS FUNCTION REFERENCES',
            'TRAIN A/B: 25 MMSCFD NOMINAL EACH (ASSUMED)']
    for i,t in enumerate(legend): c.text(t,659,410-9*i,size=1.8,left=True)
    c.text('REFERENCE DRAWINGS',739,180,size=2.2)
    c.text('GPF-00-PI-PID-0001 - P&ID V-101',659,169,size=1.8,left=True)
    c.text('GPF-00-DB-0001 - PROJECT DESIGN BASIS',659,161,size=1.8,left=True)
    c.text('REV     DESCRIPTION                         DATE',659,141,size=1.8,left=True)
    c.text('A0       CONCEPT DEMONSTRATION      28 OCT 2026',659,126,size=1.8,left=True)
    for y in (96,74,60,48,36,25): c.title.append(line(655,y,823,y))
    c.title.append(line(739,15,739,60))
    c.text('GAS PRODUCTION FACILITY - ONSHORE FIELD',739,106,size=2.5)
    c.text('PIPING & INSTRUMENTATION DIAGRAM',739,86,size=2.5)
    c.text('CENTRIFUGAL COMPRESSORS - DEMONSTRATION',739,79,size=2.1)
    c.text('GPF-DEMO-PID-COMP-50',739,66,size=2.5)
    c.text('REV A0',695,53,size=2.2); c.text('NTS',780,53,size=2.2)
    c.text('28 OCT 2026',695,41,size=2); c.text('SHEET 1 OF 1',780,41,size=2)
    c.text('DRAWN: CAD',695,29,size=2); c.text('CHECKED: TBD',780,29,size=2)
    c.text('APPROVED: TBD',780,19,size=2)
    c.frame += rect(35,525,640,570)
    for i,t in enumerate(['COMPRESSOR PACKAGE DATA - CONCEPT ONLY',
           '2 X 50% PARALLEL; 50 MMSCFD TOTAL / 25 MMSCFD PER TRAIN ASSUMED',
           'INLET 300 PSI / OUTLET 450 PSI; PSIG OR PSIA TBD',
           '60-110% PER TRAIN IS A DESIGN TARGET; MAP / SURGE AND DRIVER TBD',
           'GAS COMPOSITION / MOLECULAR WEIGHT / TEMPERATURE / DESIGN PRESSURE TBD']):
        c.text(t,40,564-i*8,size=2 if i==0 else 1.8,left=True)
    # Common headers, no implied plant connection.
    c.proc += c.continuity_box_left(135,'LINE / SIZE TBD','FROM GAS SUPPLY','DEMO')
    c.proc += pipe_run_h(135,72.5,85)+pipe_run_v(85,135,407)
    c.flow_arrow_h(78,135,size=2); c.flow_arrow_v(85,180,size=2); c.flow_arrow_v(85,320,size=2)
    c.proc += pipe_run_v(560,214,485)+pipe_run_h(485,560,585)
    c.proc += c.continuity_box_right(485,'LINE / SIZE TBD','TO GAS SYSTEM','DEMO')
    c.flow_arrow_v(560,300,size=2); c.flow_arrow_v(560,440,size=2); c.flow_arrow_h(575,485,size=2)
    c.text('SUCTION HEADER - LINE / SPEC TBD',65,285,size=1.8,rot=90)
    c.text('DISCHARGE HEADER - LINE / SPEC TBD',551,370,size=1.8,rot=90)
    minor=[]
    for L,suffix,loop in [(400,'A','901'),(220,'B','902')]:
        yi=L+7; yd=L-6; yr=L-72
        # Valve inlet and its labelled ESD function; connections otherwise shown as process lines.
        c.proc += pipe_run_h(yi,85,195,gaps=[(125,5)])
        c.proc += pipe_run_v(205,L+25,L+40)+pipe_run_h(L+40,205,225)+pipe_run_v(225,yi,L+40)
        c.proc += pipe_run_h(yi,225,320,gaps=[(240,1.2)])
        c.sym += c.sdv_h(125,yi,tag='SDV-'+loop,fail='FC')
        c.sym += c.interlock_diamond(133.5,yi+25,tag='ESD-'+loop,r=7)
        c.sig += dashed(133.5,yi+18,133.5,yi+10.5)
        c.text('ESD FUNCTION',133.5,yi+34,size=1.8)
        c.proc += c.orifice_h(240,yi,tag_fe='')
        c.text('FE-'+loop,230,L-9,size=1.8)
        minor += [line(240,yi,240,yi+10)]
        c.sym += c.bubble(240,yi+16,'FT',loop)
        c.text('TO UIC-'+loop,240,yi+27,size=1.8)
        minor += [line(275,yi,275,yi+10)]
        c.sym += c.bubble(275,yi+16,'PT',loop)
        c.text('TO UIC-'+loop,275,yi+27,size=1.8)
        c.flow_arrow_h(165,yi,size=2); c.flow_arrow_h(305,yi,size=2)
        c.equip += c.vessel_vertical_ko(205,L-20,L+20,r=10,tag='V-'+loop)
        c.text('SUCTION SCRUBBER',150,L-35,size=1.8)
        c.flow_arrow_v(205,L+34,size=1.5); c.flow_arrow_h(220,L+40,size=1.5)
        # Dedicated vapour-space relief connection to off-sheet relief system.
        minor += pipe_run_h(L+18,185,195)+pipe_run_v(185,L+18,L+36.8)
        c.sym += c.psv_angle(185,L+46,tag='PSV-'+loop,size_str='SIZE TBD',set_press='SET TBD')
        minor += pipe_run_h(L+46,194.2,300)
        minor += [line(300,L+43,300,L+49)]
        c.text('CAPPED / RELIEF DESTINATION TBD',285,L+52,size=1.8)
        c.flow_arrow_v(185,L+30,size=1.5,layer='REF-PROC-MINOR'); c.flow_arrow_h(270,L+46,size=1.5,layer='REF-PROC-MINOR')
        # Liquid outlet and BPCS control; no tie-in to relief/flare.
        minor += pipe_run_v(205,L-55,L-29.5)+pipe_run_h(L-55,205,310,gaps=[(285,5)])
        c.sym += c.control_valve_h(285,L-55,w=10,h=6,tag='LV-'+loop,fail='TBD')
        c.text('LV-'+loop,285,L-64,size=1.8)
        minor += [line(310,L-58,310,L-52)]
        c.text('CAPPED / LIQUID DESTINATION TBD',315,L-49,size=1.8)
        c.flow_arrow_v(205,L-47,direction=-1,size=1.5,layer='REF-PROC-MINOR'); c.flow_arrow_h(260,L-55,size=1.5,layer='REF-PROC-MINOR')
        # Separate vessel taps are conceptual; final SIS independence TBD.
        minor += [line(215,L-15,244,L-15),line(215,L,244,L)]
        c.sym += c.bubble(250,L-15,'LT',loop)
        c.sym += c.bubble(250,L,'LSHH',loop)
        c.sym += c.dcs(285,L-15,'LIC',loop)
        c.sig += dashed(256,L-15,277.5,L-15)
        c.sym += c.bubble(285,L-31,'FY',str(int(loop)+20))
        c.sig += dashed(285,L-22.5,285,L-25)
        c.sigp += pneu(285,L-37,285,L-42.5,spacing=4)
        c.sym += c.interlock_diamond(285,L,tag='ESD-'+loop,r=7)
        c.sig += dashed(256,L,279,L)
        c.compressor_centrifugal_617(330,L,r_in=5,r_out=8,tag='',casing='BARREL',driver='M')
        c.equip += [line(320,L,322.5,L),line(345,L,346.6,L)]
        c.text('K-90'+('1' if suffix=='A' else '2')+'-'+suffix,330,L-20,size=2.5)
        c.text('M DRIVER SYMBOL IS ILLUSTRATIVE',330,L-27,size=1.8)
        c.text('DRIVER TYPE TBD / ESD-'+loop+' TRIP',330,L-33,size=1.8)
        # Discharge: ASV pickoff UPSTREAM of nonreturn valve, ASV return DOWNSTREAM of SDV.
        c.proc += pipe_run_h(yd,340,560,gaps=[(475,5)])
        c.sym += c.valve_check_h(475,yd,w=10,h=6)
        c.text('CHECK VALVE',475,yd+8,size=1.8)
        c.flow_arrow_h(380,yd,size=2); c.flow_arrow_h(520,yd,size=2)
        minor += [line(405,yd,405,yd+10)]
        c.sym += c.bubble(405,yd+16,'PT',str(int(loop)+10))
        c.text('TO UIC-'+loop,405,yd+27,size=1.8)
        minor += [line(435,yd,435,yd+10)]
        c.sym += c.bubble(435,yd+16,'TT',str(int(loop)+10))
        c.text('TO UIC-'+loop,435,yd+27,size=1.8)
        minor += [line(455,yd,455,yd+10)]
        c.sym += c.bubble(455,yd+16,'PSHH',loop)
        c.sym += c.interlock_diamond(455,yd+35,tag='ESD-'+loop,r=7)
        c.sig += dashed(455,yd+22,455,yd+28)
        c.text('TRIP K / CLOSE SDV',455,yd+45,size=1.8)
        c.proc += pipe_run_v(180,yr,yi)+pipe_run_h(yr,180,450,gaps=[(365,5)])+pipe_run_v(450,yr,yd)
        c.sym += c.control_valve_h(365,yr,w=10,h=6,tag='ASV-'+loop,fail='FO')
        c.text('ASV-'+loop+' (FO)',365,yr-12,size=2)
        c.text('RECYCLE / VALVE SIZE TBD',300,yr-10,size=1.8)
        c.flow_arrow_v(450,yr+30,direction=-1,size=2)
        c.flow_arrow_h(410,yr,direction=-1,size=2); c.flow_arrow_h(260,yr,direction=-1,size=2)
        c.flow_arrow_v(180,yr+30,size=2)
        c.sym += c.dcs(365,yr+45,'UIC',loop)
        c.sym += c.bubble(365,yr+25,'FY',loop)
        c.sig += dashed(365,yr+37.5,365,yr+31)
        c.sigp += pneu(365,yr+19,365,yr+12.5,spacing=4)
        c.text('FROM FT / PT / TT: SEE TAGS',405,yr+45,size=1.8)
        c.text('AS CONTROL / SURGE MAP TBD',405,yr+39,size=1.8)
        c.text('TRAIN '+suffix+' | 25 MMSCFD NOMINAL ASSUMED',470,yr-24,size=2.2)
        c.text('K-'+loop+' PACKAGE: SEAL GAS / LUBE OIL / COOLING / DRIVER',425,yr-33,size=1.8)
        c.text('INTERFACES, TRIPS, BLOWDOWN AND UTILITIES - VENDOR TBD',425,yr-39,size=1.8)
    c.text('PACKAGE AND RELIEF DETAILS REQUIRE PROCESS / VENDOR DESIGN',335,73,size=2.0)
    c.text('FAIL ACTIONS SHOWN ARE CONCEPT ASSUMPTIONS / SUBJECT TO REVIEW',335,67,size=2.0)
    layers=c.export_manifest(Path(__file__).with_name('pid_compressor_50_demo.texts.json'))
    layers['REF-PROC-MINOR']=comp(minor)
    return layers

if __name__ == '__main__':
    pid_compressor_50_demo()
