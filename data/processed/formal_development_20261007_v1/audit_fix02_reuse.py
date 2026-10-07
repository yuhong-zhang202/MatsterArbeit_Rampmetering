"""Independent actual-green witness audit; never a counterfactual effect estimate."""
import argparse,csv,gzip,hashlib,importlib.util,json,math,sys
from pathlib import Path
import xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'data/processed/formal_development_20261007_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open()))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--helper-sha',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 helper=ROOT/'scripts/formal_development_20261007_v1/safe_actuator_fix02.py'
 assert sha(helper)==a.helper_sha
 spec=importlib.util.spec_from_file_location('candidate_fix02',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
 runs=[r for r in json.load((BASE/'reuse_audit.json').open())['runs'] if r['treatment']=='T1']
 rid='DEV_M3600_R900_S17_T2_A02';runs.append(dict(run_id=rid,raw=str(ROOT/'data/raw/formal_development_20261007_v1'/rid/'outputs'),card=str(ROOT/'artifacts/formal_development_20261007_v1/inputs'/rid/'card.json')))
 results=[]
 for run in runs:
  raw=Path(run['raw']);card=json.load(open(run['card']));length=card['meter_controlled_link']['storage_length_m'];data=rows(raw/'controller_steps.csv');metadata={r['vehicle_id']:r for r in rows(raw/'vehicle_metadata.csv')}
  receipt=json.load((raw/'execution_receipt.json').open());sources={}
  for name in ['controller_steps.csv','vehicle_metadata.csv','fcd.xml.gz']:
   sources[name]=sha(raw/name);assert sources[name]==receipt['output_manifest'][name]['sha256']
  assert len(data)==4200 and [int(r['time_begin_s']) for r in data]==list(range(4200))
  witnesses=[];greens=0;identities=0
  for row in data:
   if row['slot_scheduled'].lower()!='true':continue
   greens+=1;assert row['observed_state']=='G' and row['guard_allowed'].lower()=='true'
   states=json.loads(row['guard_vehicle_states_json']);assert len(states)==len({v['vehicle_id'] for v in states})==int(row['queue_vehicle_count'])
   front=row['front_queued_vehicle_id'];assert max(states,key=lambda s:s['position_m'])['vehicle_id']==front
   bad=[]
   for v in states:
    if v['vehicle_id']==front:continue
    m=metadata[v['vehicle_id']];speed=v['speed_m_s']+v['accel_m_s2'];need=1.1+2*speed+speed**2/(2*v['decel_m_s2']);gap=length-v['position_m']
    state=h.VehicleState(v['position_m'],v['speed_m_s'],float(m['vehicle_length_m']),float(m['min_gap_m']),v['accel_m_s2'],v['decel_m_s2'])
    assert math.isclose(need,h.required_pre_green_distance_m(state),abs_tol=1e-10);identities+=1
    if gap+1e-9<need:bad.append(dict(vehicle_id=v['vehicle_id'],native_state=v,gap_m=gap,new_required_m=need,new_margin_m=gap-need))
   if bad:witnesses.append(dict(time_begin_s=int(row['time_begin_s']),front_id=front,actual_crossings=json.loads(row['crossing_bracket_ids_json']),rejected_followers=bad))
  assert witnesses
  first=witnesses[0];target=first['time_begin_s']-1;observed={}
  with gzip.open(raw/'fcd.xml.gz','rb') as f:
   for _,elem in ET.iterparse(f,events=('end',)):
    if elem.tag!='timestep':continue
    if int(float(elem.get('time')))==target:
     observed={v.get('id'):dict(v.attrib) for v in elem};break
    elem.clear()
  for v in first['rejected_followers']:
   f=observed[v['vehicle_id']];n=v['native_state'];assert f['lane']=='ramp_storage_0' and abs(float(f['pos'])-n['position_m'])<=.005001 and abs(float(f['speed'])-n['speed_m_s'])<=.005001
   v['fcd_pre_label']=target;v['fcd_rounded_state']=f
  results.append(dict(run_id=run['run_id'],status='NOT_REUSABLE_UNDER_FIX02',raw=str(raw),card_sha256=sha(Path(run['card'])),source_sha256=sources,controller_rows=len(data),actual_greens=greens,actual_greens_rejected_by_new_storage_bound=len(witnesses),independent_formula_helper_matches=identities,first_witness=first,witnesses=witnesses))
 out=Path(a.out);out.mkdir(exist_ok=False)
 report=dict(classification='DEVELOPMENT_IMPLEMENTATION_EQUIVALENCE_AUDIT',helper_sha256=a.helper_sha,script_sha256=sha(Path(__file__)),runs=results,interpretation='A native high-precision storage-follower witness is sufficient to refute identical control/traffic decisions. Counts replay old observations only; they are not corrected-run predictions. No entrant reconstruction is required to refute equality. Old rounded entrant FCD would prevent an unqualified equivalence PASS if no native witness existed.',coverage='Six OPEN slots remain eligible subject to existing gates. Four old controlled slots need same-combination corrected replacements; old results remain historical. No altered raw or simulation.')
 (out/'REUSE_FIX02_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps([{k:r[k] for k in ['run_id','status','actual_greens','actual_greens_rejected_by_new_storage_bound']} for r in results]))
if __name__=='__main__':main()
