"""Same-state direct-value memoization, not reduced observer/check coverage.

Requires one owned synchronous TraCI connection and no external mutators.
No time/ID/enumeration/TLS/leader/secure-gap result is cached.
"""
from copy import deepcopy
import math

CACHE_VEHICLE=frozenset(['getTypeID','getRoute','getSpeedMode','getLaneChangeMode',
    'getAccel','getDecel','getEmergencyDecel','getTau','getActionStepLength',
    'getImperfection','getMaxSpeed','getSpeed','getLaneID','getLanePosition',
    'getLength','getMinGap','getAcceleration'])
FRESH={
 'vehicle':frozenset(['getIDList','getLoadedIDList','getLeader','getSecureGap','getRouteIndex']),
 'simulation':frozenset(['getPendingVehicles','getArrivedIDList','getDepartedIDList','getCollidingVehiclesNumber','getStartingTeleportNumber','getEndingTeleportNumber']),
 'lane':frozenset(['getLength','getLastStepVehicleIDs']),
 'trafficlight':frozenset(['getControlledLinks','getProgram','getPhase','getRedYellowGreenState','getNextSwitch']),
 'vehicletype':frozenset(['getAccel','getDecel','getTau','getActionStepLength','getImperfection','getMaxSpeed','getEmergencyDecel']),
}


class DomainView:
    def __init__(self,owner,name,raw):self.owner=owner;self.name=name;self.raw=raw
    def __getattr__(self,name):
        try:method=getattr(self.raw,name)
        except Exception:self.owner.invalidate('MISSING_ATTRIBUTE');raise
        if not callable(method):self.owner.invalidate('UNKNOWN_ATTRIBUTE');return method
        def call(*args,**kwargs):
            if self.name=='simulation' and name=='getTime':return self.owner.read_time()
            cached=self.name=='vehicle' and name in CACHE_VEHICLE
            if not cached:
                if name not in FRESH.get(self.name,()):self.owner.invalidate('SETTER_OR_UNKNOWN_CALL')
                return self.owner.direct(method,*args,**kwargs)
            if self.owner.frame_time is None:self.owner.read_time()
            try:key=(self.name,name,args,tuple(sorted(kwargs.items())));hash(key)
            except Exception:
                self.owner.invalidate('UNHASHABLE_ARGUMENTS');return self.owner.direct(method,*args,**kwargs)
            if key in self.owner.values:
                self.owner.stats['hits']+=1
                return deepcopy(self.owner.values[key])
            value=self.owner.direct(method,*args,**kwargs)
            # Deepcopy failure never creates a reusable partially bound value.
            try:self.owner.values[key]=deepcopy(value)
            except Exception:self.owner.invalidate('COPY_FAILURE');raise
            self.owner.stats['misses']+=1
            return deepcopy(self.owner.values[key])
        return call


class FrameCache:
    def __init__(self,raw):
        self.raw=raw;self.frame_time=None;self.values={};self.domains={}
        self.stats={'hits':0,'misses':0,'underlying_calls':0,'invalidations':0,'verified_time_reads':0}
    def invalidate(self,reason):
        self.values.clear();self.frame_time=None;self.stats['invalidations']+=1
    def direct(self,method,*args,**kwargs):
        self.stats['underlying_calls']+=1
        try:return method(*args,**kwargs)
        except Exception:self.invalidate('NATIVE_CALL_FAILURE');raise
    def read_time(self):
        value=self.direct(self.raw.simulation.getTime)
        if type(value) not in (int,float) or not math.isfinite(value) or value<0:
            self.invalidate('UNKNOWN_TIME');raise ValueError('query cache unknown native frame time')
        if self.frame_time!=value:
            self.values.clear();self.frame_time=value
        self.stats['verified_time_reads']+=1
        return value
    def __getattr__(self,name):
        try:value=getattr(self.raw,name)
        except Exception:self.invalidate('MISSING_CONNECTION_ATTRIBUTE');raise
        if name in FRESH:
            if name not in self.domains:self.domains[name]=DomainView(self,name,value)
            return self.domains[name]
        if callable(value):
            def call(*args,**kwargs):
                self.invalidate('STEP_OR_UNKNOWN_CONNECTION_CALL')
                return self.direct(value,*args,**kwargs)
            return call
        self.invalidate('UNKNOWN_CONNECTION_ATTRIBUTE');return value
