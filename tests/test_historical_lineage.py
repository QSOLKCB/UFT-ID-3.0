from __future__ import annotations
import importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VPATH=ROOT/'scripts/validate_historical_lineage.py'; RPATH=ROOT/'experiments/run_lineage.py'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V=mod('historical_lineage_validator',VPATH); RECEIPT=mod('historical_lineage_receipt',RPATH)
class HistoricalLineageTests(unittest.TestCase):
 def test_registry_validates_and_exit_criterion(self):
  r=V.validate();self.assertEqual(r['status'],'ok',r['errors']);self.assertTrue(r['exit_criterion_met']);self.assertEqual(r['platforms'],['academia','archived-copy','authorea','github','google-drive','zenodo'])
 def test_expected_surface_counts(self):
  r=V.validate();self.assertEqual((r['source_count'],r['historical_source_count'],r['symbol_count'],r['conflict_count'],r['result_count'],r['inheritance_count']),(15,9,29,11,15,7))
 def test_rho_collision_is_explicit(self):
  d=json.loads((ROOT/'machine/historical_symbols.json').read_text());x=next(x for x in d['symbols'] if x['historical_symbol']=='rho (density operator)');self.assertEqual(x['disposition'],'symbol-conflict');self.assertEqual(x['canonical_target'],'s in S');self.assertIn('density-operator requirement',' '.join(x['not_inherited']))
 def test_lexicographic_weighted_sum_conflict_is_preserved(self):
  d=json.loads((ROOT/'machine/historical_conflicts.json').read_text());x=next(x for x in d['conflicts'] if x['conflict_id']=='HDC-005');self.assertEqual(x['resolution'],'do-not-reconcile-silently');self.assertIn('weighted',x['historical_definition'].lower())
 def test_dark_state_inheritance_is_quarantined(self):
  d=json.loads((ROOT/'machine/methodological_inheritance.json').read_text());x=next(x for x in d['imports'] if x['inheritance_id']=='INH-04');self.assertEqual(x['claim_class'],'DIAGNOSTIC');self.assertIn('dark matter/dark energy identification',x['not_inherited']);self.assertIn('psi or anomalous cognition mechanism',x['not_inherited'])
 def test_no_private_connector_ids_in_source_registry(self):
  t=(ROOT/'machine/historical_sources.json').read_text();
  for bad in ('gmail:','gdrive:','docs.google.com','drive.google.com'):self.assertNotIn(bad,t)
 def test_drive_hash_scope_is_export_only(self):
  d=json.loads((ROOT/'machine/historical_sources.json').read_text());x=next(x for x in d['sources'] if x['source_id']=='UFT-HIST-008');m=next(m for m in x['manifestations'] if m['platform']=='google-drive');self.assertFalse(m['native_hash_available']);self.assertIn('export bytes',m['hash']['scope'])
 def test_every_inheritance_has_noninheritance_and_claim_class(self):
  d=json.loads((ROOT/'machine/methodological_inheritance.json').read_text());
  for x in d['imports']:
   self.assertTrue(x['source_ids']);self.assertTrue(x['claim_class']);self.assertTrue(x['preserved_structure']);self.assertTrue(x['not_inherited']);self.assertTrue(x['prohibited_inference'])
 def test_receipt_deterministic(self):
  a=RECEIPT.run_suite();b=RECEIPT.run_suite();self.assertEqual(a['suite_fingerprint_sha256'],b['suite_fingerprint_sha256']);self.assertEqual(len(a['suite_fingerprint_sha256']),64)
class MutationPolicyTests(unittest.TestCase):
 def test_contract_hard_rules_are_fail_closed(self):
  d=json.loads((ROOT/'machine/historical_lineage_contract.json').read_text());self.assertTrue(all(v is False for v in d['hard_rules'].values()))
 def test_no_empirical_result_without_evidence_in_canonical_registry(self):
  d=json.loads((ROOT/'machine/historical_results.json').read_text());
  for x in d['results']:
   if x['result_class']=='empirical':self.assertTrue(x.get('evidence_paths'))
if __name__=='__main__':unittest.main()
