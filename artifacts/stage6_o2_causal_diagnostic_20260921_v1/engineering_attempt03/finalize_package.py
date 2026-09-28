#!/usr/bin/env python3
"""Finalize static immutable package; does not spawn simulations."""
import hashlib,json,sys
from pathlib import Path
B=Path(__file__).absolute().parent;R=B.parents[2]
H=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo');OLD=R/'artifacts/stage6_targeted_validation_20260920_v1/engineering'
RUN=R/'data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt3'
def bind(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
py=Path(sys.executable).resolve();sumo=H.parent.parent/'bin/sumo' # overwritten explicitly below
sumo=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo')
net=OLD/'build_attempts/TV_BUILD01/network.net.xml'
static=json.loads((B/'static_validation_receipt.json').read_text());sources=json.loads((B/'references/source_bindings.json').read_text())['sources']
# Bind installed Python client dependency files as well as specific interface sources.
deps=[p for directory in [H/'tools/traci',H/'tools/sumolib'] for p in directory.rglob('*.py') if p.is_file()]
inputs=[bind(p) for p in sorted((B/'inputs').iterdir())]
write(B/'input_manifest.json',{'status':'STATIC_BOUND_NOT_RUN','attempt_id':'O2_C_S17_450_attempt3','run_root':str(RUN),'output_root':str(RUN/'outputs'),'inputs':inputs,'network':bind(net),'original_counts':{'M':1333,'R':300,'U':150,'X':75},'counts_scope':'original0-1500 schedule; cannot call all scheduled-by450','begin':0,'end':450,'step':1,'seed':17,'program':'C_STRONG','geometry_and_behavior_change':False})
limits={'SUMO_starts':1,'TraCI_connections':1,'netconvert':0,'GUI':0,'retry':0,'per_attempt_monitored_s':180,'total_monitored_s':208.54239662599866,'per_attempt_observed_bytes':200000000,'total_observed_bytes':200118166}
files=[p for p in B.rglob('*') if p.is_file() and '/tests/fixtures_' not in str(p)]
rows=[bind(p) for p in files]+sources+static['schema_bindings']+[bind(p) for p in deps]+[bind(py),bind(sumo),bind(net),bind(Path('/usr/sbin/lsof'))]
prior=json.loads((B/'prior_attempt_accounting.json').read_text())
rows += prior['previous_raw_files']+[prior['previous_card'],bind(Path('/usr/bin/sample')),bind(Path('/bin/ps'))]
rows += prior['other_previous_cards']+[prior['non_SUMO_invocation_notes'],bind(B.parent/'O2_C_S17_450_attempt2_technical_failure.md')]
bindings=list({r['path']:r for r in rows}.values())
card={'kind':'O2_SINGLE_START_DIAGNOSTIC','approved':False,'status':'STATIC_PACKAGE_PENDING_EXACT_REVIEW_NO_LAUNCH','purpose':'technical instrumentation of C U35/R70 event, not science replication','limits':limits,'budget_semantics':'180s and200MB observed stop-lines,50ms polling, possible overshoot; existing TV 5/5 remains exhausted separately','prior_diagnostic_attempts':prior,'previous_task':{'card':bind(OLD/'RUNTIME_CARD.json'),'consumed_SUMO_starts':5,'wallclock_s':7.03850783398957,'final_bytes':170383856,'transferred_budget':0},'SUMO_HOME':str(H),'cwd':str(R),'environment':{'SUMO_HOME':str(H),'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','HOME':'inherit_only','PYTHON_and_loader_injection':'rejected'},'python':bind(py),'sumo_binary':bind(sumo),'sumo_version':'1.26.0 evidenced by archived C log and bound binary, re-read over same TraCI connection','network':bind(net),'executor':bind(B/'runtime_executor.py'),'observer':bind(B/'observer.py'),'static_receipt':bind(B/'static_validation_receipt.json'),'test_receipt':bind(B/'offline_test_receipt_revision02.json'),'input_manifest':bind(B/'input_manifest.json'),'user_authorization_binding':bind(B/'authorization_provenance.json'),'approval_path':str(B/'O2_RELEASE_APPROVAL.json'),'review_expected':{'status':'PASS_STATIC_FINAL','stage':'exact_o2_diagnostic_package','card_sha256':'must equal this final card; no circular embedded hash'},'attempt':{'attempt_id':'O2_C_S17_450_attempt3','run_root':str(RUN),'output_root':str(RUN/'outputs'),'argv':[str(py),'-B',str(B/'observer.py'),'--card',str(B/'O2_DIAGNOSTIC_CARD.json')]},'sumo_argv':[str(sumo),'-c',str(B/'inputs/scenario.sumocfg'),'--remote-port','8819','--num-clients','1'],'bindings':bindings}
write(B/'O2_DIAGNOSTIC_CARD.json',card)
write(B/'O2_RELEASE_APPROVAL.template.json',{'status':'TEMPLATE_NOT_RELEASED','card_sha256':bind(B/'O2_DIAGNOSTIC_CARD.json')['sha256'],'max_SUMO_starts':1,'scope':'single_C_seed17_end450_readonly_diagnostic','user_authorization_binding':card['user_authorization_binding'],'review_receipt':None,'release_rule':'Parent writes separate O2_RELEASE_APPROVAL.json only after exact review PASS, status conditionally_authorized_released_after_exact_review. Existing user instruction, not later personal approval of this SHA.'})
print(json.dumps({'card':bind(B/'O2_DIAGNOSTIC_CARD.json'),'binding_count':len(bindings),'python':str(py)}))
