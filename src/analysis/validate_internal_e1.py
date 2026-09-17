"""Offline validation of the approved pair of mainline internal E1 loops."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import shlex
import sys
import xml.etree.ElementTree as ET

from build_stage2_g1_diagnostic import (digest, verify_hashes, reserve_directories,
                                      e1_row, check_intervals, summarize_e1, csv_write, json_write)

LOOPS = {"mainline_merge_entry_e1_l0": ":freeway_merge_1_0",
         "mainline_merge_entry_e1_l1": ":freeway_merge_1_1"}
WINDOWS = {"full": (0,2700), "A": (0,1500), "B": (300,1500), "post": (1500,2700)}


def combined_summary(rows, begin, end):
    """Parallel lane flows sum; speed contribution weighted; occupancy stays per lane."""
    lanes = {lane:summarize_e1([r for r in rows if r['lane_id']==lane],begin,end)
             for lane in sorted({r['lane_id'] for r in rows})}
    denom = sum(v['speed_contribution_denominator'] for v in lanes.values())
    return {'begin_s':begin,'end_s':end,'lane_summaries':lanes,
            'total_flow_vehph':sum(v['flow_vehph'] for v in lanes.values()),
            'nVehContrib':sum(v['nVehContrib'] for v in lanes.values()),
            'speed_contribution_denominator':denom,
            'speed_mps':sum(v['speed_mps']*v['speed_contribution_denominator'] for v in lanes.values() if v['speed_mps'] is not None)/denom if denom else None,
            'occupancy_aggregation':'none; separate lane occupancy percentages retained'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ('runtime-dir','reference-dir','output-dir','table-dir','figure-dir'):
        parser.add_argument('--'+arg,type=Path,required=True)
    args=parser.parse_args(); run=args.runtime_dir.resolve(); ref=args.reference_dir.resolve()
    out=args.output_dir.resolve(); tables=args.table_dir.resolve(); figures=args.figure_dir.resolve()
    summary=json.loads((run/'summary.json').read_text())
    cfg=ET.parse(run/'scenario.sumocfg').getroot()
    netpath=(run/cfg.find('input/net-file').attrib['value']).resolve()
    demandpath=(run/cfg.find('input/route-files').attrib['value']).resolve()
    addpath=(run/cfg.find('input/additional-files').attrib['value']).resolve()
    add=ET.parse(addpath).getroot(); network=ET.parse(netpath).getroot()
    loops={n.attrib['id']:n for n in add.findall('inductionLoop') if n.attrib['id'] in LOOPS}
    assert set(loops)==set(LOOPS)
    command=summary['sumo_command']
    def source(flag):return Path(command[command.index(flag)+1])
    trip=source('--tripinfo-output'); fcd=source('--fcd-output'); routes=source('--vehroute-output')
    paths=[run/'summary.json',run/'scenario.sumocfg',netpath,demandpath,addpath,trip,fcd,routes,
           ref/'summary.json',ref/'outputs/tripinfo.xml',ref/'outputs/fcd.xml',Path(__file__).resolve(),
           Path(__file__).with_name('build_stage2_g1_diagnostic.py'),
           Path(__file__).resolve().parents[2]/'docs/STAGE2_S3_S4_ENGINEERING_REPORT.md']
    paths.extend(Path(n.attrib['file']) for n in loops.values())
    hashes={str(p):digest(p) for p in paths}
    reserve_directories([out,tables,figures])
    rows=[]; topology={}
    for ident,node in loops.items():
        lane=node.attrib['lane']; assert lane==LOOPS[ident] and float(node.attrib['pos'])==4.32
        lane_node=next(n for n in network.iter('lane') if n.attrib['id']==lane)
        incoming=[n.attrib for n in network.findall('connection') if n.get('via')==lane]
        assert len(incoming)==1 and incoming[0]['from']=='main_up' and incoming[0]['to']=='main_down'
        assert float(lane_node.attrib['length'])==8.64
        topology[ident]={'lane':lane,'position_m':4.32,'lane_length_m':8.64,'incoming_connection':incoming,
                         'scope':'M-only route topology; aggregate E1 has no vehicle IDs'}
        raw=ET.parse(node.attrib['file']).getroot().findall('interval')
        block=[e1_row(n.attrib,ident,lane) for n in raw];check_intervals(block);rows.extend(block)
    trips={n.attrib['id']:n.attrib for n in ET.parse(trip).getroot().findall('tripinfo')}
    assert len(trips)==len(ET.parse(trip).getroot().findall('tripinfo'))
    main_trips={k:v for k,v in trips.items() if k.startswith('M_flow.')}
    demand=ET.parse(demandpath).getroot();mflow=next(n for n in demand.findall('flow') if n.attrib['id']=='M_flow')
    planned=int(mflow.attrib['number'])
    route_rows={n.attrib['id']:n.find('route').attrib['edges'].split() for n in ET.parse(routes).getroot().findall('vehicle')}
    assert all(route_rows[k]==['main_up','main_down'] for k in main_trips)
    summaries={name:combined_summary(rows,*bounds) for name,bounds in WINDOWS.items()}
    cohort={name:{'actual_M_departures':sum(a<=float(v['depart'])<b for v in main_trips.values()),
                  'M_arrivals':sum(a<=float(v['arrival'])<b for v in main_trips.values()),
                  'scope':'event windows, not interchangeable with detector passage windows'}
            for name,(a,b) in WINDOWS.items()}
    # Independent known-record reference equality, not a repeated full semantic diff.
    reference_trips={n.attrib['id']:n.attrib for n in ET.parse(ref/'outputs/tripinfo.xml').getroot().findall('tripinfo')}
    checked_ids=['M_flow.0','M_flow.1332','R_flow.0','R_flow.299','U_flow.149']
    assert all(trips[k]==reference_trips[k] for k in checked_ids)
    # FCD only validates observed examples; short lanes are not fully sampled.
    fcd_examples=[]; observed_ids=set(); class_samples=Counter();selected_times={0,68,450,475,1499,1500,1987,2373,2401}
    frame_records={}
    for _,step in ET.iterparse(fcd,events=('end',)):
        if step.tag!='timestep':continue
        t=float(step.attrib['time'])
        if t in selected_times:frame_records[t]=[v.attrib for v in step]
        for v in step:
            if v.get('lane') in LOOPS.values():
                observed_ids.add(v.attrib['id']);class_samples[v.attrib['id'].split('_')[0]]+=1
                if len(fcd_examples)<8:fcd_examples.append({'time_s':t,**v.attrib})
        step.clear()
    paired_frames=0
    for _,step in ET.iterparse(ref/'outputs/fcd.xml',events=('end',)):
        if step.tag!='timestep':continue
        t=float(step.attrib['time'])
        if t in selected_times:
            assert [v.attrib for v in step]==frame_records[t];paired_frames+=1
        step.clear()
    assert paired_frames==len(selected_times)
    extrema={ident:{'min_valid_speed_interval':min((r for r in rows if r['detector_id']==ident and r['speed_valid']),key=lambda r:r['speed_raw_mps']),
                    'max_valid_speed_interval':max((r for r in rows if r['detector_id']==ident and r['speed_valid']),key=lambda r:r['speed_raw_mps'])} for ident in LOOPS}
    result={'classification':'exploratory observation-only paired validation','runtime':str(run),'reference':str(ref),
            'source_windows':summary['time_windows'],'analysis_windows':WINDOWS,'topology':topology,'window_summaries':summaries,
            'M_cohort':{'planned':planned,'trip_records':len(main_trips),'arrived_by_end':sum(float(v['arrival'])>=0 and float(v['arrival'])<2700 for v in main_trips.values()),'windows':cohort},
            'aggregate_count_relationship':{'contributions':sum(r['nVehContrib'] for r in rows),'entered_detector':sum(r['nVehEntered'] for r in rows),'planned_M':planned,
                'equal_totals':sum(r['nVehContrib'] for r in rows)==planned,'per_ID_coverage':'not_verified','reason':'Aggregate equality and M-only topology do not establish per-vehicle membership, zero omissions or zero duplicates.'},
            'coverage':{'interval_rows':len(rows),'intervals_per_detector':90,'window_s': [0,2700],'no_contribution_speed_intervals':sum(not r['speed_valid'] for r in rows)},
            'extrema':extrema,'invalid_speed_with_contributions':[r for r in rows if r['missing_reason']=='negative_speed_with_contributions'],
            'fcd_examples':fcd_examples,'internal_lane_FCD_observed_unique_ID_count':len(observed_ids),'internal_lane_FCD_class_samples':dict(class_samples),
            'independent_reference_checks':{'trip_ids_equal':checked_ids,'FCD_frames_equal':sorted(selected_times),'full_semantic_regression':'Engineering result reused; not rerun by this script'},
            'interpretation':{'speed_valid':'nonnegative raw E1 speed with contributions only; not scientific traffic-state validity',
                'location':'M-only internal merge-entry passage measurement; not an upstream feeder/queue detector',
                'duration':'0/1500/1200 describes this finite cohort; no independent duration sufficiency test',
                'scientific_gate':'Breakdown, capacity drop, capacity, formal free-flow or per-ID completeness not established'},
            'limitations':['One seed and matched unchanged traffic; not an independent stochastic replication.','No new speed or duration threshold.','Do not require same-window departures, arrivals and passage contributions to match.','1 Hz FCD misses many short internal-lane passages and cannot validate exact E1 speed for every passage.']}
    csv_write(tables/'internal_e1_native.csv',rows)
    # Independently re-read XML and written CSV; no production parser reuse here.
    with (tables/'internal_e1_native.csv').open() as f: written=list(csv.DictReader(f))
    for ident,node in loops.items():
        selected=[r for r in written if r['detector_id']==ident]
        for raw,table in zip(ET.parse(node.attrib['file']).getroot().findall('interval'),selected,strict=True):
            for a,b in [('speed','speed_raw_mps'),('flow','flow_vehph'),('occupancy','occupancy_pct'),('nVehContrib','nVehContrib'),('nVehEntered','nVehEntered'),('begin','begin_s'),('end','end_s')]:assert float(raw.attrib[a])==float(table[b])
    result['independent_table_check']={'raw_rows_reconciled':len(written),'fields_per_row':7}
    json_write(out/'diagnostic.json',result)
    verify_hashes(hashes)
    json_write(out/'manifest.json',{'source_sha256':hashes,'command':shlex.join([sys.executable,*sys.argv]),'source_hashes_unchanged':True,
                                  'output_sha256':{str(p):digest(p) for p in [out/'diagnostic.json',tables/'internal_e1_native.csv']},
                                  'figure_decision':'No extra figure: two-loop window summaries and complete native table suffice for this feasibility check.'})
    print(json.dumps({'rows':len(rows),'summaries':summaries,'M_cohort':result['M_cohort'],'aggregate':result['aggregate_count_relationship'],'FCD_IDs':len(observed_ids)},indent=2))


if __name__=='__main__':main()
