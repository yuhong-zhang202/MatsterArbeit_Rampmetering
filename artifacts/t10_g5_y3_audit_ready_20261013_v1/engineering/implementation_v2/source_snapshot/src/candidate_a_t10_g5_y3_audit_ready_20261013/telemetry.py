"""Pure identity journal; records existing getter values, never changes vehicles."""
import math
from src.candidate_a_t10_g5_y3_20261013.adapter import inventory,require
GETTERS={'accel_m_s2':'getAccel','normal_decel_m_s2':'getDecel','emergency_decel_m_s2':'getEmergencyDecel','tau_s':'getTau','action_step_s':'getActionStepLength','sigma':'getImperfection','max_speed_m_s':'getMaxSpeed'}

def snapshot(conn,t,stage):
    require(type(t) is int and conn.simulation.getTime()==t and stage in ('BEFORE_MOTION','AFTER_ACK'),'IDENTITY_JOURNAL_TIME_UNKNOWN')
    world,loaded,pending=inventory(conn);ids=set(world)|set(loaded)|set(pending);rows={}
    for vid in sorted(ids):
        v=conn.vehicle;values={k:getattr(v,g)(vid) for k,g in GETTERS.items()}
        require(all(type(x) in (int,float) and math.isfinite(x) for x in values.values()),'IDENTITY_JOURNAL_NUMERIC_UNKNOWN')
        rows[vid]=dict(vehicle_id=vid,time_s=t,type_id=v.getTypeID(vid),route=list(v.getRoute(vid)),speed_mode=v.getSpeedMode(vid),lane_change_mode=v.getLaneChangeMode(vid),**values)
    require(conn.simulation.getTime()==t,'IDENTITY_JOURNAL_TIME_CHANGED')
    return dict(time_s=t,stage=stage,active_ids=sorted(world),loaded_ids=sorted(loaded),pending_ids=sorted(pending),vehicle_states=rows,model_scope='bound vType/carFollowModel input; private native branch not observed',setter_calls=0)
