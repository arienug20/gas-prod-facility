"""Bounded directed connectivity checks on explicitly supplied semantic graph."""
from collections import deque
from .registry import audit_graph

VERSION = '1.0'


def check_connectivity(graph, requirements):
    """Check declared directed port-to-port paths; never infer connectivity from geometry.

    Each requirement has id, from_port, to_port and kind (process or signal).
    Only explicitly declared connections and object internal_links of matching kind
    are traversed. Unknown or malformed topology is never reported as a pass.
    """
    findings = audit_graph(graph)
    if any(f.get('severity') == 'error' for f in findings):
        return {'schema_version': VERSION, 'status': 'INVALID', 'findings': findings, 'checks': []}
    if not isinstance(graph, dict) or any(not isinstance(graph.get(k), list) for k in ('objects','ports','connections')):
        return {'schema_version': VERSION, 'status': 'INVALID', 'findings': findings, 'checks': []}
    if requirements is None or requirements == []:
        return {'schema_version': VERSION, 'status': 'NOT ASSESSED', 'findings': findings, 'checks': []}
    if not isinstance(requirements, list):
        findings.append({'rule':'connectivity.invalid_requirements','category':'graph','severity':'error','message':'Kebutuhan konektivitas harus berupa daftar.','object_ids':[]})
        return {'schema_version': VERSION, 'status': 'INVALID', 'findings': findings, 'checks': []}
    ports = {p['id']: p for p in graph['ports'] if isinstance(p,dict) and isinstance(p.get('id'),str)}
    edges = []
    known_ids = {item['id'] for section in ('objects','ports','connections') for item in graph[section] if isinstance(item,dict) and isinstance(item.get('id'),str)}
    for c in graph['connections']:
        if isinstance(c,dict): edges.append(c)
    for obj in graph['objects']:
        if not isinstance(obj,dict): continue
        links = obj.get('internal_links', [])
        if not isinstance(links,list):
            findings.append({'rule':'connectivity.invalid_internal_link','category':'graph','severity':'error','message':'internal_links harus berupa daftar.','object_ids':[obj.get('id')]})
            continue
        for link in links:
            if isinstance(link,dict) and isinstance(link.get('id'),str) and link['id'].strip() and link['id'] not in known_ids and isinstance(link.get('from_port'),str) and isinstance(link.get('to_port'),str) and link['from_port'] in ports and link['to_port'] in ports and link['from_port'] != link['to_port'] and ports[link['from_port']].get('owner_id') == obj.get('id') and ports[link['to_port']].get('owner_id') == obj.get('id') and link.get('kind') in ('signal','process') and ports[link['from_port']].get('port_kind') == link['kind'] and ports[link['to_port']].get('port_kind') == link['kind']:
                edges.append(link)
                known_ids.add(link['id'])
            else:
                findings.append({'rule':'connectivity.invalid_internal_link','category':'graph','severity':'error','message':'Koneksi internal tidak valid atau tidak memiliki pemilik yang sama.','object_ids':[obj.get('id')]})
    if any(f.get('severity') == 'error' for f in findings):
        return {'schema_version':VERSION,'status':'INVALID','findings':findings,'checks':[]}
    checks=[]; seen=set()
    for req in requirements:
        if not isinstance(req,dict) or not all(isinstance(req.get(k),str) and req[k].strip() for k in ('id','from_port','to_port','kind')) or req['id'] in seen or req['kind'] not in ('process','signal') or req['from_port'] not in ports or req['to_port'] not in ports or req['from_port'] == req['to_port']:
            checks.append({'id': req.get('id') if isinstance(req,dict) else None, 'status':'INVALID', 'path':[]}); continue
        seen.add(req['id']); kind=req['kind']
        queue=deque([(req['from_port'], [])]); visited={req['from_port']}; path=None
        while queue:
            current, route=queue.popleft()
            if current == req['to_port']: path=route; break
            for edge in edges:
                a,b=edge.get('from_port'),edge.get('to_port')
                if a != current or edge.get('kind') != kind or not isinstance(b,str) or b not in ports or b in visited: continue
                if ports[a].get('port_kind') != kind or ports[b].get('port_kind') != kind: continue
                if not isinstance(edge.get('id'),str) or not edge['id'].strip(): continue
                visited.add(b); queue.append((b,route+[edge['id']]))
        checks.append({'id':req['id'], 'status':'CONNECTED' if path is not None else 'MISSING', 'path':path or []})
    status = 'INVALID' if any(c['status']=='INVALID' for c in checks) else 'INCOMPLETE' if any(c['status']=='MISSING' for c in checks) else 'CHECKED'
    return {'schema_version':VERSION,'status':status,'findings':findings,'checks':checks}
