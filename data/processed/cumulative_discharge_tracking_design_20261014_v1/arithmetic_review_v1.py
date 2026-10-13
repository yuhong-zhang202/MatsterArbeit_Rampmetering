"""Exact design arithmetic only: not a runtime scheduler or production test."""
from fractions import Fraction as F
import json
R=F(750);CANDIDATES=(8,10)
def text(x):return str(x) if isinstance(x,F) else x
def scores(D,rate):return {T:D+rate*T/3600-2 for T in CANDIDATES}
def choice(values):return min(values,key=lambda T:(abs(values[T]),-T))
def triage(N):
 if N is None:return 'UNKNOWN_NO_OBSERVED_COUNT'
 if N!=2:return 'STOP_DIAGNOSE_NO_AUTOMATIC_COMPENSATION'
 return 'NORMAL_COMPLETED_TWO_VEHICLE_ASSUMPTION'
def main():
 D=F(0);elapsed=0;C=F(0);N=0;E=0;table=[]
 for i in range(10):
  candidates=scores(D,R);T=choice(candidates);elapsed+=T;C+=R*T/3600;N+=2;E+=2;D=C-N
  table.append(dict(cycle=i+1,T_s=T,cumulative_s=elapsed,candidate_predicted_errors={str(t):text(v)for t,v in candidates.items()},C=text(C),E=E,N_assumed=N,D=text(D),Dq=text(C-E),Ds=E-N))
 assert [q['T_s']for q in table[:5]]==[10,10,8,10,10]
 assert [q['T_s']for q in table[5:]]==[10,10,8,10,10]
 expected_C=['25/12','25/6','35/6','95/12','10'];expected_D=['1/12','1/6','-1/6','-1/12','0']
 assert [q['C']for q in table[:5]]==expected_C and [q['D']for q in table[:5]]==expected_D
 assert table[4]['cumulative_s']==48 and table[4]['N_assumed']==10 and table[4]['D']=='0'
 assert table[9]['cumulative_s']==96 and table[9]['N_assumed']==20 and table[9]['D']=='0'
 assert max(abs(F(q['D']))for q in table)==F(1,6)
 tie=scores(F(1,8),R);assert abs(tie[8])==abs(tie[10])==F(5,24) and choice(tie)==10
 # Design-only midcycle change. Actual integration differs from prediction.
 predicted_first_C=R*10/3600;actual_C=R*7/3600+F(900)*3/3600;D=actual_C-2
 next_values=scores(D,F(900));T=choice(next_values);assert predicted_first_C==F(25,12) and actual_C==F(53,24) and D==F(5,24) and T==8
 second_C=actual_C+F(900)*T/3600;assert second_C-4==D
 partial_C=R*4/3600;partial_E=0;partial_N=2;assert partial_C-partial_N==(partial_C-partial_E)+(partial_E-partial_N)==F(-7,6)
 assert partial_E-partial_N==-2 # Not a completed-cycle shortfall.
 return dict(classification='DESIGN_MATHEMATICS_NOT_ACTUAL_SUMO_NOT_IMPLEMENTATION_VALIDATION',verdict='PASS_EXACT_DESIGN_ARITHMETIC_ONLY',assumptions=['D0=0','constant request750','exactly2 actual entries per completed packet','no boundary admission delay','no safety UNKNOWN/STOP','observed counts assumed solely for arithmetic'],constant750_two_blocks=table,repeat_block_period_s=48,nominal_block_vehicles=10,nominal_block_average_veh_h=text(F(10*3600,48)),observed_N=None,complete_boundary_error_bound_for_this_example='1/6',within_cycle_bound_claimed=False,tie_case=dict(D='1/8',predicted_errors={str(t):text(v)for t,v in tie.items()},selected_T_s=10),midcycle_request_change_example=dict(requests_relative_s=[dict(t=0,r=750),dict(t=7,r=900)],first_T_s=10,predicted_C_if_constant=text(predicted_first_C),actual_C_integral_under_toy_changes=text(actual_C),assumed_N_at_boundary=2,actual_D_under_toy=text(D),next_candidate_scores={str(t):text(v)for t,v in next_values.items()},selected_next_T_s=T,second_boundary_C=text(second_C),second_assumed_N=4,second_D=text(second_C-4),previous_request_feedback_state_modified=False),partial_at_t4=dict(C=text(partial_C),E=partial_E,N_assumed=partial_N,D=text(partial_C-partial_N),Dq=text(partial_C-partial_E),Ds=partial_E-partial_N,meaning='Observed partial hypothetical, not completed deficiency or violation of boundary-only bound'),unobserved_ledgers=dict.fromkeys(('C','E','N','D','Dq','Ds')),count_condition_examples={str(n):triage(n)for n in (0,1,2,3,None)},supported_rate_range=[720,900],unsupported_examples=[300,600,719,901],native_runs=0,production_scheduler_created=False,formal_acceptance_tolerance_created=False)
if __name__=='__main__':print(json.dumps(main(),indent=2))
