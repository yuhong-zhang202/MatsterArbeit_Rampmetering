"""Source-bound Stage6 scientific table assembly, preserving fixed denominators."""
from pathlib import Path
import csv
import json
import statistics
import xml.etree.ElementTree as ET
from src.scenarios import stage6_h2_offline as o
from src.scenarios import stage6_h2_execution as x
from src.analysis import stage6_h2_measurement as m


def validate_auxiliary_context(executed_receipt, observations):
    """Require loaded E2 grids and trip context before claiming V1 T_MEASURE."""
    result={}
    for detector in ('ramp_storage_e2','shared_boundary_e2'):
        path=o.verify_binding(executed_receipt['output_bindings'][detector+'.xml'])
        cursor=0;rows=[]
        for item in ET.parse(path).getroot().findall('interval'):
            o.require(item.get('id')==detector,'E2 identity mismatch')
            begin=m.number(item.get('begin'),'E2 begin',0);end=m.number(item.get('end'),'E2 end',0)
            o.require(begin==cursor and end==min(begin+30,2700) and begin<2700,'E2 missing/extra/period interval')
            sampled=m.number(item.get('sampledSeconds'),'E2 sampledSeconds',0)
            for field in ('nVehEntered','nVehLeft','nVehSeen'):
                o.require(m.number(item.get(field),field,0).is_integer(),'E2 count nonintegral')
            for field in ('meanSpeed','meanTimeLoss'):
                v=m.number(item.get(field),field)
                o.require(v>=0 or (v==-1 and sampled==0),'E2 invalid contributed mean')
            for field in ('meanOccupancy','maxOccupancy'):
                o.require(m.number(item.get(field),field,0)<=100,'E2 occupancy range')
            rows.append(dict(item.attrib));cursor=end
        o.require(cursor==2700,'E2 incomplete coverage')
        result[detector]={'rows':rows,'scope':'named ordinary lane only; full path uses FCD'}
    for trip in observations['tripinfo'].values():
        if trip['depart']>=0:
            for field in ('timeLoss','duration'):m.number(trip.get(field),field,0)
    return result


def descriptive_companions(observations):
    trajectories=observations['trajectories'];trips=observations['tripinfo'];horizon=len(observations['tls_states'])
    accumulation=[0]*horizon;stopped=[0]*horizon;entries=[];exits=[];R_stops={};U_exposure={}
    for vid,samples in sorted(trajectories.items()):
        group=m.group(vid)
        if group=='M':
            for sample in samples:
                if sample.lane in ('main_up_0','main_up_1') and 200<=sample.pos<1200:
                    accumulation[sample.time]+=1;stopped[sample.time]+=sample.speed<=.1
            for pos,target in ((200,entries),(1200,exits)):
                bracket=m.crossing(samples,{'main_up_0','main_up_1'},pos)
                target.append({'vehicle_id':vid,'bracket':bracket,'value_state':'observed' if bracket else 'no_contributors'})
        elif group=='R':
            regions={}
            for sample in samples:
                if sample.speed<=.1:
                    region=next(k for k,lanes in m.REGIONS.items() if sample.lane in lanes)
                    regions.setdefault(region,[]).append(sample.time)
            R_stops[vid]={region:{'first_label':min(ts),'last_label':max(ts),'label_count':len(ts)} for region,ts in regions.items()}
        elif group=='U':
            U_exposure[vid]=[s.time for s in samples if s.lane=='shared_approach_0' and s.speed<=.1 and observations['regional_stops']['shared']['R'][s.time]>0]
    time_loss={}
    for group in 'MRUX':
        rows=[t for vid,t in trips.items() if m.group(vid)==group and t['depart']>=0]
        known=[t['timeLoss'] for t in rows if t.get('timeLoss') is not None]
        time_loss[group]={'value':statistics.mean(known) if known else None,'value_state':'observed' if known else 'missing_observation','entered_count':len(rows),'observed_count':len(known),'unarrived_count':sum(t['arrival']<0 for t in rows),'scope':'whole observed trip records; unfinished values retained; not causal loss'}
    return {'feeder_accumulation_1Hz':accumulation,'feeder_technical_stops_1Hz':stopped,'feeder_entries':entries,'feeder_exits':exits,'R_regional_first_last_stopped_labels':R_stops,'propagation_scope':'ordered raw regional stopping context, not causal propagation proof','U_shared_R_coexposure_labels_by_ID':U_exposure,'U_unique_exposed_count':sum(bool(v) for v in U_exposure.values()),'trip_time_loss_context':time_loss,'TLS_states_link0_RU_link1_X':observations['tls_states'],'endpoints':observations['endpoints']}


def assemble_rule_tables(analysis_manifest_bindings,output,*,allow_fixture=False):
    """All352+14 rows exist even for partial/unpaired/stopped execution."""
    output=o.checked_path(output,o.BATCH,exists=False)
    o.require(output.parent.is_dir() and not output.exists(),'rule output unavailable/exists')
    output.mkdir();observed={};bindings={};scopes=set()
    try:
        for binding in analysis_manifest_bindings:
            manifest=o.read_json(o.verify_binding(binding));run_id=manifest['run_id']
            o.require(run_id not in observed,'duplicate analysis run')
            o.require(manifest['status']=='qualified_offline_measurements' and manifest['card']==o.bind(o.CARD),'unqualified analysis/card mismatch')
            o.verify_binding(manifest['implementation'])
            o.require(manifest['implementation']==o.bind(Path(m.__file__)),'analysis implementation not current')
            row=o.registered_run(o.load_card(),run_id)
            if row['version']=='V1':
                identity=x.verify_executed_source(manifest['source_identity']['execution_receipt'],run_id,allow_fixture=allow_fixture)
                scopes.add(identity['evidence_scope'])
            else:
                m.verify_archive_identity(o.load_card(),row,manifest['source_bindings'])
            data=o.read_json(o.verify_binding(manifest['output']))
            o.require(data['analysis_qualification']=='qualified','invalid measurements')
            observed[run_id]=data;bindings[run_id]=binding
        o.require(len(scopes)<=1,'mixed real and synthetic V1 sources')
        keys,sens=o.read_rule_keys(o.load_card());rows=[{**r,'value_state':'not_applicable' if r['applicable']=='false' else 'missing_observation','result':'not_applicable' if r['applicable']=='false' else 'not_evaluated'} for r in keys];sensitivity=[dict(r) for r in sens]
        pair_results={};sensitivity_results={}
        for seed in ('17','23'):
            left=f'S6_V1_ML_S{seed}';right=f'S6_V1_C_S{seed}'
            if left in observed and right in observed:
                a=observed[left]['feeder_science_inputs'];b=observed[right]['feeder_science_inputs']
                pair_results[seed]=m.evaluate_science_pair(a,b,allow_fixture=allow_fixture)
                sensitivity_results[seed]=m.evaluate_registered_sensitivities(a,b,allow_fixture=allow_fixture)
        for row in rows:
            if row['applicable']=='false':continue
            run_id=f"S6_{row['version']}_{row['condition']}_S{row['seed']}"
            if run_id not in observed:continue
            data=observed[run_id];rule=row['rule_id'];passed=None
            if rule in ('T_SOURCE','T_TIME','T_ENTRY','T_MEASURE'):passed=True
            elif rule=='S_M_INFLOW':passed=data['inlet']['scientific_result']=='supported_bounded'
            elif rule=='S_REF_QUAL':
                v=data['feeder_science_inputs'];passed=m.reference_qualification(v['bin_speeds'],v['certain_counts'],v['cohort']['bounds']['certain_count'])
            elif row['version']=='V1' and row['seed'] in pair_results:
                result=pair_results[row['seed']]
                passed={'M_PRIMARY':result['M_PRIMARY'],'M_SUPPORT':bool(result['M_SUPPORT_blocks']),'R_SUPPORT':bool(result['R_SUPPORT_blocks']),'S_RU_EXPOSURE':bool(result['RU_SUPPORT_blocks']),'Q4_COEXIST':bool(result['Q4_blocks'])}.get(rule)
            elif row['version']=='V1' and rule in ('M_PRIMARY','M_SUPPORT','R_SUPPORT','S_RU_EXPOSURE','Q4_COEXIST'):
                row.update(value_state='not_paired',result='not_evaluated');continue
            if passed is not None:
                evidence=[bindings[run_id]]
                if rule in ('M_PRIMARY','M_SUPPORT','R_SUPPORT','S_RU_EXPOSURE','Q4_COEXIST') and row['version']=='V1':evidence.append(bindings[f"S6_V1_ML_S{row['seed']}"])
                row.update(value=int(passed),value_state='observed' if passed else 'observed_zero',value_kind='registered_boolean_rule_result',result='supported_bounded' if passed else 'not_resolved',evidence_bindings=evidence)
        for row in sensitivity:
            if row['seed'] in sensitivity_results:
                result=sensitivity_results[row['seed']][row['sensitivity_id']]
                row.update(value_state='observed',result=result['scientific_result'],evidence_bindings=[bindings[f"S6_V1_{c}_S{row['seed']}"] for c in ('ML','C')])
            elif any(f"S6_V1_{c}_S{row['seed']}" in observed for c in ('ML','C')):row.update(value_state='not_paired',result='not_evaluated')
        summaries={'main':m.validate_rule_results(rows,keys),'sensitivity':m.validate_rule_results(sensitivity,sens,True)}
        for name,value in [('resolution_rule_results.json',rows),('sensitivity_rule_results.json',sensitivity),('pair_results.json',pair_results),('rule_summary.json',summaries)]:x.exclusive_json(output/name,value)
        for name,items in [('resolution_rule_results.csv',rows),('sensitivity_rule_results.csv',sensitivity)]:
            fields=list(dict.fromkeys(k for row in items for k in row))
            with (output/name).open('x',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
                writer.writerows({k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in items)
        manifest={'analysis_inputs':analysis_manifest_bindings,'implementation':o.bind(Path(__file__)),'evidence_scope':next(iter(scopes),'historical_or_empty'),'launch_eligible':False,'outputs':{p.name:o.bind(p) for p in output.iterdir() if p.is_file()},'counts':{'main':352,'sensitivity':14},'all_required_supported':summaries['main']['all_required_supported'] and summaries['sensitivity']['all_required_supported']}
        x.exclusive_json(output/'rule_manifest.json',manifest)
        return manifest
    except Exception as exc:
        x.exclusive_json(output/'rule_error.json',{'analysis_qualification':'blocked_by_evidence_error','error':str(exc),'type':type(exc).__name__})
        raise
