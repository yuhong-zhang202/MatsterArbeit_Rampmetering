"""Pure fake counting/equivalence and terminal paths; never native execution."""
import importlib.util,json,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
from unittest.mock import patch
from src.candidate_a_native_smoke_runtime_fix_20261012.profile import ROOT,TASK,RUN,OUTPUT,stage_package
from src.candidate_a_native_smoke_runtime_fix_20261012.frame_cache import FrameCache,CACHE_VEHICLE
from src.candidate_a_native_smoke_runtime_fix_20261012.bridge import _diagnostic_loop as optimized,execute
from src.candidate_a_native_smoke_selfloop_fix_20261011.bridge import _diagnostic_loop as original
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_native_smoke_20261011.adapter import inventory,StepAdapter,ROUTES

spec=importlib.util.spec_from_file_location('xml_fake_fixture',ROOT/'tests/candidate_a_native_smoke_selfloop_fix_20261011/test_selfloop.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)


class CountedWorld(fixture.XMLFakeConnection):
    def __init__(self,additional):
        super().__init__(additional);self.counts=Counter();self.mode=31;self.speed_shift=0
        values={'getTypeID':lambda vid:'technical_passenger','getRoute':lambda vid:ROUTES[vid.split('_')[0]],'getSpeedMode':lambda vid:self.mode,'getLaneChangeMode':lambda vid:1621,
          'getAccel':lambda vid:2.6,'getDecel':lambda vid:4.5,'getEmergencyDecel':lambda vid:9.0,'getTau':lambda vid:1.0,'getActionStepLength':lambda vid:1.0,'getImperfection':lambda vid:.5,'getMaxSpeed':lambda vid:55.55555555555556,
          'getSpeed':lambda vid:10+self.time*.001+self.speed_shift,'getLaneID':lambda vid:'main_up_0','getAcceleration':lambda vid:.001,
          'getLanePosition':lambda vid:100,'getLength':lambda vid:5,'getMinGap':lambda vid:2.5,'getIDList':lambda:('M_flow.0','M_flow.1'),'getLoadedIDList':lambda:('M_flow.0','M_flow.1','R_flow.0')}
        def counted(name,method):
            def call(*args,**kwargs):self.counts[name]+=1;return method(*args,**kwargs)
            return call
        self.vehicle=SimpleNamespace(**{name:counted(name,method) for name,method in values.items()})
        self.vehicle.setSpeed=lambda vid,value:setattr(self,'speed_shift',value)
        self.trafficlight.setProgram=lambda tls,v:self._setter('setProgram',v)
        self.trafficlight.setPhase=lambda tls,v:self._setter('setPhase',v)
    def _setter(self,method,value):super().request(self.trafficlight,[],self.time,method,value)
    def phase_request(self,tls,records,t,method,value):
        rec={'time_s':t,'method':method,'value':value,'call_completed':False};records.append(rec);getattr(tls,method)('ramp_mid',value);rec['call_completed']=True


def normalized(value):
    if isinstance(value,dict):return {k:normalized(v) for k,v in value.items() if k not in ('source','device','inode')}
    if isinstance(value,list):return [normalized(v) for v in value]
    return value


class RuntimeFixTests(unittest.TestCase):
    def world(self,tmp):
        pkg=Path(tmp)/'package';stage_package(ROOT,pkg,Path(tmp)/'not_raw');return CountedWorld(pkg/'scenario.add.xml')
    def test_same_frame_identity_checks_same_outputs_fewer_underlying_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw=self.world(tmp);view=FrameCache(raw);a=inventory(view);b=inventory(view)
            self.assertEqual(a,b);self.assertEqual(raw.counts['getIDList'],2);self.assertEqual(raw.counts['getLoadedIDList'],2)
            for field in ['getTypeID','getRoute','getSpeedMode','getLaneChangeMode','getAccel','getDecel','getEmergencyDecel','getTau','getActionStepLength','getImperfection','getMaxSpeed']:self.assertEqual(raw.counts[field],3)
            self.assertGreater(view.stats['hits'],0)
    def test_time_step_setter_and_unknown_call_invalidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw=self.world(tmp);view=FrameCache(raw);self.assertEqual(view.vehicle.getSpeed('M_flow.0'),10)
            view.vehicle.setSpeed('M_flow.0',2);self.assertEqual(view.vehicle.getSpeed('M_flow.0'),12)
            view.simulationStep(1);self.assertEqual(view.vehicle.getSpeed('M_flow.0'),12.001)
            raw.time=2;self.assertEqual(view.simulation.getTime(),2);self.assertEqual(view.vehicle.getSpeed('M_flow.0'),12.002)
            raw.vehicle.unknown_mutator=lambda:setattr(raw,'speed_shift',3)
            view.vehicle.unknown_mutator();self.assertEqual(view.vehicle.getSpeed('M_flow.0'),13.002)
            raw.vehicle.setSpeedMode=lambda vid,m:setattr(raw,'mode',m)
            view.vehicle.setSpeedMode('M_flow.0',0);self.assertEqual(view.vehicle.getSpeedMode('M_flow.0'),0)
    def test_mutable_values_ids_arguments_and_uncached_readers(self):
        raw=SimpleNamespace(simulation=SimpleNamespace(getTime=lambda:0),vehicle=SimpleNamespace());calls=Counter()
        def route(vid,extra=None):calls[(vid,extra)]+=1;return ['edge',vid,extra]
        raw.vehicle.getRoute=route;raw.vehicle.getIDList=lambda:[];raw.vehicle.getLeader=lambda vid:('leader',1)
        view=FrameCache(raw);r=view.vehicle.getRoute('A',extra=1);r.append('modified');self.assertEqual(view.vehicle.getRoute('A',extra=1),['edge','A',1]);view.vehicle.getRoute('B',extra=1);view.vehicle.getRoute('A',extra=2)
        self.assertEqual(dict(calls),{('A',1):1,('B',1):1,('A',2):1})
        before=view.stats['underlying_calls'];view.vehicle.getIDList();view.vehicle.getIDList();view.vehicle.getLeader('A');view.vehicle.getLeader('A');self.assertEqual(view.stats['underlying_calls']-before,4)
    def test_getter_missing_error_time_error_and_step_failure_failclosed(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw=self.world(tmp);view=FrameCache(raw);view.vehicle.getTypeID('M_flow.0')
            with self.assertRaises(AttributeError):view.vehicle.missingGetter()
            self.assertEqual(view.values,{})
            raw.vehicle.getSpeed=lambda vid:(_ for _ in ()).throw(ValueError('getter failure'))
            for _ in range(2):
                with self.assertRaisesRegex(ValueError,'getter failure'):view.vehicle.getSpeed('M_flow.0')
                self.assertEqual(view.values,{})
            raw.simulationStep=lambda end:(_ for _ in ()).throw(ValueError('stepfailure'))
            with self.assertRaisesRegex(ValueError,'stepfailure'):view.simulationStep(1)
            self.assertEqual(view.values,{})
            raw.simulation.getTime=lambda:float('nan')
            with self.assertRaisesRegex(ValueError,'unknown native frame time'):view.simulation.getTime()
    def test_typed_key_and_unknown_domain_cannot_expose_mutable_raw(self):
        counts=Counter()
        def getter(vid):counts[type(vid)]+=1;return type(vid).__name__
        raw=SimpleNamespace(simulation=SimpleNamespace(getTime=lambda:0),vehicle=SimpleNamespace(getTypeID=getter,unsupported_object=SimpleNamespace(set=lambda:None)),unknown_domain=SimpleNamespace(set=lambda:None))
        view=FrameCache(raw)
        self.assertEqual([view.vehicle.getTypeID(v) for v in [True,1,1.0,True,1,1.0]],['bool','int','float','bool','int','float'])
        self.assertEqual(sum(counts.values()),3)
        with self.assertRaisesRegex(ValueError,'noncallable connection'):view.unknown_domain
        self.assertEqual(view.values,{})
        view.vehicle.getTypeID('A')
        with self.assertRaisesRegex(ValueError,'noncallable domain'):view.vehicle.unsupported_object
        self.assertEqual(view.values,{})
    def test_complete_old_new_loop_same_checked_outputs_and_query_counts(self):
        results=[]
        for implementation in (original,optimized):
            with tempfile.TemporaryDirectory() as tmp:
                raw=self.world(tmp);out=Path(tmp)/'output';out.mkdir();capture=LogCapture(out);worker=SimpleNamespace(observe=raw.observe,request_phase=raw.phase_request);started=time.perf_counter()
                adapter=implementation(raw,worker,capture,out,{'wall_limit_s':180,'minimum_free_bytes':0,'run_limit_bytes':300000000},fixture.fixture.FakeProcess(),time.monotonic())
                elapsed=time.perf_counter()-started;rows=[normalized(json.loads(line)) for line in (out/'post_steps.jsonl').read_text().splitlines()]
                results.append({'rows':rows,'calls':dict(raw.counts),'elapsed_fake_s':elapsed,'cache_stats':getattr(adapter,'query_cache_stats',None),'last':adapter.last_completed});capture.close_handles()
        self.assertEqual(results[0]['rows'],results[1]['rows']);self.assertEqual(results[1]['last'],1207)
        self.assertLess(sum(results[1]['calls'].values()),sum(results[0]['calls'].values()))
        self.assertEqual(results[0]['calls']['getIDList'],results[1]['calls']['getIDList']);self.assertEqual(results[0]['calls']['getLoadedIDList'],results[1]['calls']['getLoadedIDList'])
        print('FAKE_QUERY_BENCH='+json.dumps({str(i):{k:v for k,v in r.items() if k!='rows'} for i,r in enumerate(results)},sort_keys=True))
    def test_coverage_mode_and_original_log_warning_still_stop(self):
        for case in ['duplicate_world','mode_zero','warning']:
            with self.subTest(case=case),tempfile.TemporaryDirectory() as tmp:
                raw=self.world(tmp);out=Path(tmp)/'output';out.mkdir();capture=LogCapture(out);worker=SimpleNamespace(observe=raw.observe,request_phase=raw.phase_request)
                if case=='duplicate_world':raw.vehicle.getIDList=lambda:('M_flow.0','M_flow.0')
                elif case=='mode_zero':raw.mode=0
                else:capture.paths['sumo_stderr.log'].write_bytes((ROOT/'artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/RUNTIME_NATIVE_WARNING_EXTRACT.txt').read_bytes())
                with self.assertRaises(ValueError):optimized(raw,worker,capture,out,{'wall_limit_s':180,'minimum_free_bytes':0,'run_limit_bytes':300000000},fixture.fixture.FakeProcess(),time.monotonic())
                self.assertEqual(raw.time,0);capture.close_handles()
    def test_new_auth_denied_before_spawn_no_raw(self):
        with patch('subprocess.Popen',side_effect=AssertionError('no native')):
            with self.assertRaisesRegex(ValueError,'SMOKE03 native execution authorization missing'):execute(ROOT/'fakecard',ROOT/'fakerelease')
        self.assertFalse((ROOT/OUTPUT).parent.exists());self.assertFalse((ROOT/TASK/'AUTHORIZATION_NATIVE_EXECUTION.json').exists())

if __name__=='__main__':unittest.main()
