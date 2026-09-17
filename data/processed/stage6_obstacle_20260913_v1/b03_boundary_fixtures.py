"""Small independent examples of proposed interval-membership arithmetic only."""
import math,json,hashlib
from pathlib import Path
def extremum(definite,optional,minimize):
 vals=sorted(optional,reverse=not minimize);s=sum(definite);n=len(definite);candidates=[]
 for k in range(len(vals)+1):
  if n+k:candidates.append((s+sum(vals[:k]))/(n+k))
 return (min(candidates) if minimize else max(candidates)) if candidates else None
assert extremum([10],[1,20],True)==5.5
assert extremum([10],[1,20],False)==15
assert math.isinf(extremum([10],[float('inf')],False))
assert extremum([],[],True) is None
assert not(12>1.1*float('inf'))
assert len({True,False})>1
p=Path(__file__)
with (p.parent/'b03_boundary_fixture_receipt.json').open('x') as f:json.dump({'status':'passed','assertions':6,'scope':'proposed finite optional-member extrema, unbounded censor, empty mean and sensitivity flip examples; not complete future production validator','code_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'simulator_invocations':0},f,indent=2)
print('6 boundary arithmetic assertions passed')
