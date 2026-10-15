"""Single-use native diagnostic bridge. No launch or connection at import.

Current task has no native release. execute() always checks canonical future
human authorization/release before output allocation or native import/spawn.
"""
from pathlib import Path
from dataclasses import asdict
import json
import os
import shutil
import socket
import sys
import time

from src.candidate_a_native_receiver_wait_20261012.adapter import StepAdapter, inventory, TLS, STORAGE, INGRESS, INTERNAL
from src.candidate_a_native_wait_budget_series_20261012.profile import ROOT,TASK,NETWORK,SUMO,sha,write_new,validate_release,require
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_native_smoke_20261011.bridge_resources import ResourceWatchdog
from src.candidate_a_native_smoke_runtime_fix_20261012.frame_cache import FrameCache


def protected_worker():
    sys.path.insert(0,str(ROOT/'scripts/candidate_a_qualification_20261008_v1'))
    import worker
    require(Path(worker.__file__).resolve()==ROOT/'scripts/candidate_a_qualification_20261008_v1/worker.py','wrong protected observer module')
    return worker


def encoded(value):
    if isinstance(value,set):return sorted(value)
    if isinstance(value,Path):return str(value)
    raise TypeError(type(value).__name__)


def append_new(path, value):
    with path.open('a') as f:
        f.write(json.dumps(value,default=encoded,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())


def admission(conn, time_s, observe):
    """Before control requests, rather than after a green is already selected."""
    require(conn.simulation.getTime()==time_s,'admission source time')
    require(conn.trafficlight.getControlledLinks(TLS)==((('ramp_storage_0','ramp_accel_0',INTERNAL),),),'admission link drift')
    inventory(conn)
    vehicles,ids,internal,receiver=observe(conn)
    for lane,length in [(STORAGE,204.49),(INGRESS,113.08),(INTERNAL,81.98)]:
        require(abs(conn.lane.getLength(lane)-length)<=1e-8,'admission geometry drift')
    require(type(receiver.get('available')) is bool and receiver['available'],'receiver denies green')
    require(time_s in (1200,1224,1248), 'admission outside declared cycle boundaries')
    program = 'CA_C8' if time_s == 1200 else 'CA_C24'
    require(conn.trafficlight.getProgram(TLS)==program and conn.trafficlight.getRedYellowGreenState(TLS)=='r' and conn.trafficlight.getPhase(TLS)==2,'not native cycle-red boundary')
    switch=conn.trafficlight.getNextSwitch(TLS)
    require(switch>=time_s if time_s==1200 else switch==time_s,'native cycle switch mismatch')
    # Reuse full adapter observation validation on a read-only red view before
    # any setters. A new adapter would otherwise expect G at activation1200.
    # Validate all current lane membership here; do not relax its post-selection checks.
    world,_,_=inventory(conn)
    require({v.vehicle_id for v in vehicles}==set(ids[STORAGE])|set(ids[INGRESS]),'admission local coverage')
    for v in vehicles:
        v.validate();require(v.vehicle_id in world and world[v.vehicle_id]['role']=='R' and abs(world[v.vehicle_id]['speed_m_s']-v.speed_m_s)<=1e-8,'admission vehicle binding')
    for lane,covered in [(STORAGE,set(ids[STORAGE])),(INGRESS,set(ids[INGRESS])),(INTERNAL,set(internal))]:
        require(covered==set(conn.lane.getLastStepVehicleIDs(lane))=={v for v,w in world.items() if w['lane_id']==lane},'admission lane binding')
    return {'time_s':time_s,'receiver':receiver,'vehicle_states':[asdict(v) for v in vehicles],'native_red_boundary':True}


def checkpoint(conn, adapter, capture, output, start_time):
    """Durable in-run gate. Full native log binding still requires final EOF."""
    require(adapter.checkpoint_pending and not adapter.checkpoint_verified, 'checkpoint identity')
    require(conn.simulation.getTime()==1207 and adapter.last_completed==adapter.last_end==1207 and adapter.pending is None, 'checkpoint accounting/time unknown')
    row=adapter.receipts[-1]
    require(row['time_begin_s']==1206 and row['motion']=='r' and row['accounting_complete'] and row['status']=='MANDATORY_FIRST_RED_CHECKPOINT_PENDING', 'checkpoint motion/reconciliation unknown')
    require(conn.trafficlight.getProgram(TLS)=='CA_C24' and conn.trafficlight.getPhase(TLS)==2 and conn.trafficlight.getRedYellowGreenState(TLS)=='r' and conn.trafficlight.getNextSwitch(TLS)==1224, 'checkpoint native signal mismatch')
    require(conn.trafficlight.getControlledLinks(TLS)==((('ramp_storage_0','ramp_accel_0',INTERNAL),),), 'checkpoint link mismatch')
    captured=capture.snapshot(1207,1207,'FIRST_RED_CHECKPOINT_PROVISIONAL_UNTIL_EOF')
    require(not captured['streams']['sumo_stderr.log']['text'], 'checkpoint stderr message')
    append_new(output/'log_intervals.jsonl',captured)
    receipt={'time_s':1207, 'last_accounted_s':adapter.last_end, 'status':'CHECKPOINT_PASSED_CONTINUE_SAME_AUTHORIZED_RUN',
        'accounting':adapter.ledger.accounting(), 'log_capture':captured, 'log_scope':'PROVISIONAL_NATIVE_CAPTURE_FINAL_EOF_REQUIRED',
        'elapsed_monitored_wall_s':time.monotonic()-start_time, 'native_safety_proven':False, 'rate_qualified':False}
    with (output/'first_red_checkpoint.json').open('x') as f:
        f.write(json.dumps(receipt,default=encoded,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
    adapter.checkpoint_verified=True;adapter.checkpoint_pending=False
    return receipt


def _diagnostic_loop(conn, worker, capture, output, resources, process, start_time, adapter=None):
    """Private post-release loop; fake tests inject here, not a public launch API."""
    adapter=adapter or StepAdapter(worker.observe)
    conn=FrameCache(conn)
    adapter.query_cache_stats=conn.stats
    phase_requests=[]
    worker.request_phase(conn.trafficlight,phase_requests,0,'setProgram','A_OPEN')
    worker.request_phase(conn.trafficlight,phase_requests,0,'setPhase',0)
    for t in range(1272):
        require(time.monotonic()-start_time<=resources['wall_limit_s'],'wall resource STOP')
        require(shutil.disk_usage(output).free>=resources['minimum_free_bytes'],'disk reserve STOP')
        require(sum(p.stat().st_size for p in output.rglob('*') if p.is_file())<=resources['run_limit_bytes'],'output bytes STOP')
        require(process.poll() is None,'native child exited before observed step')
        if t==600:
            worker.request_phase(conn.trafficlight,phase_requests,t,'setProgram','CA_C8')
            worker.request_phase(conn.trafficlight,phase_requests,t,'setPhase',1)
        if t==1200:
            bound=admission(conn,t,worker.observe);append_new(output/'admission.jsonl',bound)
            worker.request_phase(conn.trafficlight,phase_requests,t,'setProgram','CA_C24')
            # setProgram retains a phase index; select G only after the bound red
            # observation. No direct red and no transient setPhase(2) is needed.
            worker.request_phase(conn.trafficlight,phase_requests,t,'setPhase',0)
        if t in (1224,1248):
            bound=admission(conn,t,worker.observe);append_new(output/'admission.jsonl',bound)
        before=adapter.prepare_step(conn,t)
        append_new(output/'pre_steps.jsonl',{'time_s':t,'bound_snapshot':adapter.pending,'preparation':before,'phase_requests':phase_requests})
        # All log cursors began at byte0 including startup/control queries. Check
        # existing stderr before motion, then consume the afterACK interval.
        pre=capture.snapshot(t,t,'PRE_MOTION_AFTER_CONTROL_AND_OBSERVATION')
        append_new(output/'log_intervals.jsonl',pre)
        require(not pre['streams']['sumo_stderr.log']['text'],'native stderr before motion')
        conn.simulationStep(t+1)
        adapter.bridge_last_ack={'requested_target_s':t+1,'ACK_received':True,'actual_readback_s':None,'actual_time_verified':False}
        append_new(output/'step_ack.jsonl',adapter.bridge_last_ack)
        actual=conn.simulation.getTime()
        adapter.bridge_last_ack['actual_readback_s']=actual
        require(type(actual) in (int,float) and actual==t+1,'ACK actual simulation time mismatch')
        adapter.bridge_last_ack['actual_time_verified']=True
        adapter.last_completed=actual
        append_new(output/'step_ack.jsonl',adapter.bridge_last_ack)
        after=capture.snapshot(t,t+1,'AFTER_SIMULATION_STEP_ACK')
        append_new(output/'log_intervals.jsonl',after)
        try:row=adapter.reconcile_step(conn,capture.adapter_warning(after))
        except Exception:
            append_new(output/'post_steps.jsonl',{'time_s':t,'retained_receipts':[r for r in adapter.receipts if r.get('time_begin_s')==t] ,'pending':adapter.pending,'last_completed_s':adapter.last_completed,'last_accounted_s':adapter.last_end})
            raise
        append_new(output/'post_steps.jsonl',row)
        if adapter.checkpoint_pending:
            checkpoint(conn, adapter, capture, output, start_time)
        if adapter.paused:
            require(t==1271,'unexpected diagnostic pause')
            require(conn.trafficlight.getPhase(TLS)==2 and conn.trafficlight.getRedYellowGreenState(TLS)=='r' and conn.trafficlight.getNextSwitch(TLS)==1272,'final native cycle boundary drift')
            adapter.loop_terminal_elapsed_s=time.monotonic()-start_time
            return adapter
        phase_requests=[]
    raise ValueError('mandatory three-cycle stop missing')


def execute(card_path, release_path, root=ROOT):
    root=Path(root).resolve()
    require(root==ROOT,'execute root injection prohibited')
    card=validate_release(card_path,release_path,root)
    run=card['spec']['run_id']
    output=root/card['output'];parent=output.parent
    require(not parent.exists(),'run identity/output already consumed')
    require(shutil.disk_usage(root).free>=card['resources']['minimum_free_bytes'],'insufficient fresh disk reserve')
    parent.mkdir(parents=True,exist_ok=False);output.mkdir()
    write_new(parent/'ONE_USE_RESERVATION.json',{'run_id':run,'card_sha256':sha(card_path),'release_sha256':sha(release_path),'status':'CONSUMED_NO_RETRY'})
    # Review source/input snapshots before any child can alter output.
    snaps=output/'snapshots';snaps.mkdir()
    for p,h in {**card['sources_sha256'],**card['prepared_input_sha256'],**card['inherited_inputs_sha256'],str(NETWORK):card['network_sha256']}.items():
        target=snaps/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/p,target);require(sha(target)==h,'fresh snapshot drift')
    shutil.copyfile(card_path,output/'card.json');shutil.copyfile(release_path,output/'release.json')
    process=None;conn=None;capture=None;adapter=None;watchdog=None;normal_closed=False;status='ABORTED_UNKNOWN';error='';final_logs=None
    started=time.monotonic()
    try:
        capture=LogCapture(output)
        worker=protected_worker()
        import traci  # Authorized entry only; does not itself spawn.
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        env=worker.sumo_launch_environment()
        command=[str(SUMO),'-c',str(root/card['package']/'scenario.sumocfg'),'--remote-port',str(port)]
        write_new(output/'startup_context.json',{'command':command,'SUMO_HOME':env['SUMO_HOME'],'native_warning_suppression':False,'aggregate_warnings':-1,'source_compiler_equivalence':'NOT_VERIFIED'})
        process=worker.launch_sumo_process(command,capture.handles['sumo_stdout.log'],capture.handles['sumo_stderr.log'],env)
        watchdog=ResourceWatchdog(process,output,card['resources'],started);watchdog.start()
        conn=worker.connect_traci(traci,port,process,worker.startup_trace_callback(output/'startup_trace.jsonl'),deadline_s=card['resources']['startup_limit_s'])
        startup=capture.snapshot(0,0,'STARTUP_CONNECT_ACK');append_new(output/'log_intervals.jsonl',startup)
        require(not startup['streams']['sumo_stderr.log']['text'],'startup stderr nonempty')
        adapter=StepAdapter(worker.observe)
        _diagnostic_loop(conn,worker,capture,output,card['resources'],process,started,adapter)
        status='THREE_CYCLES_PENDING_LOG_FINALIZATION'
    except Exception as exc:
        error=type(exc).__name__+':'+str(exc)
        write_new(output/'failure_snapshot.json',json.loads(json.dumps({'error':error,'last_completed_s':adapter.last_completed if adapter else None,
            'last_step_ack':getattr(adapter,'bridge_last_ack',None),
            'same_state_query_cache':getattr(adapter,'query_cache_stats',None),
            'last_accounted_s':adapter.last_end if adapter else None,'pending':adapter.pending if adapter else None,
            'accounting':adapter.ledger.accounting() if adapter else None,
            'retained_last_observation':adapter.receipts[-1:] if adapter else [],
            'original_logs_preserved':True},default=encoded)))
    finally:
        if conn is not None:
            try:conn.close();normal_closed=True
            except Exception as exc:error+=';close:'+type(exc).__name__+':'+str(exc)
        if process is not None:
            try:process.wait(timeout=5)
            except Exception as exc:
                normal_closed=False;error+=';wait:'+type(exc).__name__+':'+str(exc)
                try:process.terminate();process.wait(timeout=5)
                except Exception as kill_error:
                    error+=';terminate:'+str(kill_error)
                    try:process.kill();process.wait(timeout=5)
                    except Exception as final_kill_error:error+=';kill:'+str(final_kill_error)
            if process.returncode!=0:normal_closed=False
        if watchdog is not None:
            watchdog.close()
            if watchdog.reason or watchdog.error:
                normal_closed=False;error+=';watchdog:'+str(watchdog.reason)+':'+str(watchdog.error)
        if capture is not None:
            try:
                require(process is not None,'native process not started')
                final_logs=capture.finalize(process,adapter.last_completed if adapter else None,normal_closed)
                append_new(output/'log_intervals.jsonl',capture.records[-1])
                if final_logs['status']!='BOUND_NO_OBSERVED_NATIVE_MESSAGE':status='STOP_UNKNOWN_LOG_COVERAGE_OR_NATIVE_MESSAGE'
            except Exception as exc:
                status='STOP_UNKNOWN_LOG_FINALIZATION';error+=';logfinal:'+type(exc).__name__+':'+str(exc)
            capture.close_handles()
        if status=='THREE_CYCLES_PENDING_LOG_FINALIZATION':status='THREE_CYCLES_OBSERVED_NO_MONITORED_ANOMALY_NOT_QUALIFIED'
        write_new(output/'bridge_receipt.json',{'run_id':run,'card_sha256':sha(card_path),'status':status,'error':error,
            'native_started':process is not None,'last_completed_s':adapter.last_completed if adapter else None,
            'last_step_ack':getattr(adapter,'bridge_last_ack',None),
            'same_state_query_cache':getattr(adapter,'query_cache_stats',None),
            'last_accounted_s':adapter.last_end if adapter else None,'final_logs':final_logs,
            'resource_watchdog':{'reason':watchdog.reason,'error':watchdog.error,'poll_s':.2} if watchdog else None,
            'actual_native_safety_proven':False,'rate_qualified':False,'automatic_continuation':False,
            'first_red_checkpoint_verified':getattr(adapter,'checkpoint_verified',False),
            'cycles':adapter.ledger.rows if adapter else None,
            'control_accounting':adapter.ledger.accounting() if adapter and adapter.last_end is not None and adapter.last_end>1200 else None,
            'loop_terminal_elapsed_s':getattr(adapter,'loop_terminal_elapsed_s',None),
            'monitored_elapsed_through_cleanup_s':time.monotonic()-started,
            'files_sha256':{str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()}})
    return 0 if status=='THREE_CYCLES_OBSERVED_NO_MONITORED_ANOMALY_NOT_QUALIFIED' else 1
