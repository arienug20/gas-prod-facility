"""Versioned company A1 P&ID sheet furniture; presentation only."""
from dataclasses import dataclass

PROFILE_VERSION = 'gpf-pid-a1-1.0'


@dataclass(frozen=True)
class Revision:
    rev: str
    description: str
    date: str
    checked: str = 'TBD'
    approved: str = 'TBD'


def draw_sheet(ctx, *, line, rect, title, number, revisions, date,
               notes=(), legend=(), references=(), designed='TBD', drawn='CAD',
               checked='TBD', approved='TBD', sheet='1 OF 1', sheet_profile=None):
    """Render A1 frame and furniture on a PIDContext; revisions oldest first.

    Input is presentation metadata, not approval or engineering evidence.
    """
    if not 1 <= len(revisions) <= 6 or any(not isinstance(r, Revision) for r in revisions):
        raise ValueError('Berikan satu sampai enam revisi, urutan terlama dahulu')
    if len(notes) > 12 or len(legend) > 20 or len(references) > 4:
        raise ValueError('Isi furniture melampaui kapasitas lembar')
    if sheet_profile is None:
        sheet_profile = {'project':'GAS PRODUCTION FACILITY - ONSHORE FIELD', 'company':'PM OIL & GAS SURFACE FACILITY', 'consultant':'REKAYASA ENGINEERING'}
    if not isinstance(sheet_profile,dict) or any(not isinstance(sheet_profile.get(k),str) or not sheet_profile[k].strip() for k in ('project','company','consultant')):
        raise ValueError('sheet_profile wajib memuat project, company dan consultant')
    ctx.frame += rect(10, 7, 831, 587) + rect(20, 15, 823, 579)
    for i in range(1, 12):
        x = 20 + 803*i/12
        ctx.frame += [line(x,7,x,15), line(x,579,x,587)]
    for i in range(12):
        x = 20 + 803*(i+.5)/12
        ctx.text(str(i+1),x,11,size=2); ctx.text(str(i+1),x,583,size=2)
    for i in range(1,8):
        y=15+564*i/8
        ctx.frame += [line(10,y,20,y),line(823,y,831,y)]
    for i in range(8):
        y=579-564*(i+.5)/8
        ctx.text('ABCDEFGH'[i],15,y,size=2); ctx.text('ABCDEFGH'[i],827,y,size=2)
    ctx.frame.append(line(655,15,655,579))
    for y in (435,185,175,148): ctx.frame.append(line(655,y,823,y))
    for heading,y in [('NOTES',573),('LEGEND / SYMBOLS',429),('REFERENCE DRAWINGS',180)]: ctx.text(heading,739,y,size=2.3)
    for entries,start,step in ((notes,560,10),(legend,417,11),(references,169,5.5)):
        for i, entry in enumerate(entries): ctx.text(entry,659,start-i*step,size=1.8,left=True)
    for y in (116,120.6,125.2,129.8,134.4,139,143.6,96,74,60,48,36,25): ctx.title.append(line(655,y,823,y))
    for x in (675,763,795,809): ctx.title.append(line(x,116,x,148))
    ctx.title.append(line(739,15,739,60))
    for label,x in [('REV',665),('DESCRIPTION',719),('DATE',779),('CHK',802),('APP',816)]: ctx.text(label,x,145.8,size=1.8)
    for i,r in enumerate(revisions):
        y=118.3+4.6*i
        ctx.text(r.rev,665,y,size=1.8); ctx.text(r.description,678,y,size=1.8,left=True)
        ctx.text(r.date,779,y,size=1.8); ctx.text(r.checked,802,y,size=1.8); ctx.text(r.approved,816,y,size=1.8)
    ctx.text(sheet_profile['project'],739,108.5,size=2.8)
    ctx.text(sheet_profile['company'],739,102.5,size=2.2)
    ctx.text(sheet_profile['consultant'],739,98,size=2)
    ctx.text('PIPING & INSTRUMENTATION DIAGRAM',739,87,size=2.8)
    ctx.text(title,739,80,size=2.5)
    ctx.text('DRAWING NO:',658,70,size=1.8,left=True); ctx.text(number,739,65.5,size=2.5)
    for label,value,x,y in [('REV:',revisions[-1].rev,658,56.5),('SCALE:','NTS',742,56.5),('DATE:',date,658,44.5),('SHEET:',sheet,742,44.5),('DESIGNED:',designed,658,32.5),('DRAWN:',drawn,742,32.5),('CHECKED:',checked,658,21.5),('APPROVED:',approved,742,21.5)]:
        ctx.text(label,x,y,size=1.8,left=True); ctx.text(value,x+39,y-3.5,size=2.2)
