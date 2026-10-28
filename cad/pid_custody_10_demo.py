"""Standalone sour gas custody metering demonstration; conceptual only."""
from pathlib import Path
from cadgen import dxf
from pid_common import PIDContext, line, rect, dashed, pipe_run_h, pipe_run_v, comp
from metering_common import MeteringContext, DBB_HALF

@dxf
def pid_custody_10_demo():
    c=MeteringContext()
    c.frame += rect(10,7,831,587)+rect(20,15,823,579)
    for i in range(1,12):
        x=20+(823-20)*i/12; c.frame += [line(x,7,x,15),line(x,579,x,587)]
    for i in range(12):
        x=20+(823-20)*(i+.5)/12; c.text(str(i+1),x,11,size=2); c.text(str(i+1),x,583,size=2)
    for i in range(1,8):
        y=15+(579-15)*i/8; c.frame += [line(10,y,20,y),line(823,y,831,y)]
    for i in range(8):
        y=579-(579-15)*(i+.5)/8; c.text('ABCDEFGH'[i],15,y,size=2); c.text('ABCDEFGH'[i],827,y,size=2)
    c.frame += [line(655,15,655,579),line(655,435,823,435),line(655,567,823,567),line(655,195,823,195),line(655,148,823,148),line(655,116,823,116)]
    c.text('NOTES',739,573,size=2.5)
    notes=[
      '1. CONCEPT DEMONSTRATION ONLY - NOT FOR CONSTRUCTION.',
      '2. 10 MMSCFD AT STANDARD CONDITIONS: BASE P/T TBD.',
      '3. GAS MOL%: CH4 90; C2H6 5; C3H8 3; H2S 1; N2 1.',
      '   H2S 1 MOL% = 10,000 PPM IN THE PROCESS GAS.',
      '4. SOUR SERVICE: MATERIALS, WET PHASE AND H2S PARTIAL',
      '   PRESSURE REVIEW TO ISO 15156 APPLICABILITY: TBD.',
      '5. PIPE / METER SIZE, OPERATING P/T AND CALIBRATION TBD.',
      '6. CUSTODY REQUIREMENTS, UNCERTAINTY AND PROVING TBD.',
      '7. GC COMPOSITION / H2S CAPABILITY AND SAMPLE CONDITIONING',
      '   REQUIRE VENDOR CONFIRMATION; SAMPLE DISPOSAL TBD.',
      '8. METER RUN STRAIGHT LENGTHS AND CONDITIONER TBD.',
      '9. SAMPLE, DBB BLEEDS: CONTAINED DISPOSAL DESIGN TBD.',
      '10. TAGS AND LINE NUMBERS ARE DEMO; OUTSIDE GPF BASIS.',
      '11. SCHEMATIC ONLY; NO ENGINEERING APPROVAL.',
    ]
    for i,t in enumerate(notes): c.text(t,659,560-i*7,size=1.8,left=True)
    c.text('LEGEND / DATA STATUS',739,425,size=2.5)
    for i,t in enumerate(['SOLID = PROCESS / IMPULSE', 'DASHED = ELECTRICAL SIGNAL', 'CIRCLE = FIELD INSTRUMENT', 'CIRCLE IN SQUARE = FLOW COMPUTER', 'DBB = DOUBLE BLOCK AND BLEED', 'TBD = TO BE DETERMINED', 'MATERIAL / PRESSURE CLASS: TBD']): c.text(t,659,412-i*8,size=1.8,left=True)
    c.text('REFERENCE DOCUMENTS',739,187,size=2.3)
    c.text('GPF-00-DB-0001: PROJECT DESIGN BASIS',659,176,size=1.8,left=True)
    c.text('GPF-00-PI-PID-0001: P&ID REFERENCE',659,169,size=1.8,left=True)
    c.text('REV     DESCRIPTION                         DATE',659,141,size=1.8,left=True)
    c.text('A0       INITIAL CONCEPT DEMO       28 OCT 2026',659,128,size=1.8,left=True)
    for y in (96,74,60,48,36,25): c.title.append(line(655,y,823,y))
    c.title.append(line(739,15,739,60))
    c.text('GAS PRODUCTION FACILITY - ONSHORE FIELD',739,106,size=2.5)
    c.text('PIPING & INSTRUMENTATION DIAGRAM',739,86,size=2.5)
    c.text('CUSTODY GAS METER - DEMONSTRATION',739,79,size=2.3)
    c.text('GPF-DEMO-PID-METER-10',739,66,size=2.5)
    c.text('REV A0',695,53,size=2.2); c.text('NTS',780,53,size=2.2)
    c.text('28 OCT 2026',695,41,size=2); c.text('SHEET 1 OF 1',780,41,size=2)
    c.text('DRAWN: CAD',695,29,size=2); c.text('CHECKED: TBD',780,29,size=2)
    c.text('APPROVED: TBD',780,19,size=2)

    c.frame += rect(45,485,605,565)
    c.text('DESIGN INFORMATION - CONCEPT BASIS',50,557,size=2.5,left=True)
    data=['SERVICE: SOUR GAS / CUSTODY MEASUREMENT; FLOW 10 MMSCFD (BASE TBD)',
          'MOL% CH4 90 | C2H6 5 | C3H8 3 | H2S 1 | N2 1',
          'P/T, MOISTURE, DEW POINT, LINE CLASS AND MATERIALS: TBD',
          'USM NOMINAL SIZE, RANGE, STRAIGHT RUN AND CALIBRATION: TBD',
          'METER SELECTION / REDUNDANCY / FLOW COMPUTER SPECIFICATION: TBD',
          'CONTRACTUAL REQUIREMENTS AND UNCERTAINTY ALLOCATION: TBD']
    for i,t in enumerate(data): c.text(t,50,547-i*9,size=2,left=True)

    # One conceptual USM run with bounded, capped DBB bleed connections.
    c.proc += c.continuity_box_left(320,'XXX-MT-9101 DN TBD','FROM SOUR GAS SUPPLY','DEMO')
    c.proc += pipe_run_h(320,72.5,585,gaps=[(190,DBB_HALF),(300,22),(525,DBB_HALF)])
    c.dbb_valve_h(190,320,tag='DBB-9101'); c.dbb_valve_h(525,320,tag='DBB-9102')
    c.usm_meter_run(300,320,tag='USM-9101',fe_pair=('FT','9101'),fqi_pair=('FQI','9101'))
    c.text('ULTRASONIC METER - SIZE TBD',300,300,size=2.2)
    c.text('SINGLE RUN SHOWN; REDUNDANCY TBD',300,288,size=2)
    c.text('METER PATHS / CONDITIONER ILLUSTRATIVE',300,280,size=1.8)
    c.text('XXX-MT-9101 / SPEC TBD',150,308,size=1.8)
    c.text('XXX-MT-9102 / SPEC TBD',480,308,size=1.8)
    c.proc += c.continuity_box_right(320,'XXX-MT-9102 DN TBD','TO GAS RECEIVER - TBD','DEMO')
    for x in (100,150,245,360,460,565): c.flow_arrow_h(x,320,size=2)

    # Pressure and temperature inputs to FQI; conceptual instrument taps.
    minor=[]
    minor += pipe_run_v(395,320,349)
    c.sym += c.bubble(395,355,'PT','9101')
    c.sig += dashed(389,355,307.5,355)
    minor += pipe_run_v(470,320,384)
    c.sym += c.bubble(470,390,'TT','9101')
    c.sig += dashed(464,390,300,390)+dashed(300,390,300,367.5)
    c.text('P / T INPUTS TO FLOW COMPUTER',455,410,size=1.8)

    # Analyzer package is conceptual: no assumed fast loop or vent routing.
    minor += pipe_run_v(120,225,320,gaps=[(270,5)])
    c.sym += c.valve_gate_v(120,270,w=6,h=10,tag='GV-9101')
    c.text('GV-9101',137,270,size=1.8)
    c.flow_arrow_v(120,250,direction=-1,size=2,layer='REF-PROC-MINOR')
    c.gc_analyzer(120,205,w=90,h=40,tag='AT-9101',comp_lines=('GC / ANALYZER PACKAGE','AT-9101   CAPABILITY TBD','SAMPLE CONDITIONING TBD','COMPOSITION TO FQI-9101'))
    minor += [line(120,185,120,160),line(118,160,122,160)]
    c.flow_arrow_v(120,173,direction=-1,size=2,layer='REF-PROC-MINOR')
    c.sym += [line(120,160,132,155),line(132,155,148,155)]
    c.text('CAPPED SAMPLE OUTLET; DESTINATION TBD',210,155,size=1.8)
    c.sig += dashed(165,205,260,205)
    c.sig += dashed(260,205,260,318.5) + dashed(260,321.5,260,360)
    c.sig += dashed(260,360,292.5,360)
    c.text('GC DATA TO FQI-9101',215,211,size=1.8)
    c.text('ISOLATED SAMPLE SYSTEM - DETAIL TBD',120,145,size=1.8)
    c.text('DEMONSTRATION ONLY - NOT FOR DESIGN OR CONSTRUCTION',340,75,size=2.2)
    for tag,svc in [('XXX-MT-9101','GAS INLET'),('XXX-MT-9102','METER OUTLET')]:
        c.register_line(tag,spec='TBD',service=svc,dn=0); c.schedule_lines[-1]['dn']=None
    for item in c.schedule_equipment:
        if item.get('tag') == 'AT-9101':
            item['type'] = 'GAS ANALYZER PACKAGE - COMPOSITION AND H2S CAPABILITY TBD'
        elif item.get('tag') == 'USM-9101':
            item['type'] = 'ULTRASONIC GAS METER - SIZE AND CUSTODY QUALIFICATION TBD'
            item['symbol_length_sheet_mm'] = item.pop('length')
            item['physical_length'] = None
            item['conditioner'] = None
            item['paths'] = None
    for item in c.schedule_valves:
        if item.get('tag') in ('DBB-9101','DBB-9102'):
            item['type'] = 'DOUBLE BLOCK AND BLEED - QUALIFICATION TBD'
    c.export_schedules(Path(__file__).with_name('pid_custody_10_demo.schedules.json'))
    layers=c.export_manifest(Path(__file__).with_name('pid_custody_10_demo.texts.json'))
    layers['REF-PROC-MINOR']=comp(minor)
    return layers

if __name__=='__main__': pid_custody_10_demo()
