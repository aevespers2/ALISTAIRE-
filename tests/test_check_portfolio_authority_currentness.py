from __future__ import annotations
import copy, importlib.util, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('currentness',ROOT/'scripts'/'check_portfolio_authority_currentness.py'); assert SPEC and SPEC.loader
v=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(v)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.p=v.load_profile(ROOT/'docs'/'portfolio-authority-currentness-v1.json')
 def mutate(self,fn,pattern):
  p=copy.deepcopy(self.p); fn(p)
  with self.assertRaisesRegex(v.ValidationError,pattern): v.validate_profile(p)
 def test_packet(self):
  r=v.validate_repository(ROOT); self.assertEqual(r['result'],'PASS'); self.assertEqual(r['repository_count'],19); self.assertEqual(r['corrected_source_count'],3)
 def test_duplicate_repo(self): self.mutate(lambda p:p['repositories'].append(copy.deepcopy(p['repositories'][0])),'exactly 19')
 def test_authority(self): self.mutate(lambda p:p.__setitem__('authority_effect','OWNER_APPOINTED'),'authority effect')
 def test_snapshot(self): self.mutate(lambda p:p.__setitem__('snapshot_parent','0'*40),'snapshot parent')
 def test_seeker_head(self): self.mutate(lambda p:next(x for x in p['repositories'] if x['repository']=='aevespers2/QSO-SEEKER')['source'].__setitem__('sha','1'*40),'QSO-SEEKER corrected head')
 def test_seeker_body(self): self.mutate(lambda p:next(x for x in p['repositories'] if x['repository']=='aevespers2/QSO-SEEKER').__setitem__('body_declared_sha','1'*40),'body/metadata')
 def test_seeker_history(self): self.mutate(lambda p:next(x for x in p['repositories'] if x['repository']=='aevespers2/QSO-SEEKER').__setitem__('correction_history',[]),'correction history')
 def test_justice(self): self.mutate(lambda p:next(x for x in p['repositories'] if x['repository']=='aevespers2/JusticeForMe').__setitem__('currentness','current_candidate'),'evidence qualification')
 def test_vacancy(self): self.mutate(lambda p:p['vacancies'].pop(),'V1-V10')
 def test_safety(self): self.mutate(lambda p:p['safety_boundaries'].__setitem__('pages_publication',True),'operational authority')
 def test_duplicate_json_key(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/'p.json'; q.write_text('{"profile_id":"a","profile_id":"b"}',encoding='utf-8')
   with self.assertRaisesRegex(v.ValidationError,'duplicate JSON key'): v.load_profile(q)
 def test_nan(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/'p.json'; q.write_text('{"value":NaN}',encoding='utf-8')
   with self.assertRaisesRegex(v.ValidationError,'non-standard numeric'): v.load_profile(q)
if __name__=='__main__': unittest.main()
