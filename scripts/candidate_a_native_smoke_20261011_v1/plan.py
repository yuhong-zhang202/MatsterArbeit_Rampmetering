"""Proposal output only; intentionally no launch or SUMO/TraCI imports."""
import argparse
import json

def plan():
    return {'status':'PROPOSED_NOT_AUTHORIZED_NOT_LAUNCHABLE',
            'run_id':'CA_NATIVE_PHASE_R300_S17_SMOKE01','seed':17,
            'qMain_veh_h':3600,'qRamp_veh_h':900,'qUrban_veh_h':360,'qCross_veh_h':180,
            'service_command_veh_h':300,'activation_s':1200,'step_s':1,
            'phase_states':['G','y','r'],'phase_durations_s':[3,3,18],
            'nominal_n':2,'nominal_n_qualified':False,
            'first_activated_red_interval_s':[1206,1207],
            'mandatory_pause_after_first_red':True,'maximum_proposed_end_s':1272,
            'continuation_requires_separate_user_review':True,
            'old_envelope_policy':'SHADOW_ADVISORY_THIS_ISOLATED_PROFILE_ONLY',
            'old_guard_unchanged':True,'A1_proven':False,'rate_qualification_claim':False,
            'native_launch_bridge_implemented':False,'SUMO_launch_authorized':False}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Plan only. No launch option exists.')
    parser.parse_args()
    print(json.dumps(plan(),indent=2,allow_nan=False))
