import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.project_config import load_project
from cad.pid_sheet_profile import Revision, draw_sheet
from cad.roadmap_foundation.standards import build_baseline

ROOT = Path(__file__).resolve().parents[1]


def write(path, data):
    path.write_text(json.dumps(data), encoding='utf-8')


class ProjectScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'drawings').mkdir()
        self.config = {
            'schema_version':'1.0','project_id':'OTHER','cad_dir':'drawings','documents_registry':'registry.json',
            'design_basis':{'file':'basis.json','format':'register-json-v1'}, 'hmb':None,
            'numbering':{'document_regex':r'XYZ-\d{4}','tag_regex':r'\b([A-Z]+)-(\d{3})\b','line_regex':r'\b(\d{3}-[A-Z]{2}-\d{4})\b'},
            'consistency':{'core_files':['drawing'],'equipment_scope':{'drawing':['V-777']},'unknown_tags_pid':'drawing'},
            'sheet_profile':{'project':'OTHER PROJECT','company':'OTHER OWNER','consultant':'OTHER CONSULTANT'}}
        write(self.root/'project.json',self.config)
        write(self.root/'basis.json',{'schema_version':'1.0','meta':{'doc_no':'XYZ-0001','rev':'A0'},'equipment':[{'tag':'V-777','description':'OTHER VESSEL'}],'lines':[{'line_no':'999-GO-7777','dn':80}], 'instruments':[{'tag':'PT-777'}]})
        write(self.root/'registry.json',{'documents':[{'file':'drawing','doc_no':'XYZ-0002','type':'P&ID','sheet':'A1'}], 'design_basis':{'doc_no':'XYZ-0001'}})
        write(self.root/'drawings'/'drawing.texts.json',{'texts':[{'t':t,'x':0,'y':0} for t in ('XYZ-0002','V-777','PT-777','999-GO-7777 DN80','A0')]})

    def tearDown(self): self.temp.cleanup()

    def run_tool(self, name, *args):
        return subprocess.run([sys.executable,str(ROOT/'tools'/name),'--project',str(self.root/'project.json'),*map(str,args)],capture_output=True,text=True)

    def test_checker_and_workbook_use_only_selected_project(self):
        check=self.run_tool('consistency_check.py','--json')
        self.assertEqual(check.returncode,0,check.stdout+check.stderr)
        data=json.loads(check.stdout)
        self.assertEqual(data['project_id'],'OTHER'); self.assertEqual(data['hmb']['status'],'NOT PROVIDED')
        self.assertEqual(data['design_basis'],{'equipment':1,'lines':1,'instruments':1})
        self.assertNotIn('GPF-',check.stdout)
        out=self.root/'other.xlsx'; result=self.run_tool('export_xlsx.py','-o',out)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        from openpyxl import load_workbook
        wb=load_workbook(out,data_only=True)
        self.assertEqual(wb['Equipment Register']['A2'].value,'V-777')
        self.assertEqual(wb['Line List']['A2'].value,'999-GO-7777')
        self.assertEqual(wb['Instrument Index']['B2'].value,'PT-777')
        self.assertEqual(wb['Register Dokumen']['A2'].value,'XYZ-0002')

    def test_missing_basis_and_unmapped_format_fail(self):
        (self.root/'basis.json').unlink()
        for tool in ('consistency_check.py','export_xlsx.py'):
            result=self.run_tool(tool,'-o',self.root/'missing.xlsx') if tool=='export_xlsx.py' else self.run_tool(tool)
            self.assertNotEqual(result.returncode,0,result.stdout)
        self.assertFalse((self.root/'missing.xlsx').exists())
        self.config['design_basis']['format']='unknown'; write(self.root/'project.json',self.config)
        self.assertNotEqual(self.run_tool('consistency_check.py').returncode,0)

    def test_unmapped_and_empty_registers_fail_without_export(self):
        for data in ({'schema_version':'1.0'}, {'schema_version':'1.0','meta':{'doc_no':'XYZ-0001'},'equipment':[],'lines':[],'instruments':[]}):
            write(self.root/'basis.json',data)
            self.assertNotEqual(self.run_tool('consistency_check.py').returncode,0)
            out=self.root/'empty.xlsx'
            self.assertNotEqual(self.run_tool('export_xlsx.py','-o',out).returncode,0)
            self.assertFalse(out.exists())

    def test_mismatched_basis_identity_fails(self):
        basis=json.loads((self.root/'basis.json').read_text())
        basis['meta']['doc_no']='XYZ-9999'; write(self.root/'basis.json',basis)
        self.assertNotEqual(self.run_tool('consistency_check.py').returncode,0)
        result=self.run_tool('export_xlsx.py','-o',self.root/'mismatch.xlsx')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.root/'mismatch.xlsx').exists())

    def test_invalid_or_missing_config_does_not_fall_back(self):
        self.config['schema_version']='99'; write(self.root/'project.json',self.config)
        self.assertNotEqual(self.run_tool('consistency_check.py').returncode,0)
        (self.root/'project.json').unlink()
        self.assertNotEqual(self.run_tool('export_xlsx.py').returncode,0)

    def test_outside_repo_requires_project_and_sources_are_protected(self):
        result=subprocess.run([sys.executable,str(ROOT/'tools'/'consistency_check.py')],cwd=self.root,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        original=(self.root/'basis.json').read_bytes()
        result=self.run_tool('export_xlsx.py','-o',self.root/'basis.json')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((self.root/'basis.json').read_bytes(),original)

    def test_alternate_tag_convention_is_not_rewritten(self):
        self.config['numbering']['tag_regex']=r'\b([A-Z]+)(\d{3})\b'
        self.config['consistency']['equipment_scope']={'drawing':['V777']}
        write(self.root/'project.json',self.config)
        basis=json.loads((self.root/'basis.json').read_text())
        basis['equipment'][0]['tag']='V777'; basis['instruments'][0]['tag']='PT777'
        write(self.root/'basis.json',basis)
        write(self.root/'drawings'/'drawing.texts.json',{'texts':[{'t':t,'x':0,'y':0} for t in ('XYZ-0002','V777','PT777','999-GO-7777 DN80','A0')]})
        result=self.run_tool('consistency_check.py','--json')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_other_project_is_not_subject_to_gpf_tag_exclusions(self):
        self.config['numbering']['tag_regex']=r'\b([A-Z]{1,4}(?:/[A-Z]{1,4})?)-(\d{3}[A-Z]?)\b'
        self.config['consistency']['equipment_scope']={'drawing':['GPF-777']}
        write(self.root/'project.json',self.config)
        basis=json.loads((self.root/'basis.json').read_text())
        basis['equipment'][0]['tag']='GPF-777'; write(self.root/'basis.json',basis)
        write(self.root/'drawings'/'drawing.texts.json',{'texts':[{'t':t,'x':0,'y':0} for t in ('XYZ-0002','GPF-777','PT-777','999-GO-7777 DN80','A0')]})
        result=self.run_tool('consistency_check.py','--json')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_hmb_and_baseline_scoped_to_project(self):
        self.config['hmb']={'file':'hmb.csv'}; write(self.root/'project.json',self.config)
        project=load_project(self.root/'project.json')
        self.assertEqual(project.hmb_status,'MISSING')
        report=build_baseline(ROOT,self.root/'project.json')
        self.assertEqual(report['project']['id'],'OTHER')
        self.assertEqual(report['project']['hmb_status'],'MISSING')
        self.assertTrue(any(x['path']==str(self.root/'basis.json') for x in report['artifacts']))
        self.assertFalse(any(x['path']=='dokumen/01-design-basis.md' for x in report['artifacts']))
        (self.root/'hmb.csv').write_text('stream,value\n',encoding='utf-8')
        self.assertEqual(load_project(self.root/'project.json').hmb_status,'AVAILABLE')

    def test_sheet_profile_does_not_write_gpf_identity(self):
        class Context:
            def __init__(self): self.frame=[]; self.title=[]; self.values=[]
            def text(self,value,*args,**kwargs): self.values.append(value)
        c=Context()
        draw_sheet(c,line=lambda *p:p,rect=lambda *p:[p],title='TITLE',number='XYZ-0002',date='-',revisions=[Revision('A0','TEST','-')],sheet_profile=load_project(self.root/'project.json').sheet_profile)
        self.assertIn('OTHER PROJECT',c.values)
        self.assertNotIn('GAS PRODUCTION FACILITY - ONSHORE FIELD',c.values)


if __name__=='__main__': unittest.main()
