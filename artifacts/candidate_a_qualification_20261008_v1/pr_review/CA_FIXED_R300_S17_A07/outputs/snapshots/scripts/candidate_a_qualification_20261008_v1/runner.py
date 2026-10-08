"""Issue4 one-use technical cards. Default preparation never starts SUMO."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/candidate_a_qualification_20261008_v1'
CONFIG=ROOT/'config/candidate_a_qualification_20261008_v1'
RAW=ROOT/'data/raw/candidate_a_qualification_20261008_v1'
PYTHON=ROOT/'.venv/bin/python'
SUMO=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo')
NETWORK=ROOT/'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml'
FEEDBACK=dict(target_pct=11.0,gain_veh_h_per_pct=70.0,minimum_veh_h=300.0,maximum_veh_h=900.0,initial_veh_h=900.0)
RESOURCES=dict(wall_limit_s=180,startup_limit_s=60,run_limit_bytes=300_000_000,new_raw_limit_bytes=4_000_000_000,minimum_free_bytes=5_000_000_000,poll_s=.2)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

def sources():
    paths=[]
    for folder in ('src/candidate_a_qualification_20261008','scripts/candidate_a_qualification_20261008_v1','tests/candidate_a_qualification_20261008'):
        paths.extend((ROOT/folder).glob('*.py'))
    paths.append(CONFIG/'PHASE_RATE_CONTRACT.json')
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}

def protection():
    j=json.loads((BASE/'PROTECTED_BASELINE.json').read_text())['protected_sha256']
    for p,h in j.items():
        if sha(ROOT/p)!=h:raise ValueError('protected baseline changed: '+p)
    return j

def tree_bytes(path):
    return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())

def prepare(rate,attempt=1,mode='FIXED',ramp=900):
    if mode=='FIXED' and (rate not in (300,450,600,750,900) or ramp!=900):raise ValueError('fixed card outside scope')
    if mode=='T1' and ramp not in (750,900):raise ValueError('integration card outside scope')
    if mode not in ('FIXED','T1') or attempt<1:raise ValueError('invalid card')
    protection()
    name=(f'CA_FIXED_R{rate}_S17' if mode=='FIXED' else f'CA_M3600_R{ramp}_S17_T1')+f'_A{attempt:02}'
    package=CONFIG/name;output=RAW/name/'outputs'
    if package.exists() or output.parent.exists():raise FileExistsError(name)
    package.mkdir(parents=True)
    old=ROOT/f'artifacts/stage6_boundary_search_20261002_v1/inputs/M3600_R{ramp}_S17'
    shutil.copyfile(old/'demand.rou.xml',package/'demand.rou.xml')
    for file in ('scenario.add.xml','scenario.sumocfg'):
        x=ET.parse(old/file)
        if file=='scenario.add.xml':
            for node in x.getroot().iter():
                for key in ('file','dest'):
                    if key in node.attrib:node.set(key,str(output/Path(node.get(key)).name))
            for period in range(8,25):
                tl=ET.SubElement(x.getroot(),'tlLogic',id='ramp_mid',type='static',programID=f'CA_C{period}',offset='0')
                for state,duration,nxt in (('G',3,1),('y',3,2),('r',period-6,2)):
                    ET.SubElement(tl,'phase',duration=str(duration),state=state,next=str(nxt))
        else:
            x.find('./input/route-files').set('value',str(package/'demand.rou.xml'))
            x.find('./input/additional-files').set('value',str(package/'scenario.add.xml'))
            for node in x.findall('./output/*')+x.findall('./report/*'):
                if node.get('value','').startswith('/'):node.set('value',str(output/Path(node.get('value')).name))
        ET.indent(x);x.write(package/file,encoding='utf-8',xml_declaration=True)
    card=dict(classification='ENGINEERING_QUALIFICATION_ONLY',status='PREPARED_NOT_RELEASED',base_commit='35651751a2e03d1906ff32a267a95077553c4404',run_id=name,
              mode=mode,fixed_command_veh_h=rate if mode=='FIXED' else None,qMain=3600,qRamp=ramp,seed=17,treatment='FIXED_RATE' if mode=='FIXED' else 'T1',
              horizon_s=4200,step_s=1,activation_s=1200 if mode=='FIXED' else 600,external_hold_begin_s=600 if mode=='FIXED' else None,
              external_hold_end_s=1200 if mode=='FIXED' else None,initial_hold_yellow_s=3 if mode=='FIXED' else 0,
              service_windows=[[t,t+300] for t in range(1200,3000,300)],tracking_tolerance=.10,feedback=FEEDBACK,
              package=str(package),output=str(output),resources=RESOURCES,sources_sha256=sources(),protected_baseline_sha256=protection(),
              inherited_input_sha256={str((old/f).relative_to(ROOT)):sha(old/f) for f in ('demand.rou.xml','scenario.add.xml','scenario.sumocfg')},
              runtime_input_sha256={str(p.relative_to(ROOT)):sha(p) for p in (NETWORK,SUMO) if p.is_relative_to(ROOT)},sumo_binary_sha256=sha(SUMO),
              prepared_input_sha256={str((package/f).relative_to(ROOT)):sha(package/f) for f in ('demand.rou.xml','scenario.add.xml','scenario.sumocfg')})
    write(package/'card.json',card)
    return package/'card.json'

def validate_card(card):
    if card.get('classification')!='ENGINEERING_QUALIFICATION_ONLY' or card.get('mode') not in ('FIXED','T1'):raise ValueError('invalid classification')
    if card.get('seed')!=17 or card.get('qMain')!=3600 or card.get('horizon_s')!=4200 or card.get('step_s')!=1 or card.get('feedback')!=FEEDBACK or card.get('resources')!=RESOURCES:raise ValueError('protected configuration changed')
    if card['mode']=='FIXED' and (card.get('fixed_command_veh_h') not in (300,450,600,750,900) or card.get('qRamp')!=900 or card.get('activation_s')!=1200 or card.get('external_hold_begin_s')!=600 or card.get('external_hold_end_s')!=1200 or card.get('initial_hold_yellow_s')!=3):raise ValueError('fixed card changed')
    if card['mode']=='T1' and (card.get('qRamp') not in (750,900) or card.get('activation_s')!=600 or card.get('external_hold_begin_s') is not None or card.get('external_hold_end_s') is not None or card.get('initial_hold_yellow_s')!=0):raise ValueError('integration must have natural input, no preload')
    if card.get('service_windows')!=[[t,t+300] for t in range(1200,3000,300)] or card.get('tracking_tolerance')!=.10:raise ValueError('qualification screen changed')
    if card.get('sources_sha256')!=sources() or card.get('protected_baseline_sha256')!=protection() or card.get('sumo_binary_sha256')!=sha(SUMO):raise ValueError('source/binary drift')
    for field in ('inherited_input_sha256','runtime_input_sha256','prepared_input_sha256'):
        for p,h in card[field].items():
            if sha(ROOT/p)!=h:raise ValueError('input drift: '+p)
    expected=RAW/card['run_id']/'outputs'
    if Path(card['output'])!=expected or Path(card['package'])!=CONFIG/card['run_id']:raise ValueError('unsafe card path')
    return True

def launch(card_path,release_path):
    card_path=Path(card_path);card=json.loads(card_path.read_text());validate_card(card)
    release=json.loads(Path(release_path).read_text())
    if release.get('disposition')!='PASS_FOR_TECHNICAL_EXECUTION' or release.get('card_sha256')!=sha(card_path) or release.get('run_id')!=card['run_id'] or not release.get('scientific_review_sha256'):raise ValueError('missing exact reviewed release')
    review=ROOT/release['scientific_review_path']
    if sha(review)!=release['scientific_review_sha256']:raise ValueError('review binding changed')
    if card['mode']=='T1':
        b=ROOT/release['phase_b_gate_path']
        if sha(b)!=release['phase_b_gate_sha256'] or json.loads(b.read_text()).get('disposition')!='QUALIFIED_300_900':raise ValueError('PhaseB range not qualified; integration STOP')
    for prior in RAW.glob('*/outputs/worker_receipt.json'):
        info=json.loads(prior.read_text())
        stem=card['run_id'].rsplit('_A',1)[0]
        if info.get('status','').startswith('COMPLETED') and info.get('run_id','').rsplit('_A',1)[0]==stem:
            raise ValueError('one effective run already completed for this technical configuration; no outcome-based retry')
    if release.get('replaces_run_id'):
        old=RAW/release['replaces_run_id']/'outputs/failure_snapshot.json'
        if not old.is_file() or sha(old)!=release.get('failure_snapshot_sha256') or not release.get('repair_evidence_path') or sha(ROOT/release['repair_evidence_path'])!=release.get('repair_evidence_sha256'):
            raise ValueError('technical retry lacks exact preserved failure and repair evidence')
    output=Path(card['output']);reserve=BASE/'engineering/reservations'/f"{card['run_id']}.json"
    if output.parent.exists() or reserve.exists():raise FileExistsError('attempt already consumed')
    if shutil.disk_usage(ROOT).free<RESOURCES['minimum_free_bytes'] or tree_bytes(RAW)>=RESOURCES['new_raw_limit_bytes']:raise ValueError('resource reserve insufficient')
    lock=BASE/'engineering/launch.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('x') as f:f.write(card['run_id'])
    start=time.monotonic();proc=None;reason='';exitcode=None
    try:
        output.mkdir(parents=True)
        snapshot=output/'snapshots'
        for p,h in {**card['sources_sha256'],**card['prepared_input_sha256'],**card['runtime_input_sha256']}.items():
            target=snapshot/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,target)
            if sha(target)!=h:raise ValueError('fresh run snapshot mismatch')
        write(snapshot/'card.json',card)
        write(reserve,dict(run_id=card['run_id'],card_sha256=sha(card_path),release_sha256=sha(release_path),utc=datetime.now(timezone.utc).isoformat()))
        with (output/'guardian_stdout.log').open('x') as out,(output/'guardian_stderr.log').open('x') as err:
            proc=subprocess.Popen([str(PYTHON),str(Path(__file__).with_name('worker.py')),'--card',str(card_path)],stdout=out,stderr=err,start_new_session=True)
            while proc.poll() is None:
                elapsed=time.monotonic()-start
                if elapsed>RESOURCES['wall_limit_s']:reason='WALL_LIMIT'
                if tree_bytes(output)>RESOURCES['run_limit_bytes']:reason='RUN_BYTES_LIMIT'
                if tree_bytes(RAW)>RESOURCES['new_raw_limit_bytes']:reason='TOTAL_RAW_LIMIT'
                if shutil.disk_usage(ROOT).free<RESOURCES['minimum_free_bytes']:reason='DISK_RESERVE'
                if reason:
                    os.killpg(proc.pid,signal.SIGTERM);break
                time.sleep(RESOURCES['poll_s'])
            try:exitcode=proc.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);exitcode=proc.wait()
    finally:
        receipt=dict(run_id=card['run_id'],card_sha256=sha(card_path),release_sha256=sha(release_path),worker_started=proc is not None,worker_exit_code=exitcode,guardian_reason=reason,elapsed_s=time.monotonic()-start,payload_bytes=tree_bytes(output),output=str(output),files_sha256={str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()})
        write(output.parent/'guardian_receipt.json',receipt)
        with (BASE/'engineering/EXECUTION_LEDGER.jsonl').open('a') as f:f.write(json.dumps(receipt)+'\n')
        lock.unlink()
    print(json.dumps(receipt,indent=2))
    return exitcode

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--prepare',type=int,choices=(300,450,600,750,900));a.add_argument('--attempt',type=int,default=1);a.add_argument('--check-card');a.add_argument('--launch');a.add_argument('--release');args=a.parse_args()
    if args.prepare:print(prepare(args.prepare,args.attempt))
    elif args.check_card:validate_card(json.loads(Path(args.check_card).read_text()));print('OFFLINE_CARD_PASS')
    elif args.launch:
        if not args.release:a.error('--launch requires an exact --release')
        sys.exit(launch(args.launch,args.release))
    else:a.print_help()
