"""Independent FCD service reconciliation for stopped and moving V15 branches.

Preserves historical stopped-only helper output rather than overwriting it.
No raw writes; no simulation or runtime sensor calls.
"""
import argparse, csv, json, sys
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode = True
import analyze_run as D

def audit(raw, card):
    rows=D.read_csv(raw/'controller_steps.csv')
    metadata={r['vehicle_id']:r for r in D.read_csv(raw/'vehicle_metadata.csv')}
    via=card['meter_controlled_link']['via']
    stopline=card['meter_controlled_link']['storage_length_m']
    prior={}; seen=set(); counts=Counter(); mismatches=[]
    for elem in D.A.records(raw/'fcd.xml.gz','timestep'):
        t=int(float(elem.get('time'))); row=rows[t]
        now={v.get('id'):dict(v.attrib) for v in elem}
        if t>=600:
            before={i for i,v in prior.items() if v['lane']==via}
            cross={i for i,v in now.items() if v['lane']==via}-before
            if before!=set(json.loads(row['internal_before_ids_json'])):mismatches.append([t,'internal_before'])
            if cross!=set(json.loads(row['crossing_bracket_ids_json'])):mismatches.append([t,'crossing_bracket'])
            if cross & seen:mismatches.append([t,'duplicate_crossing'])
            seen|=cross
            states=json.loads(row['guard_vehicle_states_json'])
            storage={i for i,v in prior.items() if v['lane']=='ramp_storage_0'}
            if {v['vehicle_id'] for v in states}!=storage:mismatches.append([t,'guard_population'])
            for v in states:
                old=prior.get(v['vehicle_id'])
                if old is None or abs(float(old['pos'])-v['position_m'])>.005001 or abs(float(old['speed'])-v['speed_m_s'])>.005001:mismatches.append([t,'guard_sensor_state'])
                for field,mfield in [('length_m','vehicle_length_m'),('accel_m_s2','accel_m_s2'),('decel_m_s2','normal_decel_m_s2')]:
                    if field in v and mfield in metadata[v['vehicle_id']] and abs(float(v[field])-float(metadata[v['vehicle_id']][mfield]))>1e-8:mismatches.append([t,'guard_metadata_'+field])
            allowed,reason=D.independent_guard(row,metadata,stopline)
            slot=D.truth(row['slot_scheduled']); qualified=D.truth(row['queued_unblocked_slot'])
            if qualified:
                counts['qualified']+=1
                front=row['front_queued_vehicle_id']
                if not slot or not allowed or not storage or max(storage,key=lambda i:float(prior[i]['pos']))!=front:mismatches.append([t,'qualification_identity_or_branch'])
                counts['qualified_front_crossings']+=front in cross
                counts['wrong_front']+=bool(cross and cross!={front})
                counts['qualified_'+reason]+=1
            counts['multiple_slots']+=slot and len(cross)>1
            counts['red_crossings']+=len(cross) if not slot else 0
        prior=now
    return {'status':'PASS_V15_FCD_SERVICE' if not mismatches and not counts['wrong_front'] and not counts['multiple_slots'] and not counts['red_crossings'] and counts['qualified']>=20 and counts['qualified_front_crossings']/counts['qualified']>=.9 else 'FAIL_OR_INSUFFICIENT','counts':dict(counts),'mismatches':mismatches,'qualification':'Independent stopped and moving V15 guards, not historical stopped-only 1.1m geometry. FCD is rounded; native pre-step sensors are independently replayed and compared with previous label. SecureGap remains conditional on logged SUMO value.','supersedes_only':'Historical sampled_service.json stopped-only geometry interpretation; original result retained.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--card',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    card=json.loads(Path(a.card).read_text());raw=Path(card['output_dir']) if 'output_dir' in card else None
    if raw is None:
        raw=D.ROOT/'data/raw/formal_development_20261007_v1'/card['run_id']/'outputs'
    x=audit(raw,card); D.write(Path(a.out),x);print(json.dumps(x))
if __name__=='__main__':main()
