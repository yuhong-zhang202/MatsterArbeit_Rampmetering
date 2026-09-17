"""Independent rule arithmetic; full means and blocks enumerated without SUT helpers."""
from pathlib import Path
import sys,statistics,copy,json,math,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[3];sys.path.insert(0,str(ROOT))
from src.analysis import stage6_h2_measurement as sut

def oracle(ref,chal,tt=1.1,sp=.95,persist=3,half=.05,cv=.05):
 means=[sum(b)/len(b) for b in ref['bin_speeds']];fst=[x for b in ref['bin_speeds'][:10] for x in b];lst=[x for b in ref['bin_speeds'][10:] for x in b]
 mu=sum(means)/20;sd=(sum((x-mu)**2 for x in means)/19)**.5
 eligible=ref['cohort']['bounds']['certain_count']>=500 and min(ref['certain_counts'])>=20
 reference=eligible and abs((sum(lst)/len(lst))/(sum(fst)/len(fst))-1)<=half and sd/mu<=cv
 a=ref['cohort']['bounds'];b=chal['cohort']['bounds'];primary=b['certain_count']>=500 and a['certain_count']>=500 and a['upper'] is not None and b['lower'] is not None and b['lower']>tt*a['upper']
 blocks=[]
 for start in range(20-persist+1):
  idx=list(range(start,start+persist))
  speedok=all(len(chal['bin_speeds'][i]) and (sum(chal['bin_speeds'][i])/len(chal['bin_speeds'][i]))/means[i]<=sp and min(ref['certain_counts'][i],chal['certain_counts'][i])>=20 for i in idx)
  if speedok:
   for sub in range(start,start+persist-2):
    inds=range(sub,sub+3)
    if sum(chal['r_counts'][i] for i in inds)>=10 and all(chal['r_counts'][i]>=1 and chal['ru_labels'][i]>=1 for i in inds):blocks.append(sub)
 passed=reference and primary and bool(blocks) and all(x['inlet']['scientific_result']=='supported_bounded' for x in [ref,chal])
 return {'S_REF_QUAL':reference,'M_PRIMARY':primary,'Q4_blocks':sorted(set(blocks)),'scientific_result':'supported_bounded' if passed else 'not_resolved'}
def item(tt,speed):return {'source_qualification':'qualified','cohort':{'bounds':{'certain_count':500,'lower':tt,'upper':tt,'bound_state':'bounded'}},'bin_speeds':[[speed]*25 for i in range(20)],'certain_counts':[25]*20,'r_counts':[4]*20,'ru_labels':[1]*20,'inlet':{'scientific_result':'supported_bounded'}}
base=(item(20,30),item(25,27));cases=[]
for name,mut in [('positive',lambda r,c:None),('lowcount',lambda r,c:c['cohort']['bounds'].update(certain_count=499)),('unbounded_reference',lambda r,c:r['cohort']['bounds'].update(upper=None)),('delayed_inlet',lambda r,c:c['inlet'].update(scientific_result='not_resolved')),('noR',lambda r,c:c.update(r_counts=[0]*20)),('noRU',lambda r,c:c.update(ru_labels=[0]*20)),('sample_gap',lambda r,c:c.update(certain_counts=[19]*20)),('no_speed',lambda r,c:c.update(bin_speeds=[[30]*25 for _ in range(20)])),('half_drift',lambda r,c:r.update(bin_speeds=[[30]*25 for _ in range(10)]+[[35]*25 for _ in range(10)])),('weights',lambda r,c:r.update(bin_speeds=[[29]*1]+[[30]*100 for _ in range(19)]))]:
 r,c=copy.deepcopy(base);mut(r,c)
 for sid,kw in [('primary',{}),('TT05',{'tt':1.05}),('TT15',{'tt':1.15}),('SPEED90',{'sp':.9}),('SPEED98',{'sp':.98}),('PERSIST240',{'persist':4}),('REF_STRICT',{'half':.03,'cv':.04}),('REF_LOOSE',{'half':.07,'cv':.06})]:
  expected=oracle(r,c,**kw);actual=sut.evaluate_science_pair(r,c,tt_ratio=kw.get('tt',1.1),speed_ratio=kw.get('sp',.95),speed_bins=kw.get('persist',3),reference_half_limit=kw.get('half',.05),reference_cv_limit=kw.get('cv',.05));assert all(actual[k]==v for k,v in expected.items()),(name,sid,expected,actual);cases.append({'fixture':name,'case':sid,'matches':True,'result':actual['scientific_result']})
with (D/'science_oracle_receipt.json').open('x') as f:json.dump({'status':'passed','comparisons':len(cases),'cases':cases,'production_hash':hashlib.sha256(Path(sut.__file__).read_bytes()).hexdigest(),'oracle':'independent explicit arithmetic and block enumeration; no production function used as expected value','SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},f,indent=2)
print('80 scientific arithmetic comparisons matched')
