import json,sys,math
from pathlib import Path
from unittest.mock import patch
R=Path.cwd();sys.path.insert(0,str(R));D=R/'data/processed/stage6_obstacle_20260913_v1/d2_data_review_revision_01'
from src.analysis import stage6_h2_measurement as m
read=lambda p:json.loads(p.read_text())
ref=read(D/'S6_V1_ML_S17_registered_analysis/measurements.json')['feeder_science_inputs'];chal=read(D/'S6_V1_C_S17_registered_analysis/measurements.json')['feeder_science_inputs'];ind=read(D/'independent_pair_and_sensitivities.json')
with patch('subprocess.Popen',side_effect=AssertionError('No process permitted')):actual=m.evaluate_registered_sensitivities(ref,chal)
checks=[]
for key,result in actual.items():
 for field in ('S_REF_QUAL','S_M_INFLOW','M_PRIMARY','M_SUPPORT_blocks','R_SUPPORT_blocks','RU_SUPPORT_blocks','Q4_blocks','bin_certain_counts_minimum','scientific_result'):
  assert result[field]==ind[key][field],(key,field,result[field],ind[key][field]);checks.append(key+'/'+field)
 for i,(a,b) in enumerate(zip(result['bin_speed_ratios'],ind[key]['bin_speed_ratios'])):
  assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10);checks.append(key+'/ratio/'+str(i))
with (D/'sensitivity_component_verification.json').open('x') as f:json.dump({'status':'PASS','component_comparisons':len(checks),'sensitivity_cases':7,'checks':checks,'registered_results':actual,'scientific_result':'not_resolved','simulation_calls':0},f,indent=2,sort_keys=True)
print(len(checks),'sensitivity component comparisons PASS')
