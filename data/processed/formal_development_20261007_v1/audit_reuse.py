"""Independent bounded reuse audit. Raw files are opened read-only."""
from pathlib import Path
import csv, hashlib, json, math, xml.etree.ElementTree as ET
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''): h.update(block)
    return h.hexdigest()

def canonical(e, ignore=()):
    return [e.tag,sorted((k,v) for k,v in e.attrib.items() if k not in ignore),[canonical(c,ignore) for c in e]]

def inspect(run_id, treatment):
    family='stage6_boundary_search_20261002_v1' if treatment=='T0' else 'stage6_standard_metering_execution_20261003_v1'
    package=ROOT/'artifacts'/family/'inputs'/run_id
    card_path=package/'card.json';card=json.loads(card_path.read_text())
    raw=Path(card['output']);rec_path=raw/'execution_receipt.json';receipt=json.loads(rec_path.read_text())
    checks={};checks['receipt_card_sha']=sha(card_path)==receipt['card_sha256']
    checks['completed']=receipt['status']=='COMPLETED' and receipt['return_code']==0
    manifest=receipt.get('output_manifest',receipt.get('files'));bad=[]
    for name,m in manifest.items():
        p=raw/name
        if p.stat().st_size!=m['bytes'] or sha(p)!=m['sha256']:bad.append(name)
    checks['manifest_all_bound']=not bad
    checks['input_hashes']=all(sha(package/name)==h for name,h in card['input_sha256'].items())
    config=ET.parse(package/'scenario.sumocfg').getroot()
    network=Path(config.find('./input/net-file').get('value'))
    checks['network_hash']=sha(network)==card['network_sha256']
    checks['sumo_hash']=sha('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo')==card['sumo_sha256']
    checks['time_seed']=all(config.find(tag).get('value')==str(value) for tag,value in [('./time/begin',0),('./time/end',4200),('./time/step-length',1),('./random_number/seed',card['seed'])])
    demand=ET.parse(package/'demand.rou.xml').getroot();planned={};attributes={}
    for v in demand.findall('vehicle'):
        vid=v.get('id');assert vid not in planned
        planned[vid]=float(v.get('depart'));attributes[vid]=dict(v.attrib)
    counts=Counter(i[0] for i in planned)
    checks['requested_counts']=dict(counts)==card['counts']
    checks['materialized_no_flow']=not demand.findall('flow')
    checks['depart_semantics']=all(v['departLane']=='best' and v['departSpeed']=='max' and v['departPos']==('100' if i[0]=='M' else 'last') for i,v in attributes.items())
    checks['explicit_speed_factors']=all(.2<=float(v['speedFactor'])<=2 for v in attributes.values())
    checks['schedule']=all((600 if i[0]=='R' else 0)<=p<3000 for i,p in planned.items())
    trips={};warnings=[]
    for e in ET.parse(raw/'tripinfo.xml').getroot().findall('tripinfo'):
        vid=e.get('id');assert vid not in trips;trips[vid]=dict(e.attrib)
    checks['trip_identity']=set(trips)==set(planned)
    classes=[]
    for group in 'MRUX':
        ids=[i for i in planned if i[0]==group];tot=src=inside=0.;inserted=arrived=0
        for vid in ids:
            row=trips.get(vid);p=planned[vid]
            d=float(row['depart']) if row and float(row['depart'])>=0 else math.inf
            a=float(row['arrival']) if row and float(row['arrival'])>=0 else math.inf
            inserted+=d<4200;arrived+=a<4200
            s=min(a,4200)-p;w=min(d,4200)-p;n=min(a,4200)-min(d,4200)
            assert abs(s-w-n)<1e-8
            if a<4200:
                assert abs(s-float(row['duration'])-float(row['departDelay']))<=.010001
            if row and row.get('vaporized','') not in ('','false','0'):warnings.append([vid,'vaporized'])
            tot+=s;src+=w;inside+=n
        classes.append(dict(run_id=run_id,treatment=treatment,seed=card['seed'],q_ramp=750 if len([i for i in planned if i[0]=='R'])==500 else 900,vehicle_class=group,planned=len(ids),inserted=inserted,arrived=arrived,unfinished=inserted-arrived,undeparted=len(ids)-inserted,system_time_T_s=tot,source_wait_T_s=src,in_network_T_s=inside,mean_system_time_T_s=tot/len(ids)))
    summary=ET.parse(raw/'sumo_summary.xml').getroot().findall('step')
    checks['summary_labels']=len(summary)==4200 and all(float(e.get('time'))==j for j,e in enumerate(summary))
    last=summary[-1];checks['summary_lifecycle']=int(last.get('inserted'))==sum(c['inserted'] for c in classes) and int(last.get('arrived'))==sum(c['arrived'] for c in classes) and int(last.get('running'))==sum(c['unfinished'] for c in classes) and int(last.get('waiting'))==sum(c['undeparted'] for c in classes)
    checks['no_lifecycle_anomaly']=not warnings and all(int(e.get(k,'0'))==0 for e in summary for k in ['collisions','teleports','discarded'])
    error=(raw/'sumo_error.log').read_text();checks['no_sumo_warning']=not error.strip()
    additional=ET.parse(package/'scenario.add.xml').getroot()
    measurement=[canonical(e,('file','dest')) for e in additional if e.tag in ('laneAreaDetector','inductionLoop','timedEvent')]
    urban=[canonical(e) for e in additional if e.tag=='tlLogic' and e.get('id')=='urban_tls']
    checks['measurement_count']=len([e for e in additional if e.tag in ('laneAreaDetector','inductionLoop')])==11
    if treatment=='T1':
        checks['base_receipt_sha']=sha(Path(card['base_output'])/'execution_receipt.json')==card['base_receipt_sha256']
        checks['base_demand_sha']=sha(package/'demand.rou.xml')==card['base_input_sha256']['demand.rou.xml']
        checks['reference_parameters']=card['feedback']==dict(gain_veh_h_per_pct=70.,initial_veh_h=900.,maximum_veh_h=900.,minimum_veh_h=300.,target_pct=11.) and card['meter_start_s']==600 and card['feedback_update_s']==[630,4170,30]
    return dict(run_id=run_id,treatment=treatment,seed=card['seed'],raw=str(raw),card=str(card_path),card_sha256=sha(card_path),receipt_sha256=sha(rec_path),manifest_files=len(manifest),bad_manifest_files=bad,checks=checks,eligible_existing_data=all(checks.values()),classes=classes,network_sha256=card['network_sha256'],sumo_sha256=card['sumo_sha256'],demand_sha256=sha(package/'demand.rou.xml'),measurement=measurement,urban=urban,config_processing=canonical(config.find('processing')),types_routes=[canonical(e) for e in demand if e.tag!='vehicle'],last_summary=dict(last.attrib),runtime_wall_s=receipt.get('runtime_wall_s',receipt.get('wall_s')),raw_payload_bytes=receipt['output_bytes'])

def main():
    runs=[inspect(f'M3600_R{r}_S{s}','T0') for r in [750,900] for s in [17,23,42]]
    runs += [inspect(f'M3600_R900_S{s}_ALINEA_TRACI_V15','T1') for s in [17,23,42]]
    ref=runs[0]
    for run in runs:
        run['shared_scene_equivalence']={k:run[k]==ref[k] for k in ['network_sha256','sumo_sha256','measurement','urban','config_processing','types_routes']}
        run['eligible_existing_data'] &= all(run['shared_scene_equivalence'].values())
        if run['treatment']=='T1':
            base=next(x for x in runs if x['run_id']==f"M3600_R900_S{run['seed']}")
            run['demand_byte_matched_OPEN']=run['demand_sha256']==base['demand_sha256']
            run['eligible_existing_data'] &= run['demand_byte_matched_OPEN']
    record=dict(classification='DEVELOPMENT_REUSE_AUDIT',script_sha256=sha(__file__),runs=runs,qualification='Existing raw/input eligibility only. Reuse in new wrapper additionally requires unchanged input contract and T1 behavior equivalence.',new_required=[dict(q_main=3600,q_ramp=r,seed=s,treatment=t) for s in [17,23,42] for r in [900,750] for t in ['T1','T2'] if not(t=='T1' and r==900)])
    with (OUT/'reuse_audit.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    rows=[c for run in runs for c in run['classes']]
    with (ROOT/'results/tables/formal_development_20261007_v1/reused_class_costs.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({'runs':len(runs),'eligible':sum(r['eligible_existing_data'] for r in runs),'new_required':record['new_required'],'failed_checks':[(r['run_id'],k) for r in runs for k,v in r['checks'].items() if not v]}))

if __name__=='__main__':main()
