"""Observe already-front-crossed rear clearance; no invented yellow deadline."""
import math
INTERNAL=':ramp_mid_0_0'


def require(ok,reason):
    if not ok:raise ValueError(reason)


class BodyTracker:
    def __init__(self):self.entries={};self.active=set();self.cleared={};self.last_time=None
    def observe(self,conn,time_s,world,crossings,motion):
        require(conn.simulation.getTime()==time_s,'BODY_TIME_UNKNOWN')
        require(self.last_time is None or time_s in (self.last_time,self.last_time+1),'BODY_FRAME_GAP')
        self.last_time=time_s
        ids=tuple(conn.vehicle.getIDList());internal=tuple(conn.lane.getLastStepVehicleIDs(INTERNAL))
        require(len(set(ids))==len(ids) and set(ids)==set(world),'BODY_WORLD_UNKNOWN')
        require(len(set(internal))==len(internal) and set(internal)=={v for v,w in world.items() if w['lane_id']==INTERNAL},'BODY_INTERNAL_COVERAGE_UNKNOWN')
        for x in crossings:
            vid=x['vehicle_id'];require(vid not in self.entries,'BODY_DUPLICATE_ENTRY')
            require(vid in internal and world[vid]['role']=='R','BODY_ENTRY_BINDING_UNKNOWN')
            self.entries[vid]={'vehicle_id':vid,'entry_time_begin_s':x['crossing_time_lower_s'],'entry_time_end_s':x['crossing_time_upper_s'],'entry_signal':motion}
            self.active.add(vid)
        rows=[];spanning=set()
        # Inspect all internal bodies, not only the last entrant.
        for vid in sorted(set(internal)|self.active):
            require(vid in ids and vid in internal and world[vid]['role']=='R','BODY_LOST_BEFORE_OBSERVED_CLEARANCE')
            pos=conn.vehicle.getLanePosition(vid);length=conn.vehicle.getLength(vid);speed=conn.vehicle.getSpeed(vid)
            require(all(type(x) in (int,float) and math.isfinite(x) for x in (pos,length,speed)) and 0<=pos<=81.98 and length>0 and speed>=0,'BODY_GEOMETRY_OR_SPEED_UNKNOWN')
            require(conn.vehicle.getLaneID(vid)==INTERNAL and abs(speed-world[vid]['speed_m_s'])<=1e-8,'BODY_FRAME_BINDING_UNKNOWN')
            rear=pos-length
            if rear<=0:
                require(vid in self.entries and vid not in self.cleared,'BODY_SPANNING_ENTRY_UNBOUND_OR_REGRESSED')
                self.active.add(vid);spanning.add(vid)
            if vid in self.active:
                row={**self.entries[vid],'observed_ACK_s':time_s,'observed_signal':motion,'head_position_m':pos,'length_m':length,'speed_m_s':speed,'rear_position_m':rear,'status':'REAR_SPANS_LINE' if rear<=0 else 'REAR_CLEAR_OBSERVED','red_rear_is_not_new_front_entry':True}
                if rear>0:self.cleared[vid]=time_s;self.active.remove(vid);row['first_actual_rear_clear_ACK_s']=time_s
                rows.append(row)
        require(self.active==spanning and conn.simulation.getTime()==time_s,'BODY_SPANNING_COVERAGE_UNKNOWN')
        return {'ACK_s':time_s,'signal':motion,'spanning_ids':sorted(spanning),'rows':rows,'claim':'actual per-ACK rear observation; no yellow-end clearance deadline or future guarantee'}
