import copy
import unittest
from .pid_sheet_profile import Revision, draw_sheet
from .roadmap_foundation.connectivity import check_connectivity


class Context:
    def __init__(self): self.frame=[]; self.title=[]; self.texts=[]
    def text(self, value, x, y, **kwargs): self.texts.append((value,x,y,kwargs))


def segment(*args): return args
def rectangle(*args): return [args]


def fixture():
    objects=[{'id':x,'kind':'instrument'} for x in ('gc','pt','fqi')]
    ports=[{'id':x,'owner_id':owner,'port_kind':'signal','service_ref':'test'} for x,owner in [('gc.out','gc'),('pt.out','pt'),('fqi.gc','fqi'),('fqi.pt','fqi')]]
    connections=[{'id':'gc-link','from_port':'gc.out','to_port':'fqi.gc','kind':'signal'}, {'id':'pt-link','from_port':'pt.out','to_port':'fqi.pt','kind':'signal'}]
    requirements=[{'id':'gc-to-fqi','from_port':'gc.out','to_port':'fqi.gc','kind':'signal'}, {'id':'pt-to-fqi','from_port':'pt.out','to_port':'fqi.pt','kind':'signal'}]
    return {'schema_version':'1.0','objects':objects,'ports':ports,'connections':connections},requirements


class SheetTests(unittest.TestCase):
    def test_furniture_revision_and_empty_approval(self):
        c=Context(); draw_sheet(c,line=segment,rect=rectangle,title='TEST',number='TEST-1',date='TBD',revisions=[Revision('A0','INITIAL','TBD'),Revision('A1','CHANGE','TBD')])
        self.assertTrue(c.frame and c.title)
        self.assertIn(('A1',697,53.0,{'size':2.2}),c.texts)
        self.assertTrue(any(t[0]=='APPROVED:' for t in c.texts))
        self.assertTrue(any(t[0]=='TBD' for t in c.texts))
    def test_capacity_fails_before_modifying_context(self):
        c=Context()
        with self.assertRaises(ValueError): draw_sheet(c,line=segment,rect=rectangle,title='x',number='y',date='z',revisions=[])
        self.assertFalse(c.frame)


class ConnectivityTests(unittest.TestCase):
    def test_required_paths_and_missing_leg(self):
        graph,req=fixture(); before=copy.deepcopy(graph)
        result=check_connectivity(graph,req)
        self.assertEqual(result['status'],'CHECKED'); self.assertEqual(result['checks'][0]['path'],['gc-link'])
        graph['connections'].pop(); self.assertEqual(check_connectivity(graph,req)['status'],'INCOMPLETE')
        self.assertEqual(before['connections'][0],graph['connections'][0])
    def test_wrong_direction_and_crossing_do_not_connect(self):
        graph,req=fixture(); graph['connections'][0]['from_port'],graph['connections'][0]['to_port']=graph['connections'][0]['to_port'],graph['connections'][0]['from_port']
        graph['lines']=[{'crossing':True}]
        self.assertEqual(check_connectivity(graph,req)['checks'][0]['status'],'MISSING')
    def test_missing_and_invalid_requirements_never_pass(self):
        graph,req=fixture()
        self.assertEqual(check_connectivity(graph,[])['status'],'NOT ASSESSED')
        req[0]['to_port']='missing'
        self.assertEqual(check_connectivity(graph,req)['status'],'INVALID')
    def test_incompatible_endpoint_invalidates_audit(self):
        graph,req=fixture(); graph['ports'][0]['port_kind']='process'
        self.assertEqual(check_connectivity(graph,req)['status'],'INVALID')
    def test_malformed_requirements_and_internal_links_are_invalid(self):
        graph,req=fixture()
        self.assertEqual(check_connectivity(graph, {'bad': 'input'})['status'],'INVALID')
        graph['objects'][0]['internal_links']=[{'id':'broken','from_port':'gc.out','to_port':'missing','kind':'signal'}]
        result=check_connectivity(graph,req)
        self.assertEqual(result['status'],'INVALID')
        self.assertTrue(any(f['rule']=='connectivity.invalid_internal_link' for f in result['findings']))
    def test_internal_link_identity_and_kind_checked(self):
        graph,req=fixture()
        graph['ports'].append({'id':'gc.in','owner_id':'gc','port_kind':'signal','service_ref':'test'})
        graph['objects'][0]['internal_links']=[{'id':'gc-link','from_port':'gc.in','to_port':'gc.out','kind':'signal'}]
        self.assertEqual(check_connectivity(graph,req)['status'],'INVALID')
        graph['objects'][0]['internal_links'][0].update(id='internal',kind='process')
        self.assertEqual(check_connectivity(graph,req)['status'],'INVALID')
        graph['objects'][0]['internal_links'][0]['kind']='signal'
        self.assertEqual(check_connectivity(graph,req)['status'],'CHECKED')


if __name__=='__main__': unittest.main()
