"""Independent selected-evidence review; default needs no ignored raw or native API."""
import argparse, hashlib, json, math
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]

def review(local_raw=False):
    source=json.loads((BASE/'YELLOW_SELECTED_RAW_EXTRACT.json').read_text())
    rows=source['rows'];assert [r['time_begin_s'] for r in rows]==list(range(1200,1207))
    assert [r['predicted_motion_state'] for r in rows]==['G','G','G','y','y','y','r']
    assert rows[-1]['time_end_s'] is None and rows[-1]['crossing_ids'] is None
    assert all(r['crossing_ids']==[] for r in rows[3:6])
    summaries=[]
    for row in rows:
        vs=row['vehicles'];assert len({v['id'] for v in vs})==len(vs)
        for v in vs:
            assert all(math.isfinite(v[k]) for k in ['position_m','speed_m_s','normal_decel_m_s2','tau_s','action_step_s'])
            assert v['normal_decel_m_s2']==4.5 and v['tau_s']==v['action_step_s']==1
        moving=[v for v in vs if v['speed_m_s']>0]
        summaries.append({'time_s':row['time_begin_s'],'pre_state':row['state_before'],'next_motion':row['predicted_motion_state'],'executed':row['time_end_s'] is not None,'storage_count':sum(v['population']=='storage' for v in vs),'ingress_count':sum(v['population']=='ingress' for v in vs),'moving':[{'id':v['id'],'v_m_s':v['speed_m_s'],'gap_m':204.49-v['position_m'],'estimated_reaction_braking_s':1+v['speed_m_s']/4.5,'estimated_reaction_braking_distance_m':v['speed_m_s']+v['speed_m_s']**2/9} for v in moving]})
    start=summaries[3];assert start['storage_count']==27 and start['ingress_count']==15
    assert {v['id'] for v in start['moving']}=={'R_flow.1','R_flow.2'}
    lanes={v['id']:v for v in source['lanes']}
    limits=[{'lane':k,'nominal_limit_m_s':float(lanes[k]['speed']),'estimated_reaction_braking_s':1+float(lanes[k]['speed'])/4.5} for k in ['ramp_storage_0',':urban_diverge_1_0']]
    if local_raw:
        assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in source['source_files'].items())
    return {'status':'PASS','source_rows_complete_prefix':source['source_rows'],'selected_timestamps':summaries,'nominal_limit_context':limits,'assumptions':'continuous constant ordinary decel4.5 and illustrative reaction1s; tau/action1 are saved but do not establish native literal1s reaction delay; no slope, offsets, perception, followers, LC or receiver proof','classification':'BASIC_PLANNING_ESTIMATE_NOT_NATIVE_SAFETY_OR_YELLOW_CLEARANCE_PROOF','yellow_duration_s':3,'yellow_executed_intervals':[[1203,1204],[1204,1205],[1205,1206]],'yellow_crossings_observed':0,'refused_red_motion_executed':0,'local_raw_hashes_verified':len(source['source_files']) if local_raw else 0,'default_public_scope':'submitted selected extract; raw extraction reconstruction requires local immutable phase/snapshot/network/routes; no raw dependency by default'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify-local-raw-hashes',action='store_true');args=parser.parse_args();print(json.dumps(review(args.verify_local_raw_hashes),indent=2))
