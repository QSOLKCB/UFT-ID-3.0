#!/usr/bin/env python3
"""Fail-closed validation for the UFT-ID 3.0 historical lineage registry."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
P={k:ROOT/v for k,v in {
'contract':'machine/historical_lineage_contract.json','sources':'machine/historical_sources.json',
'symbols':'machine/historical_symbols.json','conflicts':'machine/historical_conflicts.json',
'results':'machine/historical_results.json','inheritance':'machine/methodological_inheritance.json',
'human':'research/HISTORICAL_LINEAGE.md'}.items()}
REQ_PLAT={'academia','zenodo','authorea','google-drive','github','archived-copy'}
RESULT_CLASSES={'formal','computational','empirical','interpretive','speculative'}
CLAIM_CLASSES={'DEFINITION','THEOREM_TARGET','PROVED','COUNTEREXAMPLE','DIAGNOSTIC','EMPIRICAL','INTERPRETIVE','SPECULATIVE','NONCLAIM'}
DOI=re.compile(r'^10\.\d{4,9}/\S+$'); H40=re.compile(r'^[0-9a-f]{40}$'); H64=re.compile(r'^[0-9a-f]{64}$')
def load(path:Path)->dict[str,Any]:
    x=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(x,dict): raise ValueError(f'{path} must contain an object')
    return x
def ne(x:object)->bool: return isinstance(x,str) and bool(x.strip())
def sl(x:object,label:str,e:list[str],nonempty=False)->list[str]:
    if not isinstance(x,list): e.append(f'{label} must be a list'); return []
    if nonempty and not x: e.append(f'{label} must be non-empty')
    out=[]
    for i,v in enumerate(x):
        if not ne(v): e.append(f'{label}[{i}] must be a non-empty string')
        else: out.append(v)
    if len(out)!=len(set(out)): e.append(f'{label} must not contain duplicates')
    return out
def valid_hash(h:object,label:str,e:list[str])->None:
    if not isinstance(h,dict): e.append(f'{label} must be object'); return
    a,v,scope=h.get('algorithm'),h.get('value'),h.get('scope')
    if not ne(scope): e.append(f'{label}.scope required')
    if a=='sha256':
        if not isinstance(v,str) or not H64.fullmatch(v): e.append(f'{label}.value invalid sha256')
    elif a=='git-blob-sha1':
        if not isinstance(v,str) or not H40.fullmatch(v): e.append(f'{label}.value invalid git blob sha')
    else: e.append(f'{label}.algorithm unsupported')
def validate()->dict[str,Any]:
    e=[]
    for n,p in P.items():
        if not p.is_file(): e.append(f'missing {n}: {p.relative_to(ROOT)}')
    if e:return {'status':'error','errors':e,'exit_criterion_met':False}
    c,s,sy,co,r,inh=(load(P[k]) for k in ('contract','sources','symbols','conflicts','results','inheritance'))
    if c.get('type')!='uft-id-historical-lineage-contract' or c.get('schema_version')!='1.0.0':e.append('contract type/schema mismatch')
    if set(c.get('required_platform_families',[]))!=REQ_PLAT:e.append('contract platform families mismatch')
    if set(c.get('result_classes',[]))!=RESULT_CLASSES:e.append('contract result classes mismatch')
    hard=c.get('hard_rules')
    if not isinstance(hard,dict) or not hard or any(v is not False for v in hard.values()):e.append('contract hard rules must all be false')
    auth=c.get('authorities',{})
    if not isinstance(auth,dict):e.append('contract authorities missing')
    else:
        for _,rel in auth.items():
            if not ne(rel) or not (ROOT/rel).is_file():e.append(f'contract authority missing: {rel}')
    if s.get('type')!='uft-id-historical-source-registry':e.append('source registry type mismatch')
    cc=s.get('completeness_contract',{}); req=set(cc.get('required_platform_families',[]))
    if req!=REQ_PLAT:e.append('source required platform families mismatch')
    cov=cc.get('platform_coverage',[]); cov_names=[x.get('platform') for x in cov if isinstance(x,dict)]
    if set(cov_names)!=REQ_PLAT or len(cov_names)!=len(REQ_PLAT):e.append('platform coverage must contain all six families exactly once')
    source_ids=set(); hist_ids=set()
    for i,x in enumerate(s.get('sources',[])):
        q=f'sources[{i}]'
        if not isinstance(x,dict):e.append(f'{q} must be object');continue
        sid=x.get('source_id')
        if not ne(sid):e.append(f'{q}.source_id required');continue
        if sid in source_ids:e.append(f'duplicate source_id {sid}')
        source_ids.add(sid)
        if sid.startswith('UFT-HIST-'):hist_ids.add(sid)
        for f in ('title','source_family','date_kind','peer_review_status'):
            if not ne(x.get(f)):e.append(f'{sid}.{f} required')
        doi=x.get('doi')
        if doi is not None and (not isinstance(doi,str) or not DOI.fullmatch(doi)):e.append(f'{sid}.doi invalid')
        lic=x.get('license')
        if not isinstance(lic,dict) or 'value' not in lic or not ne(lic.get('status')):e.append(f'{sid}.license invalid')
        mans=x.get('manifestations',[])
        if not isinstance(mans,list) or not mans:e.append(f'{sid}.manifestations required');continue
        for j,m in enumerate(mans):
            ml=f'{sid}.manifestations[{j}]'
            if not isinstance(m,dict):e.append(f'{ml} must be object');continue
            plat=m.get('platform')
            if plat not in REQ_PLAT:e.append(f'{ml}.platform invalid')
            for f in ('locator','role','status'):
                if not ne(m.get(f)):e.append(f'{ml}.{f} required')
            loc=str(m.get('locator',''))
            if 'gmail:' in loc or 'docs.google.com' in loc or 'drive.google.com' in loc or loc.startswith('gdrive:'):e.append(f'{ml} leaks private connector identifier')
            if isinstance(m.get('receipt_id'),str) and m['receipt_id'].startswith('gmail:'):e.append(f'{ml} leaks private Gmail receipt id')
            if m.get('hash') is not None:valid_hash(m['hash'],f'{ml}.hash',e)
            if plat=='github':
                b=m.get('blob_sha')
                if m.get('ref')!='main' or not isinstance(b,str) or not H40.fullmatch(b):e.append(f'{ml} invalid merged-main blob pin')
                if isinstance(m.get('hash'),dict) and m['hash'].get('value')!=b:e.append(f'{ml} hash/blob mismatch')
            if plat=='google-drive':
                if m.get('private_locator_redacted') is not True:e.append(f'{ml} Drive locator must be redacted')
                if m.get('hash') is not None and m.get('native_hash_available') is not False:e.append(f'{ml} export hash must not pose as native cloud hash')
    symbols=sy.get('symbols',[]); seen=set()
    for i,x in enumerate(symbols):
        h=x.get('historical_symbol') if isinstance(x,dict) else None
        if not ne(h):e.append(f'symbols[{i}].historical_symbol required');continue
        if h in seen:e.append(f'duplicate historical symbol {h}')
        seen.add(h)
        refs=sl(x.get('source_ids'),f'{h}.source_ids',e,True)
        if set(refs)-source_ids:e.append(f'{h} has unknown source ids')
        if x.get('disposition') not in {'mapped','mapped-with-semantic-narrowing','mapped-as-specialization','superseded','symbol-conflict'}:e.append(f'{h} invalid disposition')
        if x.get('disposition')!='superseded' and not ne(x.get('canonical_target')):e.append(f'{h} canonical_target required')
        sl(x.get('not_inherited'),f'{h}.not_inherited',e,True)
    conflict_ids=set()
    for i,x in enumerate(co.get('conflicts',[])):
        if not isinstance(x,dict):e.append(f'conflicts[{i}] must be object');continue
        cid=x.get('conflict_id')
        if not ne(cid):e.append(f'conflicts[{i}].conflict_id required');continue
        if cid in conflict_ids:e.append(f'duplicate conflict {cid}')
        conflict_ids.add(cid)
        refs=sl(x.get('source_ids'),f'{cid}.source_ids',e,True)
        if set(refs)-source_ids:e.append(f'{cid} has unknown source ids')
        if not ne(x.get('historical_definition')) or not ne(x.get('current_definition')):e.append(f'{cid} must preserve both definitions')
        if x.get('resolution')!='do-not-reconcile-silently':e.append(f'{cid} must remain do-not-reconcile-silently')
    covered=set(); result_ids=set()
    for i,x in enumerate(r.get('results',[])):
        if not isinstance(x,dict):e.append(f'results[{i}] must be object');continue
        rid=x.get('result_id')
        if not ne(rid):e.append(f'results[{i}].result_id required');continue
        if rid in result_ids:e.append(f'duplicate result {rid}')
        result_ids.add(rid)
        cls=x.get('result_class')
        if cls not in RESULT_CLASSES:e.append(f'{rid} invalid result class')
        refs=sl(x.get('source_ids'),f'{rid}.source_ids',e,True); covered.update(refs)
        if set(refs)-source_ids:e.append(f'{rid} has unknown source ids')
        if cls=='empirical' and not x.get('evidence_paths'):e.append(f'{rid} empirical result requires evidence_paths')
    missing=hist_ids-covered
    if missing:e.append(f'historical sources lack classified-result coverage: {sorted(missing)}')
    imports=inh.get('imports',[]); inherit_ids=set()
    for i,x in enumerate(imports):
        if not isinstance(x,dict):e.append(f'imports[{i}] must be object');continue
        iid=x.get('inheritance_id')
        if not ne(iid):e.append(f'imports[{i}].inheritance_id required');continue
        inherit_ids.add(iid)
        if x.get('claim_class') not in CLAIM_CLASSES:e.append(f'{iid} requires exactly one valid claim_class')
        refs=sl(x.get('source_ids'),f'{iid}.source_ids',e,True)
        if set(refs)-source_ids:e.append(f'{iid} has unknown source ids')
        sl(x.get('preserved_structure'),f'{iid}.preserved_structure',e,True)
        sl(x.get('not_inherited'),f'{iid}.not_inherited',e,True)
        if not ne(x.get('prohibited_inference')):e.append(f'{iid}.prohibited_inference required')
    if inherit_ids!={f'INH-{i:02d}' for i in range(1,8)}:e.append('inheritance registry must contain INH-01 through INH-07 exactly')
    human=P['human'].read_text(encoding='utf-8')
    for phrase in ('HISTORICAL_SOURCE != CURRENT_ENDORSEMENT','METHOD_INHERITANCE != ONTOLOGY_INHERITANCE','29 historical symbol','11 explicit definition conflicts','15 classified historical results','7 methodological inheritance contracts'):
        if phrase not in human:e.append(f'human lineage summary missing: {phrase}')
    ok=not e
    return {'status':'ok' if ok else 'error','errors':e,'source_count':len(source_ids),'historical_source_count':len(hist_ids),'symbol_count':len(seen),'conflict_count':len(conflict_ids),'result_count':len(result_ids),'inheritance_count':len(inherit_ids),'platforms':sorted(REQ_PLAT),'exit_criterion_met':ok and not missing and len(inherit_ids)==7}
def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--json',action='store_true');a=ap.parse_args();r=validate()
    if a.json: print(json.dumps(r,indent=2,sort_keys=True))
    else: print('historical lineage: '+r['status'])
    return 0 if r['status']=='ok' else 1
if __name__=='__main__':raise SystemExit(main())
