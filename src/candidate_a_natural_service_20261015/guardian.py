"""Bound one dedicated Python worker session through owned-child cleanup."""
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import time
from src.candidate_a_natural_service_20261015.profile import ROOT,TASK,RAW,RUN,sha,require

CONTEXT_ENV='NATURAL_QUALIFICATION_GUARDIAN_CONTEXT'
TOKEN_ENV='NATURAL_QUALIFICATION_GUARDIAN_TOKEN'


def write_new(path,value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())


def identity(pid):
    result={'pid':pid,'pgid':None,'sid':None,'status':'UNKNOWN'}
    try:result.update(pgid=os.getpgid(pid),sid=os.getsid(pid),status='OBSERVED')
    except OSError as exc:result['error']=type(exc).__name__+':'+str(exc)
    return result


def require_worker_context(card,release,root=ROOT):
    path=os.environ.get(CONTEXT_ENV);token=os.environ.get(TOKEN_ENV)
    require(path and token,'OUTER_GUARDIAN_CONTEXT_REQUIRED')
    c=json.loads(Path(path).read_text())
    require(Path(path).resolve()==Path(root)/TASK/'runs'/RUN/'guardian_context.json','FOREIGN_GUARDIAN_CONTEXT')
    require(c['token_sha256']==__import__('hashlib').sha256(token.encode()).hexdigest(),'GUARDIAN_TOKEN_MISMATCH')
    require(c['run_id']==RUN and c['card_sha256']==sha(card) and c['release_sha256']==sha(release),'GUARDIAN_BINDING_MISMATCH')
    require(c['guardian_pid']==os.getppid(),'GUARDIAN_PARENT_MISMATCH')
    me=identity(os.getpid())
    require(me['status']=='OBSERVED' and me['pid']==me['pgid']==me['sid'],'DEDICATED_WORKER_SESSION_REQUIRED')
    return c


def record_native_identity(process,output,run,card,release,root=ROOT):
    """Called immediately after direct Popen, before connection or control."""
    c=require_worker_context(card,release,root)
    before=process.poll();worker=identity(os.getpid());native=identity(process.pid);after=process.poll()
    row=dict(schema='NATURAL_OWNED_PROCESS_IDENTITY_V1',run_id=run,
        card_sha256=sha(card),release_sha256=sha(release),guardian_pid=c['guardian_pid'],
        worker=worker,native=native,child_returncode_before=before,child_returncode_after=after,
        observed_monotonic_s=time.monotonic(),ownership_verified=False)
    row['ownership_verified']=(before is None and after is None and worker['status']=='OBSERVED' and native['status']=='OBSERVED'
        and worker['pid']==worker['pgid']==worker['sid']==native['pgid']==native['sid'])
    write_new(Path(output)/'owned_process_identity.json',row)
    require(row['ownership_verified'],'NATIVE_OWNED_GROUP_UNKNOWN_OR_MISMATCH')
    return row


def group_members(pgid):
    """Only inspect IDs in the dedicated group, never select by process name."""
    lines=subprocess.run(['ps','-ax','-o','pid=','-o','pgid=','-o','stat='],capture_output=True,text=True,timeout=2,check=True).stdout.splitlines()
    result=[]
    for line in lines:
        fields=line.split()
        if len(fields)!=3 or int(fields[1])!=pgid:continue
        pid=int(fields[0]);row=identity(pid);row['zombie']=fields[2].startswith('Z')
        if row['status']=='UNKNOWN':continue  # exited during inventory
        require(row['sid']==pgid,'OWNED_GROUP_SESSION_CHANGED')
        result.append(row)
    return result


def supervise(command,env,cwd,*,inner_s,cleanup_s,identity_path,run,card_sha,release_sha,stdout,stderr):
    """Ordinary subprocess supervisor; no traffic library is imported here."""
    started=time.monotonic();process=None;verified=False;reason='UNKNOWN';cleanup_error=None;native_verified=False
    worker=None;remaining=None
    try:
        process=subprocess.Popen(command,env=env,cwd=cwd,stdout=stdout,stderr=stderr,start_new_session=True)
        worker=identity(process.pid)
        require(worker['status']=='OBSERVED' and worker['pid']==worker['pgid']==worker['sid'],'WORKER_SESSION_UNKNOWN')
        verified=True
        while process.poll() is None:
            if time.monotonic()-started>=inner_s:reason='INNER_WALL_DEADLINE';break
            time.sleep(min(.05,max(.001,inner_s-(time.monotonic()-started))))
        else:reason='WORKER_EXITED'
        if Path(identity_path).is_file():
            row=json.loads(Path(identity_path).read_text())
            native_verified=(row['run_id']==run and row['card_sha256']==card_sha and row['release_sha256']==release_sha
                and row['ownership_verified'] is True and row['worker']==worker
                and row['native']['pgid']==process.pid and row['native']['sid']==process.pid)
        members=group_members(process.pid)
        if any(not x['zombie'] for x in members) and reason=='WORKER_EXITED':reason='WORKER_EXITED_WITH_LIVE_OWNED_MEMBERS'
    except Exception as exc:
        reason='GUARDIAN_UNKNOWN:'+type(exc).__name__+':'+str(exc)
    finally:
        if process is not None and verified:
            try:
                members=group_members(process.pid)
                if any(not x['zombie'] for x in members):
                    os.killpg(process.pid,signal.SIGTERM)
                    terminate_end=min(started+inner_s+cleanup_s,time.monotonic()+max(.05,cleanup_s/2))
                    while time.monotonic()<terminate_end:
                        process.poll()
                        if not any(not x['zombie'] for x in group_members(process.pid)):break
                        time.sleep(.02)
                    if any(not x['zombie'] for x in group_members(process.pid)):os.killpg(process.pid,signal.SIGKILL)
                try:process.wait(timeout=max(.01,min(2,started+inner_s+cleanup_s-time.monotonic())))
                except subprocess.TimeoutExpired:pass
                remaining=group_members(process.pid)
            except Exception as exc:
                cleanup_error=type(exc).__name__+':'+str(exc)
                # Inventory itself may be denied. A still-live direct Popen
                # anchors the verified session; stop it without claiming EOF.
                if process.poll() is None and identity(process.pid)==worker:
                    try:
                        os.killpg(process.pid,signal.SIGKILL)
                        process.wait(timeout=max(.01,min(2,cleanup_s)))
                    except Exception as stop_error:cleanup_error+=';direct_owned_group:'+str(stop_error)
        elif process is not None:
            # Direct Popen ownership remains valid even if group verification failed.
            try:process.terminate();process.wait(timeout=min(1,cleanup_s))
            except Exception:
                try:process.kill();process.wait(timeout=min(1,cleanup_s))
                except Exception as exc:cleanup_error=str(exc)
    elapsed=time.monotonic()-started
    no_live=(not any(not x['zombie'] for x in remaining)) if remaining is not None else None
    return dict(schema='NATURAL_QUALIFICATION_GUARDIAN_V1',run_id=run,card_sha256=card_sha,release_sha256=release_sha,
        worker=worker,worker_returncode=process.poll() if process else None,stop_reason=reason,
        native_identity_path=str(identity_path),native_identity_verified=native_verified,
        inner_wall_limit_s=inner_s,cleanup_reserve_s=cleanup_s,outer_wall_limit_s=inner_s+cleanup_s,
        monitored_elapsed_through_cleanup_s=elapsed,overshoot_s=max(0,elapsed-inner_s-cleanup_s),
        group_cleanup=dict(ownership_verified=verified,no_live_owned_members=no_live,
            status='OBSERVED_NO_LIVE_OWNED_MEMBERS' if no_live else 'UNKNOWN_OR_LIVE_OWNED_MEMBERS',error=cleanup_error))


def execute_guarded(card,release,root=ROOT):
    from src.candidate_a_natural_service_20261015 import profile,budget
    root=Path(root).resolve();require(root==ROOT,'GUARDIAN_ROOT_INJECTION_PROHIBITED')
    c=profile.validate_release(card,release,root,guardian_preflight=True)
    bound=budget.accounting(root);limits=budget.effective_limits(c['resources'],bound)
    require(__import__('shutil').disk_usage(root).free>=c['resources']['minimum_free_bytes'],'INSUFFICIENT_FREE_DISK')
    folder=root/TASK/'runs'/RUN;folder.mkdir(parents=True,exist_ok=False)
    token=secrets.token_hex(32);context=folder/'guardian_context.json'
    write_new(context,dict(run_id=RUN,guardian_pid=os.getpid(),card_sha256=sha(card),release_sha256=sha(release),
        card_path=str(Path(card).resolve()),release_path=str(Path(release).resolve()),
        token_sha256=__import__('hashlib').sha256(token.encode()).hexdigest()))
    env={**os.environ,CONTEXT_ENV:str(context),TOKEN_ENV:token}
    with (folder/'worker_stdout.log').open('xb') as out,(folder/'worker_stderr.log').open('xb') as err:
        receipt=supervise([sys.executable,'-m','scripts.candidate_a_natural_service_20261015_v1.cli','worker','--card',str(Path(card).resolve()),'--release',str(Path(release).resolve())],env,root,
            inner_s=limits['wall_limit_s'],cleanup_s=limits['cleanup_reserve_s'],identity_path=root/c['output']/'owned_process_identity.json',run=RUN,card_sha=sha(card),release_sha=sha(release),stdout=out,stderr=err)
    receipt['total_budget_before_worker']=bound
    destination=root/RAW/RUN/'guardian_receipt.json' if (root/RAW/RUN).is_dir() else folder/'guardian_receipt.json'
    write_new(destination,receipt)
    return 0 if receipt['worker_returncode']==0 and receipt['stop_reason']=='WORKER_EXITED' and receipt['native_identity_verified'] and receipt['group_cleanup']['no_live_owned_members'] is True else 1
