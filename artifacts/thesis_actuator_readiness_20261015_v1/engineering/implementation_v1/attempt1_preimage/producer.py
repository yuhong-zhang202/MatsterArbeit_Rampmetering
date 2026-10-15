"""Real project Feedback and complete E1 events; no native launch on import."""
from scripts.formal_development_20261007_v1.control import Feedback, FeedbackParameters
from src.candidate_a_natural_service_20261015.policy import Command, require
from src.candidate_a_unified_alinea_20261013.event_ledger import DetectorEventLedger, DETECTORS
import math

PARAMETERS = FeedbackParameters(11, 70, 300, 900, 900)
SCHEDULE = {600:300, 1201:750, 1226:900, 1237:300}


class Producer:
    def __init__(self, mode='real_alinea', fixed_rate=900):
        require(mode in ('fixed300','fixed750','dynamic_commands','real_alinea'), 'UNKNOWN_APPROVED_MODE')
        self.mode=mode;self.fixed_rate=fixed_rate
        self.feedback = Feedback(PARAMETERS) if mode=='real_alinea' else None
        self.e1 = DetectorEventLedger(600) if self.feedback else None
        self.events=[];self.seeded=False

    def _query(self, conn, t):
        require(conn.simulation.getTime()==t, 'E1_SOURCE_TIME_MISMATCH')
        expected = {DETECTORS[0]: 'main_down_0', DETECTORS[1]: 'main_down_1'}
        require(set(DETECTORS) <= set(conn.inductionloop.getIDList()), 'E1_ID_UNKNOWN')
        out={}
        for detector in DETECTORS:
            require(conn.inductionloop.getLaneID(detector)==expected[detector] and
                    abs(conn.inductionloop.getPosition(detector)-20)<=1e-8, 'E1_GEOMETRY_UNKNOWN')
            out[detector]=[list(x) for x in conn.inductionloop.getVehicleData(detector)]
        require(conn.simulation.getTime()==t, 'E1_QUERY_CLOCK_DRIFT')
        return out

    def seed(self, conn):
        require(self.feedback and not self.seeded, 'E1_DUPLICATE_OR_UNREQUESTED_SEED')
        raw=self._query(conn,600);ongoing={};discarded={}
        for detector,items in raw.items():
            ongoing[detector]=[];discarded[detector]=[];seen=set()
            for x in items:
                require(len(x)==5, 'E1_SEED_TUPLE_UNKNOWN')
                vid,length,entry,leave,type_id=x
                require(isinstance(vid,str) and vid and isinstance(type_id,str) and type_id and
                    all(type(v) in (int,float) and math.isfinite(v) for v in (length,entry,leave)) and
                    length>0 and entry<=600 and (leave==-1 or entry<=leave<=600), 'E1_SEED_VALUES_UNKNOWN')
                key=(vid,entry);require(key not in seen,'E1_SEED_DUPLICATE');seen.add(key)
                if leave==-1:
                    require(vid in conn.vehicle.getIDList() and conn.vehicle.getTypeID(vid)==type_id,
                            'E1_SEED_ONGOING_ID_UNBOUND')
                    self.e1.events[detector][key]=tuple(x);ongoing[detector].append(x)
                else:discarded[detector].append(x)
        self.seeded=True
        self.events.append(dict(event='E1_ACTIVATION_SEED',global_s=600,logical_s=600,
            raw_events=raw, ongoing_events=ongoing, discarded_completed_before_window=discarded,
            detector_ids=list(DETECTORS), window_begin_global_s=600))

    def after_ack(self, conn, end):
        if not self.feedback or end<=600:return
        require(self.seeded, 'E1_SEED_MISSING')
        raw=self._query(conn,end)
        normalized=self.e1.add_step(end,raw)
        self.events.append(dict(event='E1_POST_ACK_EVENTS',global_s=end,
            logical_s=end, raw_events=raw, normalized_events=normalized))

    def command_at(self, conn, t):
        if t==600:
            if self.feedback:self.seed(conn)
            rate=900 if self.feedback else SCHEDULE[t] if self.mode=='dynamic_commands' else self.fixed_rate
            return Command(f'{self.mode}:600',t,rate,
                'PROJECT_FEEDBACK' if self.feedback else 'SCHEDULED' if self.mode=='dynamic_commands' else 'FIXED',
                rate if self.feedback else None)
        if self.mode=='dynamic_commands' and t in SCHEDULE:
            return Command(f'scheduled:{t}',t,SCHEDULE[t],'SCHEDULED')
        if self.feedback and t > 600 and (t)%30 == 0:
            begin=self.e1.begin_s;occ=self.e1.finish_window(t)
            result=self.feedback.update(t,begin,t,occ[0][0],occ[1][0])
            request_id=f'feedback:{t}'
            self.events.append(dict(event='PROJECT_FEEDBACK_DECISION',global_s=t,logical_s=t,
                global_window_begin_s=begin,global_window_end_s=t,
                detector_ids=list(DETECTORS),contributors=[x[1] for x in occ],
                request_id=request_id,**result))
            return Command(request_id,t,self.feedback.rate,'PROJECT_FEEDBACK',self.feedback.rate)
        return None
