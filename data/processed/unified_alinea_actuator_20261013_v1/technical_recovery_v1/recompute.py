"""Independent conditional source-expression arithmetic, no native imports."""
from pathlib import Path
import hashlib,json,math,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 eng=ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/technical_recovery_v1'
 ref=json.loads((eng/'SOURCE_EXPRESSION_REPLAY_V1.json').read_text());detail=json.loads((ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/runs/UA_FIXED750_S17_01/STOP_INPUT_DETAIL_V1.json').read_text());prior=json.loads((ROOT/'data/processed/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_01/revision01/STOP_INDEPENDENT_CHECK_V1.json').read_text())
 assert sha(eng/'SOURCE_EXPRESSION_REPLAY_V1.json')=='869183e078e231e7376f6b0ec2b86dc500e92f875249bcc9db2bddb03ce83e77'
 assert ref['actual_inputs']['before_speed_m_s']==detail['pre_world']['speed_m_s']==prior['before_speed_m_s']
 assert ref['actual_inputs']['after_speed_m_s']==detail['post_world']['speed_m_s']==prior['after_speed_m_s']
 v=detail['pre_world']['speed_m_s'];dt=detail['yellow_scope_for_vid'][0]['action_step_s'];decel=detail['terminal_before']['normal_decel_m_s2'];pos=detail['terminal_before']['position_m'];seen=204.49-pos
 assert dt==1 and decel==4.5 and seen==ref['actual_inputs']['distance_to_line_m']
 b=decel*dt;steps=math.floor(v/b);brake=sum(max(0,v-k*b)*dt for k in range(1,steps+1));threshold=seen-brake;offset=max(.1,min(threshold,threshold));stopdist=seen-offset
 def inverse(gap,epsilon):
  g=gap-epsilon;t=1.;s=dt;n=math.floor(.5-(t-.5*math.sqrt(s*s+4*(s*(2*g/b-t)+t*t)))/s);h=.5*n*(n-1)*b*s+n*b*t;r=(g-h)/(n*s+t);return n,h,n*b+r
 n,h,pred=inverse(stopdist,.001);_,_,reference=inverse(stopdist,0)
 assert pred==detail['post_world']['speed_m_s'] and (pred-v)/dt==-4.501 and (reference-v)/dt==-4.5
 pinned={}
 for name,x in ref['pinned_sources'].items():assert sha(Path(x['cache_path']))==x['sha256'];pinned[name]=x['sha256']
 c=json.loads((ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/packages/UA_FIXED750_S17_01/card.json').read_text());pkg=ROOT/c['package'];cfg=ET.parse(pkg/'scenario.sumocfg').getroot();types=[x.attrib for x in ET.parse(pkg/'demand.rou.xml').getroot().findall('vType')]
 assert all('carFollowModel' not in x for x in types) and cfg.find('.//tls.yellow.min-decel') is None
 return {'verdict':'PASS_CONDITIONAL_MATH_MATCH_NOT_BRANCH_OR_ACCEPTANCE','before_speed_m_s':v,'dt_s':dt,'normal_decel_m_s2':decel,'seen_m':seen,'Euler_positive_braking_steps':steps,'brakeGap_zero_headway_m':brake,'unobserved_majorStopOffset_required_ge_m':threshold,'conditional_lane_stop_offset_m':offset,'conditional_stopDist_m':stopdist,'inverse_n':n,'inverse_h_m':h,'predicted_post_speed_m_s':pred,'actual_post_speed_m_s':detail['post_world']['speed_m_s'],'speed_residual':pred-detail['post_world']['speed_m_s'],'predicted_alpha_m_s2':(pred-v)/dt,'without_distance_epsilon_reference_speed':reference,'without_distance_epsilon_reference_alpha':(reference-v)/dt,'actual_private_condition_observed':False,'actual_branch_traced':False,'compiler_binary_equivalence':False,'literal_strict_guard_pass':False,'numerical_exception_enabled':False,'pinned_sources_checked':pinned,'declared_vTypes':types,'default_model_evidence':'No override; pinned defaultKrauss. Effective native model branch not serialized.','source_formula_units':'gap/epsilon in m; velocity in m/s; acceleration in m/s2; dt1 makes numerical values coincide.','native_runs':0,'raw_reaudits':0}
if __name__=='__main__':print(json.dumps(main(),indent=2))
