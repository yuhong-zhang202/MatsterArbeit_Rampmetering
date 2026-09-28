import json,hashlib,copy
from decimal import Decimal
from pathlib import Path
from repair_optional_filters import repair
B=Path(__file__).resolve().parent;E=B.parent;O=E/'runtime_validation_revision03';V1=E/'runtime_validation_revision01'
def bind(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
m=json.loads((O/'runtime_input_manifest.json').read_text());attempts=[]
for a in m['attempts']:
 n=copy.deepcopy(a);oldid=a['attempt_id'];newid=oldid.replace('RV3_','RV4_',1);d=B/'inputs'/newid;d.mkdir(parents=True,exist_ok=False)
 for row in a['inputs']:
  src=Path(row['path']);s=src.read_text().replace(str(O),str(B)).replace('RV3_','RV4_')
  if src.name=='scenario.add.xml':
   s,count=repair(s);assert count==22
  (d/src.name).write_text(s)
 n.update(attempt_id=newid,logical_run_id=a['logical_run_id'].replace('RV3_','RV4_',1),run_root=str(B/'runs'/newid),output_root=str(B/'runs'/newid/'outputs'))
 n['argv'][2]=str(d/'scenario.sumocfg');n['inputs']=[bind(d/Path(row['path']).name) for row in a['inputs']];n['source_template_bindings']=a['inputs'];n['requires_previous_attempts']=[x['attempt_id'] for x in attempts];attempts.append(n)
put(B/'runtime_input_manifest.json',dict(m,attempts=attempts,status='EMPTY_OPTIONAL_FILTER_REPAIR_PENDING_REVIEW',input_delta=['omit exactly22empty optional detector filter attributes per additional','new independent run/output identities'],original_demand_bytes_unchanged=True,original_demand_semantics_unchanged=True))
roots=[V1/'runs/RV_SMOKE_R720_S17_attempt1',O/'runs/RV3_SMOKE_R720_S17_attempt1'];receipts=[json.loads((x/'execution_receipt.json').read_text(),parse_float=Decimal) for x in roots];total=sum(x['wallclock_s'] for x in receipts);files=[bind(p) for r in roots for p in sorted(r.rglob('*')) if p.is_file()];bs=sum(x['bytes'] for x in files);assert total==Decimal('22.032722626005124') and bs==52751
put(B/'prior_attempt_ledger.json',{'scope':'runtime recovery only; not project lifetime','actual_prior_SUMO_starts':2,'actual_prior_netconvert_starts_in_P2':2,'prior_SUMO_wallclock_s':float(total),'prior_SUMO_wallclock_decimal_s':str(total),'prior_SUMO_directory_bytes':bs,'files':files,'prior_receipts':[bind(x/'execution_receipt.json') for x in roots],'old_cards':[bind(E/f'runtime_validation_revision{rev}/RUNTIME_VALIDATION_CARD.json') for rev in ['02','03']],'old_manifests':[bind(E/f'runtime_validation_revision{rev}/runtime_delivery_manifest.json') for rev in ['02','03']],'new_user_instruction':'smoke排查原因然后继续尝试','new_bounded_starts':3,'maximum_cumulative_runtime_SUMO_starts':5,'start_ceiling_change':'5 total is exactly one above revision03 ceiling4; bounded evidence-based technical retry under continuing authorization; no automatic repeat','cumulative_time_stop_s':549.3738820840008,'cumulative_byte_stop':4500023552,'remaining_time_decimal_s':str(Decimal('549.3738820840008')-total),'remaining_bytes':4500023552-bs})
s=(O/'runtime_executor.py').read_text().replace('runtime_validation_revision03','runtime_validation_revision04').replace('RV3_','RV4_').replace("history['actual_prior_SUMO_starts']==1 and history['maximum_cumulative_runtime_SUMO_starts']==4","history['actual_prior_SUMO_starts']==2 and history['maximum_cumulative_runtime_SUMO_starts']==5")
(B/'runtime_executor.py').write_text(s)
s=(O/'test_runtime_executor.py').read_text();anchor=' def test_fixed_scope(self):';extra=""" def test_prior_time_budget_not_reset(self):
  self.a['argv']=[sys.executable,'-c','import time;time.sleep(5)']
  self.assertEqual(self.run_fake(prior_time=e.LIMITS['total_monitored_s']-.01)['status'],'terminal_timeout')
 def test_prior_byte_budget_not_reset(self):
  self.assertEqual(self.run_fake(prior_bytes=e.LIMITS['total_observed_bytes']-10)['status'],'terminal_output_stop_line')
""";s=s.replace(anchor,extra+anchor);(B/'test_runtime_executor.py').write_text(s)
s=(O/'RUNTIME_CONTRACT.md').read_text().replace('Revision03 repairs schema-root hints only and uses new RV3 attempt identities and directories. Revision01/02 and the failed first smoke remain immutable.','Revision04 removes only explicitly empty optional vTypes/nextEdges detector attributes, preserving prior schema hints. It uses new RV4 attempt identities and directories. All previous packages and both failed smokes remain immutable.').replace('RV3_','RV4_')
a=s.index('New three-attempt allowance:');z=s.index('Polling sleeps',a)
s=s[:a]+'At most three new starts are proposed: exactly one repaired smoke then the two gated seed17 validations. Including two already-consumed smokes, cumulative ceiling is FIVE starts, explicitly one above revision03 ceiling FOUR under the continuing bounded troubleshooting authorization. This does not approve automatic retries. The original cumulative time/byte stop lines remain 549.3738820840008 s and 4,500,023,552 bytes, with no reset. Actual prior consumption is exactly22.032722626005124 s and52,751 bytes; remaining effective envelope is527.341159457995676 s and4,499,970,801 bytes. Each run additionally retains the180s/1.5GB stop lines; the last run receives only the smaller remaining cumulative allowance. '+s[z:]
s+='\n\nRevision04 detector repair: omit only explicitly empty optional vTypes and nextEdges attributes on the11E1/E2 detectors. Non-empty filters are preserved, and no detector position, lane, period, threshold, route, traffic input, time or compiled network changes. Installed1.26 XSD marks both attributes optional; upstream1.26 parser supplies empty defaults when omitted, and official detector documentation defines empty defaults as all types/no future-edge restriction. Empty XML attributes previously failed the runtime parser despite passing XSD. The new static checks distinguish these paths; actual loading remains unverified until smoke.\n'
(B/'RUNTIME_CONTRACT.md').write_text(s)
print('materialized inputs and preserved budgets',str(total),bs)
