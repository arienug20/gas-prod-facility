"""Project-scoped inputs; paths are relative to the configuration file."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO / 'project.gpf.json'


@dataclass(frozen=True)
class Project:
    config_path: Path
    project_id: str
    cad_dir: Path
    registry: Path
    basis: Path
    basis_format: str
    hmb: Path | None
    numbering: dict
    consistency: dict
    sheet_profile: dict

    @property
    def hmb_status(self):
        return 'NOT PROVIDED' if self.hmb is None else 'AVAILABLE' if self.hmb.is_file() else 'MISSING'


def load_project(path=None):
    if path is None and not Path.cwd().resolve().is_relative_to(REPO):
        raise ValueError('Di luar repo GPF, tentukan --project secara eksplisit; basis GPF tidak dipilih otomatis')
    source = Path(path or DEFAULT_CONFIG).resolve()
    try:
        data = json.loads(source.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError(f'Konfigurasi proyek tidak dapat dibaca: {source}: {exc}') from exc
    if not isinstance(data, dict) or data.get('schema_version') != '1.0':
        raise ValueError('schema_version konfigurasi proyek harus 1.0')
    def string(value, name):
        if not isinstance(value, str) or not value.strip(): raise ValueError(f'{name} harus berupa string yang tidak kosong')
        return value
    def location(value, name):
        return (source.parent / string(value, name)).resolve()
    basis = data.get('design_basis')
    if not isinstance(basis,dict): raise ValueError('design_basis proyek wajib tersedia')
    fmt = string(basis.get('format'),'design_basis.format')
    if fmt not in ('gpf-markdown-v1','register-json-v1'):
        raise ValueError(f'Format design basis {fmt!r} belum didukung; pemetaan diperlukan')
    numbering = data.get('numbering')
    if not isinstance(numbering,dict): raise ValueError('numbering proyek wajib tersedia')
    for key, groups in (('document_regex',0),('tag_regex',2),('line_regex',1)):
        try: pattern = re.compile(string(numbering.get(key),f'numbering.{key}'))
        except re.error as exc: raise ValueError(f'numbering.{key} tidak valid: {exc}') from exc
        if pattern.groups != groups: raise ValueError(f'numbering.{key} wajib memiliki {groups} capture group')
    rules = data.get('consistency')
    if not isinstance(rules,dict) or not isinstance(rules.get('core_files'),list) or not all(isinstance(x,str) and x for x in rules['core_files']):
        raise ValueError('consistency.core_files wajib berupa daftar nama drawing')
    scopes = rules.get('equipment_scope',{})
    if not isinstance(scopes,dict) or any(not isinstance(v,list) or not all(isinstance(x,str) and x for x in v) for v in scopes.values()):
        raise ValueError('consistency.equipment_scope tidak valid')
    pid = rules.get('unknown_tags_pid')
    if pid is not None and (not isinstance(pid,str) or not pid.strip()): raise ValueError('unknown_tags_pid tidak valid')
    profile = data.get('sheet_profile')
    if not isinstance(profile,dict) or any(not isinstance(profile.get(k),str) or not profile[k].strip() for k in ('project','company','consultant')):
        raise ValueError('sheet_profile wajib memuat project, company dan consultant')
    hmb = data.get('hmb')
    if hmb is not None and not isinstance(hmb,dict): raise ValueError('hmb harus null atau objek dengan file')
    project_id = string(data.get('project_id'),'project_id')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', project_id):
        raise ValueError('project_id hanya boleh berisi huruf, angka, underscore, atau tanda hubung')
    if not rules['core_files']:
        raise ValueError('consistency.core_files tidak boleh kosong: cakupan belum ditentukan')
    return Project(source,project_id,location(data.get('cad_dir'),'cad_dir'),location(data.get('documents_registry'),'documents_registry'),location(basis.get('file'),'design_basis.file'),fmt,None if hmb is None else location(hmb.get('file'),'hmb.file'),numbering,rules,profile)


def load_register_json(path):
    """Load explicitly mapped project registers; do not guess from arbitrary documents."""
    try: data = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc: raise ValueError(f'Design basis tidak dapat dibaca: {exc}') from exc
    if not isinstance(data,dict) or data.get('schema_version') != '1.0': raise ValueError('Design basis register-json-v1 memerlukan schema_version 1.0')
    for name, key in (('equipment','tag'),('lines','line_no'),('instruments','tag')):
        rows = data.get(name)
        if not isinstance(rows,list) or any(not isinstance(r,dict) or not isinstance(r.get(key),str) or not r[key].strip() for r in rows):
            raise ValueError(f'Design basis memerlukan daftar {name} dengan {key} eksplisit')
        if len({r[key] for r in rows}) != len(rows): raise ValueError(f'Duplikasi {key} pada {name}')
    if not any(data[name] for name in ('equipment','lines','instruments')):
        raise ValueError('Design basis tidak berisi register; pemetaan dan kelengkapan perlu ditinjau')
    for row in data['lines']:
        if isinstance(row.get('dn'),bool) or not isinstance(row.get('dn'),int) or row['dn'] <= 0: raise ValueError('DN line harus bilangan bulat positif')
    if not isinstance(data.get('meta'),dict) or not isinstance(data['meta'].get('doc_no'),str) or not data['meta']['doc_no'].strip(): raise ValueError('meta.doc_no wajib tersedia')
    if 'rev' in data['meta'] and not isinstance(data['meta']['rev'],str): raise ValueError('meta.rev harus berupa string')
    return data
