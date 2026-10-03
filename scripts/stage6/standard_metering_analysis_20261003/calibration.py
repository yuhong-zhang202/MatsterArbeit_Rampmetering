"""Read existing 30 s E1 products; no simulation or parameter search."""
import csv,json,hashlib,statistics,argparse
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(root,out):
 root=Path(root);out=Path(out)
 source=root/'results/tables/stage6_boundary_search_20261002_v1/occupancy_three_seeds/downstream_20m_30s.csv'
 data=list(csv.DictReader(source.open()));rows=[];sources={str(source):sha(source)}
 for seed in [17,23,42]:
  for ramp in [0,600,750,900]:
   run=f'M3600_R{ramp}_S{seed}';p=root/'data/processed/stage6_boundary_search_20261002_v1'/run/'summary.json';z=json.loads(p.read_text());sources[str(p)]=sha(p)
   rr=[r for r in data if r['run_id']==run and 1200<=float(r['begin'])<3000]
   if len(rr)!=60 or len({r['begin'] for r in rr})!=60:raise ValueError('coverage '+run)
   occ=[float(r['occupancy_two_lane_mean_pct']) for r in rr];delta=[70*(11-v) for v in occ]
   row=dict(run_id=run,bins=60,occupancy_mean_pct=statistics.mean(occ),occupancy_min_pct=min(occ),occupancy_max_pct=max(occ),flow_mean_veh_h=statistics.mean(float(r['flow_two_lane_sum_veh_h']) for r in rr),feedback_delta_mean_veh_h=statistics.mean(delta),feedback_delta_min_veh_h=min(delta),feedback_delta_max_veh_h=max(delta),bins_delta_abs_gt300=sum(abs(v)>300 for v in delta),bins_delta_abs_gt600=sum(abs(v)>600 for v in delta))
   for profile in 'PLS':row[profile+'_supported_seconds']=z['state']['windows']['evaluation'][profile]["supported_time_union_seconds"]
   rows.append(row)
 out.mkdir(parents=True,exist_ok=False)
 with (out/'existing_occupancy_flow_state.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (out/'provenance.json').write_text(json.dumps(dict(sources=sources,script_sha256=sha(__file__),kind='EXPLORATORY_PRE_IMPLEMENTATION_DIAGNOSTIC',target_pct=11,gain_veh_h_per_percentage_point=70,limits='Static feedback increments on existing OPEN observations. Not simulated closed-loop rates; no recursion, actuation, delay or stability validation. P/L/S durations are supported states, not clean onset. 12 runs, three independent seeds; bins are not independent replications.'),indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args();main(a.root,a.out)
