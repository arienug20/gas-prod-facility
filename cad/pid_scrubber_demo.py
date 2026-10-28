"""Standalone vertical gas scrubber P&ID, demonstration only, Rev A1."""
from pathlib import Path
from cadgen import dxf
from pid_common import PIDContext, line, rect, comp, dashed, pneu, pipe_run_h, pipe_run_v

@dxf
def pid_scrubber_demo():
    c = PIDContext()
    c.frame += rect(10, 7, 831, 587) + rect(20, 15, 823, 579)
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
    c.frame += [line(655,15,655,579), line(655,435,823,435), line(655,567,823,567), line(655,195,823,195), line(655,148,823,148), line(655,116,823,116)]
    c.text('NOTES',739,573,size=2.5)
    notes = [
        '1. DEMONSTRATION ONLY - NOT FOR DESIGN OR CONSTRUCTION.',
        '2. V-901, LINE NUMBERS AND ALL INSTRUMENT TAGS ARE',
        '   EXAMPLE IDENTIFIERS; NOT REGISTERED IN DESIGN BASIS.',
        '3. PROCESS DATA, PIPE SIZES, SETPOINTS AND FAIL ACTIONS',
        '   REQUIRE ENGINEERING DEVELOPMENT AND APPROVAL.',
        '4. PSV OUTLET TO CLOSED RELIEF SYSTEM; SIZING, SET',
        '   PRESSURE AND BACKPRESSURE TO BE VERIFIED.',
        '5. DEMO C&E: LSHH-901 -> ESD-901 -> CLOSE SDV-901.',
        '   INSTRUMENT INDEPENDENCE AND SETPOINTS: TBD.',
        '6. LIQUID DESTINATION, DRAIN AND SAMPLE REQUIREMENTS',
        '   ARE TO BE CONFIRMED IN PROCESS DESIGN.',
        '7. SINGLE PSV SHOWN; SPARE / CHANGEOVER TBD.',
        '8. SCHEMATIC - NOT TO SCALE. NO ORIENTATION IMPLIED.',
    ]
    for i,t in enumerate(notes): c.text(t,659,560-i*6,size=1.8,left=True)
    c.text('LEGEND / DESIGN STATUS',739,425,size=2.5)
    for i,t in enumerate(['SOLID LINE: PROCESS', 'DASHED LINE: ELECTRICAL SIGNAL', 'SLASHED LINE: PNEUMATIC SIGNAL', 'FIELD INSTRUMENT: CIRCLE', 'DCS: CIRCLE IN SQUARE', 'FC: FAIL CLOSED', 'TBD: TO BE DETERMINED', 'REFER TO APPROVED DESIGN BASIS FOR PROJECT WORK']):
        c.text(t,659,412-i*8,size=1.8,left=True)
    c.sigp += pneu(665,340,690,340,spacing=5)
    c.text('PNEUMATIC SIGNAL',700,340,size=1.8,left=True)
    c.text('REFERENCE DRAWINGS',739,187,size=2.3)
    c.text('GPF-00-PI-PID-0001: V-101 REFERENCE',659,176,size=1.8,left=True)
    c.text('GPF-00-DB-0001: PROJECT DESIGN BASIS',659,168,size=1.8,left=True)
    c.text('REV     DESCRIPTION                       DATE',659,141,size=1.8,left=True)
    c.text('A1       LOOP / RELIEF REVIEW          28 OCT 2026',659,135,size=1.8,left=True)
    c.text('A0       INITIAL DEMONSTRATION      28 OCT 2026',659,125,size=1.8,left=True)
    for y in (96,74,60,48,36,25): c.title.append(line(655,y,823,y))
    c.title.append(line(739,15,739,60))
    c.text('GAS PRODUCTION FACILITY - ONSHORE FIELD',739,106,size=2.5)
    c.text('PIPING & INSTRUMENTATION DIAGRAM',739,86,size=2.5)
    c.text('VERTICAL GAS SCRUBBER - DEMONSTRATION',739,79,size=2.3)
    c.text('GPF-DEMO-PID-SCRUBBER',739,66,size=2.5)
    c.text('REV A1',695,53,size=2.2); c.text('NTS',780,53,size=2.2)
    c.text('28 OCT 2026',695,41,size=2.0); c.text('SHEET 1 OF 1',780,41,size=2.0)
    c.text('DRAWN: CAD',695,29,size=2.0); c.text('CHECKED: TBD',780,29,size=2.0)
    c.text('APPROVED: TBD',780,19,size=2.0)

    # Vertical vessel with demister and bottom nozzle, from the shared library.
    c.equip += c.vessel_vertical_ko(320,230,430,r=32,tag='V-901')
    c.text('VERTICAL GAS SCRUBBER',320,315,size=2.5)
    c.text('DEMISTER',370,423,size=1.8)
    c.text('DATA / MAWP: TBD',320,300,size=2.0)
    c.frame += rect(40,520,400,567)
    c.text('EQUIPMENT DATA - DEMONSTRATION',45,560,size=2.3,left=True)
    for i,t in enumerate(['V-901  |  VERTICAL GAS SCRUBBER  |  SIZE: TBD',
                          'OPERATING P / T: TBD  |  DESIGN P / T: TBD',
                          'MAWP / DESIGN CODE / MATERIAL: TBD',
                          'ALL TAGS AND PROCESS DATA OUTSIDE GPF DESIGN BASIS']):
        c.text(t,45,552-i*7,size=1.8,left=True)
    # Inlet and isolation valve.
    c.proc += c.continuity_box_left(360,'150-NG-9901 DN150','FROM GAS SUPPLY','DEMO')
    c.proc += pipe_run_h(360,72.5,288,gaps=[(155,5)])
    c.sym += c.sdv_h(155,360,tag='SDV-901',fail='FC')
    c.sym += c.interlock_diamond(163.5,390,tag='ESD-901',r=7)
    c.sig += dashed(163.5,383,163.5,370.5)
    c.text('SHUTDOWN VALVE',155,341,size=1.8)
    c.flow_arrow_h(120,360,size=2); c.flow_arrow_h(245,360,size=2)
    # Treated gas top outlet.
    c.proc += pipe_run_v(320,446,495) + pipe_run_h(495,320,585)
    c.proc += c.continuity_box_right(495,'150-NG-9902 DN150','TO GAS SYSTEM','DEMO')
    c.text('TREATED GAS OUTLET',455,504,size=2.0)
    c.flow_arrow_v(320,475,size=2); c.flow_arrow_h(410,495,size=2); c.flow_arrow_h(530,495,size=2)
    # Dedicated top-head relief connection, exact intersection with the circular head.
    c.proc += pipe_run_v(340,440.641016,460.8)
    c.sym += c.psv_angle(340,470,tag='PSV-901',size_str='SIZE TBD',set_press='SET TBD')
    c.proc += pipe_run_h(470,349.2,585)
    c.proc += c.continuity_box_right(470,'XXX-FL-9903 DN TBD','TO RELIEF HEADER','DEMO')
    c.flow_arrow_v(340,454,size=2); c.flow_arrow_h(490,470,size=2)
    # Pressure indication: field transmitter and DCS indicator.
    minor = pipe_run_h(390,288,265)
    c.sym += c.bubble(259,390,'PT','901')
    c.sig += dashed(253,390,230,390)
    c.sym += c.dcs(222,390,'PI','901')
    c.text('PRESSURE INDICATION',222,377,size=1.8)
    # Level connections are explicitly shown on the shell and LT to LIC.
    minor += pipe_run_h(270,352,395,gaps=[(375,5)]) + pipe_run_h(335,352,395,gaps=[(375,5)])
    c.sym += c.valve_gate_h(375,270,w=10,h=6,tag='GV-902')
    c.sym += c.valve_gate_h(375,335,w=10,h=6,tag='GV-903')
    minor += pipe_run_v(395,270,335)
    minor += pipe_run_v(395,245,270,gaps=[(255,5)])
    minor += [line(393,245,397,245)]
    c.sym += c.valve_gate_v(395,255,w=6,h=10,tag='GV-904')
    c.text('GV-902',375,261,size=1.8)
    c.text('GV-903',375,326,size=1.8)
    c.text('GV-904',411,255,size=1.8)
    c.text('CAPPED DRAIN; DESTINATION TBD',445,240,size=1.8)
    c.sym += [line(395,245,403,240),line(403,240,420,240)]
    c.flow_arrow_v(395,264,direction=-1,size=1.5,layer='REF-PROC-MINOR')
    c.sym += rect(400,275,404,330)
    minor += [line(395,275,400,275),line(395,330,400,330)]
    c.text('LG-901',410,337,size=2)
    c.sym += c.bubble(415,290,'LT','901')
    minor += [line(404,290,409,290)]
    c.sym += c.dcs(470,290,'LIC','901')
    c.sig += dashed(421,290,462,290)
    c.text('LEVEL CONTROL',505,279,size=1.8)
    c.sym += c.bubble(415,320,'LSHH','901')
    minor += [line(404,320,409,320)]
    c.sym += c.sis_box(500,320,'ESD','901')
    c.sig += dashed(421,320,492,320)
    c.text('CLOSE SDV-901',540,320,size=1.8)
    c.sig += dashed(508,320,522,320)
    c.text('EXTERNAL LEVEL BRIDLE',420,347,size=1.8)
    # Bottom liquid outlet and control valve; pipe trimmed around symbol.
    c.proc += pipe_run_v(320,170,209.5) + pipe_run_h(170,320,585,gaps=[(470,5)])
    c.sym += c.control_valve_h(470,170,w=10,h=6,tag='LV-901',fail='FC')
    c.text('LV-901 (FC)',470,154,size=2.0)
    c.sym += c.bubble(470,205,'FY','901')
    c.sig += dashed(470,282.5,470,211)
    c.sigp += pneu(470,199,470,182.5,spacing=4)
    c.proc += c.continuity_box_right(170,'080-LQ-9904 DN80','TO LIQUID SYSTEM - TBD','DEMO')
    c.flow_arrow_v(320,190,direction=-1,size=2); c.flow_arrow_h(400,170,size=2); c.flow_arrow_h(545,170,size=2)
    c.text('LIQUID OUTLET',390,179,size=2.0)
    c.text('DEMONSTRATION ONLY - ALL CONNECTIONS AND DATA SUBJECT TO ENGINEERING',335,75,size=2.2)
    for tag,dn,service in [('150-NG-9901',150,'GAS INLET'),('150-NG-9902',150,'GAS OUTLET'),('080-LQ-9904',80,'LIQUID OUTLET')]:
        c.register_line(tag,spec='TBD',service=service,dn=dn)
    c.register_line('XXX-FL-9903',spec='TBD',service='RELIEF; SIZE TBD',dn=0)
    c.schedule_lines[-1]['dn'] = None
    c.schedule_instruments = [i for i in c.schedule_instruments if i.get('type') != 'INTERLOCK LOGIC' or i.get('tag') != 'ESD-901']
    for instrument in c.schedule_instruments:
        if instrument.get('tag') == 'ESD/901':
            instrument['tag'] = 'ESD-901'
            instrument['reference_symbols'] = [{'type':'INTERLOCK LOGIC','x':163.5,'y':390}]
    c.schedule_instruments.append({'tag':'LG-901','type':'LEVEL GAUGE','x':402,'y':302.5})
    c.export_schedules(Path(__file__).with_name('pid_scrubber_demo.schedules.json'))
    layers = c.export_manifest(Path(__file__).with_name('pid_scrubber_demo.texts.json'))
    layers['REF-PROC-MINOR'] = comp(minor)
    return layers

if __name__ == '__main__':
    pid_scrubber_demo()
