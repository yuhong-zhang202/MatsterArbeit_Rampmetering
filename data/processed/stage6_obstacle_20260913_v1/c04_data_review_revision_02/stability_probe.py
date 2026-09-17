import sys,os,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from src.analysis import stage6_h2_measurement as m,stage6_h2_pipeline as p
order=list({'M_flow.2','M_flow.0','M_flow.12','M_flow.9'})
if os.environ['AUDIT_ORDER']=='reverse':order.reverse()
tr={v:[m.Sample(t,'main_up_0',pos,float(v.split('.')[1])+10) for t,pos in [(300,100),(301,200),(302,1100),(303,1200)]] for v in order}
trips={v:{'depart':300,'arrival':305,'timeLoss':1,'duration':5} for v in order}
obs={'trajectories':tr,'tripinfo':trips,'regional_stops':m.regional_stops(tr,2700),'inlet':{},'analysis_qualification':'qualified','tls_states':['Gr']*2700,'endpoints':{}}
x={'cohort':m.domain_cohort(tr,trips,'main_up',200,1200),'science':m.feeder_science_inputs(obs),'context':p.descriptive_companions(obs)}
sys.stdout.write(json.dumps(x,sort_keys=True,allow_nan=False))
