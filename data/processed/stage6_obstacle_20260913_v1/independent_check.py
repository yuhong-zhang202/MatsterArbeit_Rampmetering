"""Independent raw-XML verification. Does not import the production adapter."""
from pathlib import Path
import csv,json,hashlib,math,itertools
from collections import defaultdict
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;TABLE=ROOT/'results/tables/stage6_obstacle_20260913_v1'
def rows(p):
    with Path(p).open(newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b):
    if a in ('',None) or b is None:return a in ('',None) and b is None
    return math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-8)
def index(data,cols):
    d={}
    for r in data:
        k=tuple(r[c] for c in cols)
        if k in d:raise AssertionError('duplicate derived key '+str(k))
        d[k]=r
    return d
def main():
    sources=rows(BASE/'source_registry.csv');invent=rows(BASE/'source_file_inventory.csv')
    for r in invent:assert sha(r['path'])==r['sha256']
    entry=index(rows(TABLE/'entry_vehicle_records.csv'),['run_id','id'])
    endpoints=index(rows(TABLE/'endpoint_accounting.csv'),['run_id','class','endpoint_s'])
    r_events=index(rows(TABLE/'R_passage_events.csv'),['run_id','vehicle_id'])
    ex=index(rows(TABLE/'shared_exposure.csv'),['run_id','window'])
    ms=index(rows(TABLE/'M_region_window.csv'),['run_id','window','region'])
    st=index(rows(TABLE/'M_space_time_30s.csv'),['run_id','bin_begin','region'])
    sw=index(rows(TABLE/'section_window_metrics.csv'),['run_id','group','window','metric_id'])
    pr=index(rows(TABLE/'R_region_propagation.csv'),['run_id','region'])
    contract=json.loads((ROOT/'data/processed/stage3_baseline_diagnostic_20260912_v2/measurement_contract.json').read_text());lanes=contract['lanes'];windows={'A':(0,1500),'B':(300,1500),'Post':(1500,2700),'Full':(0,2700)}
    results=[];comparisons=defaultdict(int)
    with (TABLE/'lane_class_time.csv').open(newline='') as tf:
        groups=itertools.groupby(csv.DictReader(tf),key=lambda r:r['run_id'])
        for src,(rid,group) in zip(sources,groups,strict=True):
            assert rid==src['run_id'];files={r['source_suffix']:Path(r['path']) for r in invent if r['run_id']==rid}
            trips={n.get('id'):dict(n.attrib) for _,n in ET.iterparse(files['outputs/tripinfo.xml'],events=('end',)) if n.tag=='tripinfo'}
            planned={n.get('id').split('_')[0]:int(n.get('number')) for n in ET.parse(files['demand.rou.xml']).getroot().findall('flow')}
            rawcells={};first={};previous={};event={};labels=set();co=[];regions={};mwin=defaultdict(list);mbin=defaultdict(list)
            tls={float(n.get('time')):n.get('state') for _,n in ET.iterparse(files['outputs/tls_states.xml'],events=('end',)) if n.tag=='tlsState'}
            assert set(tls)==set(range(2700))
            for _,n in ET.iterparse(files['outputs/fcd.xml'],events=('end',)):
                if n.tag!='timestep':continue
                t=float(n.get('time'));assert t not in labels;labels.add(t);seen=set();cells=defaultdict(list);R=U=0
                for v in n:
                    vid=v.get('id');lane=v.get('lane');c=vid.split('_')[0];speed=float(v.get('speed'));pos=float(v.get('pos'));assert vid not in seen and vid in trips and lane in lanes and math.isfinite(speed);seen.add(vid)
                    cells[(lane,c)].append((speed,pos));first.setdefault(vid,(t,lane,pos,speed))
                    reg=lanes[lane]['region']
                    if c=='R' and speed<=.1:regions.setdefault(reg,t)
                    if lane=='shared_approach_0' and speed<=.1:R+=c=='R';U+=c=='U'
                    if c=='R' and lane in ['main_down_0','main_down_1'] and vid not in event:event[vid]=(t,lane,previous.get(vid))
                    previous[vid]=(t,lane)
                    if c=='M':
                        signed=pos-lanes[lane]['length_m'] if lane.startswith('main_up') else pos if lane.startswith(':') else pos+8.64
                        mbin[(int(t//30)*30,reg)].append((speed,signed,vid))
                        for w,(b,e) in windows.items():
                            if b<=t<e:mwin[(w,reg)].append((speed,vid))
                for (lane,c),values in cells.items():rawcells[(t,lane,c)]=values
                co.append((t,R,U,tls[t][0]));n.clear()
            assert labels==set(range(2700))
            nrows=0
            for r in group:
                key=(float(r['time_s']),r['lane_id'],r['class']);a=rawcells.get(key,[]);nrows+=1
                assert int(r['present'])==len(a) and int(r['stopped'])==sum(v<=.1 for v,p in a)
                assert close(r['speed_sum_mps'],sum(v for v,p in a)) and int(r['speed_n'])==len(a)
                assert close(r['min_pos_m'],min((p for v,p in a),default=None)) and close(r['max_pos_m'],max((p for v,p in a),default=None))
                assert close(r['mean_speed_mps'],sum(v for v,p in a)/len(a) if a else None)
                assert r['speed_value_state']==('observed' if a else 'no_contributors')
            assert nrows==2700*sum(len(l['observed_classes']) for l in lanes.values());comparisons['lane_class_time_rows']+=nrows
            assert set(first)==set(trips)
            for vid,tr in trips.items():
                r=entry[(rid,vid)];t,lane,pos,v=first[vid]
                for col,raw in [('depart_time','depart'),('depart_pos','departPos'),('depart_delay_s','departDelay'),('arrival_time','arrival'),('in_network_duration_s','duration'),('tripinfo_time_loss_s','timeLoss'),('tripinfo_waiting_time_s','waitingTime')]:assert close(r[col],tr[raw])
                assert r['depart_lane']==tr['departLane'] and r['first_fcd_lane']==lane and close(r['first_fcd_time'],t) and close(r['first_fcd_pos'],pos)
                if vid.startswith('M_'):
                    distance=lanes[tr['departLane']]['length_m']-float(tr['departPos']);assert close(r['distance_to_main_up_end_m'],distance) and close(r['distance_to_main_down_start_m'],distance+8.64)
                comparisons['entry_vehicles']+=1
            for c in ['M','R','U','X']:
                g=[v for k,v in trips.items() if k.startswith(c+'_')]
                for t in [1500,2700]:
                    E=sum(float(v['depart'])<t for v in g);A=sum(float(v['arrival'])<t for v in g);r=endpoints[(rid,c,str(t))]
                    assert [int(r[x]) for x in ['P','E','A','N','O']]==[planned[c],E,A,E-A,planned[c]-E];comparisons['endpoints']+=1
            assert len(event)==len([r for k,r in r_events.items() if k[0]==rid])
            for vid,(t,lane,prev) in event.items():
                r=r_events[(rid,vid)];assert close(r['first_downstream_time_s'],t) and r['first_downstream_lane']==lane
                assert close(r['previous_time_s'],prev[0]) and r['previous_lane']==prev[1] and r['status']=='bracketed';comparisons['R_events']+=1
            for reg in ['ramp_accel','ramp_mid_internal','ramp_storage','ramp_diverge_internal','shared_approach']:
                assert close(pr[(rid,reg)]['first_R_stopped_label'],regions.get(reg));comparisons['propagation_firsts']+=1
            for w,(b,e) in windows.items():
                g=[x for x in co if b<=x[0]<e];both=[x for x in g if x[1]>0 and x[2]>0];r=ex[(rid,w)]
                expect={'R_shared_stopped_labels':sum(x[1]>0 for x in g),'U_shared_stopped_labels':sum(x[2]>0 for x in g),'RU_shared_labels':len(both),'R_shared_vehicle_seconds':sum(x[1] for x in g),'U_shared_vehicle_seconds':sum(x[2] for x in g),'RU_labels_green':sum(x[3] in 'Gg' for x in both),'RU_labels_red':sum(x[3]=='r' for x in both),'RU_labels_yellow':sum(x[3] in 'Yy' for x in both)}
                for k,v in expect.items():assert int(r[k])==v
                comparisons['shared_window_rows']+=1
                for reg in ['mainline_origin_observation','mainline_merge_internal','mainline_downstream']:
                    g=mwin[(w,reg)];r=ms[(rid,w,reg)];assert int(r['M_sample_count'])==len(g) and int(r['unique_M_ids'])==len({v for s,v in g})
                    assert close(r['mean_sample_speed_mps'],sum(s for s,v in g)/len(g) if g else None);assert int(r['M_stopped_vehicle_seconds'])==sum(s<=.1 for s,v in g);comparisons['M_region_window_rows']+=1
            for b in range(0,2700,30):
                for reg in ['mainline_origin_observation','mainline_merge_internal','mainline_downstream']:
                    g=mbin[(b,reg)];r=st[(rid,str(b),reg)]
                    assert int(r['M_samples'])==len(g) and close(r['mean_sample_speed_mps'],sum(s for s,p,v in g)/len(g) if g else None)
                    assert int(r['M_stopped_vehicle_seconds'])==sum(s<=.1 for s,p,v in g);assert close(r['min_signed_M_position_m'],min((p for s,p,v in g),default=None));assert close(r['max_signed_M_position_m'],max((p for s,p,v in g),default=None));comparisons['M_space_time_bins']+=1
            e1=defaultdict(list)
            for d in contract['e1_detectors']:
                a=[dict(n.attrib) for _,n in ET.iterparse(files[d['output_suffix']],events=('end',)) if n.tag=='interval'];assert len(a)==90;e1[d['group']]+=a
            for group,a in e1.items():
                for w,(b,e) in windows.items():
                    g=[r for r in a if b<=float(r['begin']) and float(r['end'])<=e];n=sum(int(r['nVehContrib']) for r in g);ne=sum(int(r['nVehEntered']) for r in g)
                    expect={'q_contrib_vehph':3600*n/(e-b),'q_entered_vehph':3600*ne/(e-b),'speed_contribution_weighted_mps':sum(int(r['nVehContrib'])*float(r['speed']) for r in g if int(r['nVehContrib']))/n if n else None,'occupancy_lane_mean_percent':sum(float(r['occupancy'])*(float(r['end'])-float(r['begin'])) for r in g)/(2*(e-b))}
                    for metric,value in expect.items():assert close(sw[(rid,group,w,metric)]['value'],value);comparisons['section_window_values']+=1
            results.append({'run_id':rid,'status':'passed','raw_FCD_frames':len(labels),'raw_FCD_vehicle_samples':sum(len(v) for v in rawcells.values()),'unique_vehicles':len(trips)})
            print('independent',rid,'passed',flush=True)
    receipt={'status':'passed','method':'independent stdlib raw XML implementation; no production adapter import','source_file_hashes':len(invent),'runs':results,'comparison_counts':dict(comparisons),'code_sha256':sha(Path(__file__)),'production_sha256':sha(BASE/'analyze_archives.py'),'analysis_contract_sha256':sha(BASE/'offline_adapter_contract.json'),'numerical_tolerance':{'abs':1e-8,'rel':1e-10},'simulation_counts':{'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},'limitations':['Independent numeric reconstruction does not validate scientific causality or future scenario suitability','No new EJMI classification or formal threshold selected']}
    with (BASE/'independent_verification.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
if __name__=='__main__':main()
