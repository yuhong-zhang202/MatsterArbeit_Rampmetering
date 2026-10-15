"""Read four saved API-fault boundaries only; no runtime imports or execution."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'artifacts/thesis_actuator_readiness_20261015_v1/engineering/review_round2_v1/fixed_failure_bundles'
OUT=Path(__file__).parent


def read(path):return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

def need(ok,why):
    if not ok:raise ValueError(why)


def main():
    results={}
    for name in ('0_setter','600_setter','600_readback','603_yellow'):
        p=BASE/name;stop=json.loads((p/'SYNTHETIC_STOP.json').read_text());rows=read(p/'control_setters.jsonl');groups={}
        for row in rows:groups.setdefault(row['setter_id'],[]).append(row)
        clock=stop['actual_clock'];last=rows[-1]
        need(stop['classification']=='FAKE_API_FAILURE_NO_NATIVE' and last==stop['last_control_setter'],'stop not bound to durable setter')
        for group in groups.values():
            need(group[0]['status']=='ATTEMPTED' and group[0]['call_completed'] is False,'no pre-call attempt')
            statuses=[r['status'] for r in group]
            if group is not list(groups.values())[-1]:
                need(statuses==['ATTEMPTED','CALL_RETURNED','READBACK_OBSERVED'],'preceding partial success missing')
            else:
                expected=['ATTEMPTED','CALL_RETURNED','READBACK_UNKNOWN_STOP'] if name=='600_readback' else ['ATTEMPTED','CALL_FAILED_STOP']
                need(statuses==expected,'failure sequence')
            for r in group:need(r['time_s']<=clock,'setter after stop')
        need(last['time_s']==clock,'failure boundary clock')
        signal=last['actual_signal'];fields=signal['fields']
        need(signal['scope']=='CURRENT_GETTERS_AFTER_CONTROL_NOT_MOVEMENT_ACK','getter not ACK distinction')
        for key,r in fields.items():
            need((r['status']=='OBSERVED' and r['value'] is not None and r['error'] is None) or
                 (r['status']=='UNKNOWN' and r['value'] is None and r['error']),'unknown evidence discarded')
        need(fields['time_s']['value']==clock,'readback clock')
        if name=='600_readback':
            need(last['call_completed'] is True and fields['phase']['status']=='UNKNOWN' and not signal['complete'],'unknown phase replaced with expected phase')
        else:
            need(last['call_completed'] is False and last['error']==stop['error'] and
                 last['effect_of_failed_call']=='UNKNOWN_POSSIBLE_PARTIAL_APPLICATION','failed call effect asserted')
        verified=[r for r in read(p/'step_ack.jsonl') if r.get('actual_time_verified')]
        need(all(r['requested_target_s']<=clock and r['actual_readback_s']==r['requested_target_s'] for r in verified),'advance after failed setter')
        need((max([r['requested_target_s'] for r in verified],default=None))==stop['last_completed_s'],'last completed ACK mismatch')
        if clock:
            posts=read(p/'post_steps.jsonl');need(max(r['time_end_s'] for r in posts)==stop['last_accounted_s']==clock,'last accounted mismatch')
        events=read(p/'command_events.jsonl')
        applications=[e for e in events if e['event'] in ('ACK_OBSERVED','PACKET_ACK_OBSERVED')]
        need(all(e['first_green_ACK_s']<=clock and e['application_global_s']<clock for e in applications),'unobserved application after setter failure')
        if name.startswith('600_'):need(not applications,'first green applied without movement ACK')
        if name=='603_yellow':
            need(last['expected_readback']['state']=='y' and fields['state']['value']=='G' and fields['phase']['value']==0,'failed yellow actual state lost')
        results[name]=dict(status='PASS_SAVED_FAULT_BOUNDARY_ONLY',clock=clock,last_verified_ACK=stop['last_completed_s'],last_accounted=stop['last_accounted_s'],setter_status=last['status'],call_completed=last['call_completed'],unknown_fields=[k for k,v in fields.items() if v['status']=='UNKNOWN'],native_safety='NOT_TESTED',full_reader='NOT_TESTED')
    with (OUT/'SETTER_BOUNDARY_READBACK_V1.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
    print('FOUR_SAVED_SETTER_BOUNDARIES_PASS_NO_EXECUTION')

if __name__=='__main__':main()
