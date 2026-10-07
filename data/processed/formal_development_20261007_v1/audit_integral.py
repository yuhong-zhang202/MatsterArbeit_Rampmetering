"""Cost identity verified independently against cumulative SUMO summary output."""
import json, xml.etree.ElementTree as ET
from pathlib import Path
from audit_reuse import sha

def main():
    here=Path(__file__).resolve().parent
    source=here/'reuse_audit.json';audit=json.loads(source.read_text());rows=[]
    for run in audit['runs']:
        raw=Path(run['raw']);package=Path(run['card']).parent
        plan=ET.parse(package/'demand.rou.xml').getroot().findall('vehicle')
        planned_exposure=sum(4200-float(v.get('depart')) for v in plan)
        steps=ET.parse(raw/'sumo_summary.xml').getroot().findall('step')
        src=planned_exposure-sum(int(s.get('inserted')) for s in steps)
        net=sum(int(s.get('running')) for s in steps)
        total=planned_exposure-sum(int(s.get('arrived')) for s in steps)
        expected={k:sum(c[k] for c in run['classes']) for k in ['source_wait_T_s','in_network_T_s','system_time_T_s']}
        residuals={k:v-expected[k] for k,v in [('source_wait_T_s',src),('in_network_T_s',net),('system_time_T_s',total)]}
        assert max(map(abs,residuals.values()))<1e-6
        rows.append(dict(run_id=run['run_id'],source_wait_integral_s=src,in_network_integral_s=net,system_time_integral_s=total,residuals_s=residuals,summary_sha256=sha(raw/'sumo_summary.xml')))
    # Small known examples: complete, inserted but unfinished, and never inserted.
    T=10.;examples=[(0.,2.,5.,5.,2.,3.),(1.,4.,float('inf'),9.,3.,6.),(2.,float('inf'),float('inf'),8.,8.,0.)]
    for p,d,a,expected_s,expected_w,expected_n in examples:
        s=min(a,T)-p;w=min(d,T)-p;n=min(a,T)-min(d,T)
        assert (s,w,n)==(expected_s,expected_w,expected_n) and s==w+n
    result=dict(status='PASS',analysis_classification='DEVELOPMENT',source_audit_sha256=sha(source),script_sha256=sha(__file__),known_example_cases=3,runs=rows,scope='Aggregate independent cumulative-count integral, 1s labels, all nine runs complete; not an FCD lane-level or controller re-audit.')
    with (here/'reuse_integral_audit.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'status':'PASS','runs':len(rows),'max_abs_residual_s':max(abs(v) for r in rows for v in r['residuals_s'].values()),'known_example_cases':3}))

if __name__=='__main__':main()
