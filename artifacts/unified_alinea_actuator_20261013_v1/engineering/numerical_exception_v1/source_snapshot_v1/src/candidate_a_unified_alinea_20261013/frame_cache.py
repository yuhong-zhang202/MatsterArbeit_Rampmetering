"""Add only fresh, read-only E1 getters to the unchanged inherited cache."""
from src.candidate_a_native_smoke_runtime_fix_20261012.frame_cache import FrameCache as ProtectedFrameCache


class FreshE1:
    def __init__(self, owner, raw):self.owner=owner;self.raw=raw
    def __getattr__(self, name):
        if name not in {'getIDList','getLaneID','getPosition','getVehicleData'}:
            self.owner.invalidate('UNSUPPORTED_E1_CALL')
            raise ValueError('unsupported E1 getter or mutator')
        method=getattr(self.raw,name)
        if not callable(method):raise ValueError('noncallable E1 getter')
        return lambda *args,**kwargs:self.owner.direct(method,*args,**kwargs)


class FrameCache(ProtectedFrameCache):
    def __getattr__(self, name):
        if name=='inductionloop':
            return FreshE1(self,self._raw.inductionloop)
        return super().__getattr__(name)
