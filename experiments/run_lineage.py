#!/usr/bin/env python3
"""Deterministic receipt for the UFT-ID historical-lineage authority surface."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, platform, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/'scripts/validate_historical_lineage.py'
FILES=[
'machine/historical_lineage_contract.json','machine/historical_sources.json','machine/historical_symbols.json',
'machine/historical_conflicts.json','machine/historical_results.json','machine/methodological_inheritance.json',
'research/HISTORICAL_LINEAGE.md','scripts/validate_historical_lineage.py','tests/test_historical_lineage.py','experiments/run_lineage.py']
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def canon(x:object)->bytes:return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def validator():
 s=importlib.util.spec_from_file_location('hist_lineage_validator',VALIDATOR);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run_suite():
 v=validator().validate()
 if v['status']!='ok':raise RuntimeError('; '.join(v['errors']))
 hashes={f:sha((ROOT/f).read_bytes()) for f in sorted(FILES)}
 ident={'type':'uft-id-historical-lineage-receipt','schema_version':'1.0.0','source_sha256':hashes,'summary':{k:v[k] for k in ('source_count','historical_source_count','symbol_count','conflict_count','result_count','inheritance_count','platforms','exit_criterion_met')}}
 fp=sha(canon(ident))
 return {**ident,'suite_fingerprint_sha256':fp,'runtime':{'python':platform.python_version(),'implementation':platform.python_implementation(),'platform':sys.platform},'runtime_excluded_from_fingerprint':True,'claim_boundary':'SOURCE_IDENTITY != TRUTH; METHOD_INHERITANCE != ONTOLOGY_INHERITANCE'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--json',action='store_true');p.add_argument('--hash-only',action='store_true');a=p.parse_args();r=run_suite()
 if a.hash_only:print(json.dumps({'suite_fingerprint_sha256':r['suite_fingerprint_sha256']},sort_keys=True))
 elif a.json:print(json.dumps(r,indent=2,sort_keys=True))
 else:print('historical lineage receipt: '+r['suite_fingerprint_sha256'])
 return 0
if __name__=='__main__':raise SystemExit(main())
