"""Registered offline analysis only; no scenario runner or process execution."""
from pathlib import Path
import json,csv,sys
from unittest.mock import patch
R=Path.cwd();sys.path.insert(0,str(R));B=R/'data/processed/stage6_obstacle_20260913_v1';D=B/'d2_data_review_revision_01'
from src.scenarios import stage6_h2_offline as o
from src.analysis import stage6_h2_measurement as m,stage6_h2_pipeline as p
card=o.load_card();names={'tripinfo.xml','fcd.xml','tls_states.xml'}|{f'{q}_l{k}.xml' for q in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1') for k in (0,1)}
registry_binding=next(b for b in card['artifact_bindings'] if Path(b['path']).name=='source_registry.csv');registry=list(csv.DictReader(o.verify_binding(registry_binding).open()));analyses=[]
with patch('subprocess.Popen',side_effect=AssertionError('No processes permitted during registered offline analysis')):
 for condition,attempt in [('ML','S6_V1_ML_S17_attempt3'),('C','S6_V1_C_S17_attempt1')]:
  run=f'S6_V1_{condition}_S17';A=B/'c04_launch_preparation_revision_03/attempts'/attempt;receipt=o.read_json(A/'execution_receipt.json');sources={n:receipt['output_bindings'][n] for n in names};sources['network.net.xml']=receipt['network'];target=D/(run+'_registered_analysis')
  m.analyze_to_new_directory(sources,run,target,execution_receipt=o.bind(A/'execution_receipt.json'));analyses.append(o.bind(target/'analysis_manifest.json'))
 for condition in ('ML','C'):
  run=f'S6_V0_{condition}_S17';row=next(r for r in card['logical_runs'] if r['run_id']==run);registered=next(r for r in registry if r['run_id']==row['parent_source_id']);A=Path(registered['archive_path']);source_map=o.read_json(o.verify_binding({'path':registered['source_map_path'],'sha256':registered['source_map_sha256']}));mapped={str(R/f['archive_relative_path']):f['sha256'] for f in source_map['file_map']}
  sources={n:{'path':str(A/'outputs'/n),'sha256':mapped[str(A/'outputs'/n)]} for n in names};sources['network.net.xml']={'path':str(A/'network.net.xml'),'sha256':mapped[str(A/'network.net.xml')]};target=D/(run+'_registered_reuse_analysis')
  m.analyze_to_new_directory(sources,run,target);analyses.append(o.bind(target/'analysis_manifest.json'))
 manifest=p.assemble_rule_tables(analyses,D/'registered_fixed_rule_tables')
print(json.dumps(manifest['counts']));print(manifest['all_required_supported'])
