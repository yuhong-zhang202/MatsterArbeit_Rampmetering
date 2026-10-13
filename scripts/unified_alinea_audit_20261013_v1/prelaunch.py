"""Read-only frozen-source/card check. Never prepares or launches a run."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def check():
    eng=ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering'
    bpath=eng/'ENGINEERING_DELIVERY_BINDING_V1.json';binding=json.loads(bpath.read_text());require(sha(bpath)=='fd09820b5d2c10f918a2fd6ebdd19d7d025102bcecfc573649e44a6fde0e39f8','ENGINEERING_BINDING_ID')
    checked={}
    def files(items):
        for p,h in items.items():
            require(isinstance(h,str) and len(h)==64,'HASH_SCHEMA');require(sha(ROOT/p)==h,'FROZEN_FILE_DRIFT:'+p);checked[p]=h
    files(binding['files']);s=json.loads((eng/'SOURCE_AND_INPUT_BINDING_V1.json').read_text())
    for key in ('sources','prepared_inputs','inherited_inputs','tests'):files(s[key])
    cardpath=ROOT/s['card_path'];require(sha(cardpath)==s['card_sha256']=='2c2330d4c977fb26c8ef52a36a16d56a7a6c94cb5334e8d5557f19eb967bed09','EXACT_CARD')
    c=json.loads(cardpath.read_text());require(c['status']=='PREPARED_NOT_RELEASED' and c['runtime_authorization_generated'] is False,'PREPARED_NOT_RELEASED')
    spec=c['spec'];require(spec['run_id']=='UA_FIXED300_S17_01' and spec['mode']=='fixed300' and spec['seed']==17 and spec['end_s']==1272 and spec['activation_s']==1200 and spec['step_s']==1 and spec['qMain']==3600 and spec['qRamp']==900 and spec['fixed_command_veh_h']==300,'FIRST_CARD_SCOPE')
    require(c['common_runtime_source_sha256']==s['common_runtime_source_sha256']=='900dcebb4f4568e6de93730977284c04f1573d02d19e6ac97ef38d79dc5702b9','COMMON_SOURCE')
    require(c['resources']=={'wall_limit_s':300,'startup_limit_s':60,'run_limit_bytes':300000000,'minimum_free_bytes':5000000000} and spec['total_resource_envelope']=={'monitored_s':1200,'raw_bytes':1200000000},'RESOURCE_SCOPE')
    require(not (ROOT/c['output']).exists(),'UNEXPECTED_NEW_RAW')
    require(s['new_native_starts']==0 and s['canonical_auth_release_created'] is False and s['zero_new_raw_allocated'] is True,'PRELAUNCH_RECORDED_STATE')
    for sub in ('authorization','releases'):
        require(not (eng/sub).exists() or not any((eng/sub).rglob('*.json')),'UNEXPECTED_CANONICAL_PERMISSION')
    return dict(status='PASS_FROZEN_PUBLIC_SOURCE_CARD_CHECK_ONLY',card_sha256=sha(cardpath),engineering_binding_sha256=sha(bpath),files_checked=checked,scope='PRELAUNCH_OFFLINE_NOT_NATIVE_OR_QUALIFICATION',new_raw_present=False,native_executed=False,environment_live_revalidated=False)
if __name__=='__main__':print(json.dumps(check(),indent=2))
