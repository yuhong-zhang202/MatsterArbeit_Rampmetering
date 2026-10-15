"""Execute actual V3 parser AST clauses on tiny valid/invalid schema examples."""
import ast
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).with_name('audit_run_W300_V3.py')
spec=importlib.util.spec_from_file_location('actual_v3',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
f=next(n for n in ast.parse(P.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='audit_raw')

class SchemaTests(unittest.TestCase):
 def test_actual_manifest_entry_and_terminal_wrapper_clauses(self):
  entry=next(n for n in f.body if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and [e.id for e in n.target.elts]==['name','entry'])
  terminal=next(n for n in f.body if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and [e.id for e in n.target.elts]==['index','row'])
  code_entry=compile(ast.fix_missing_locations(ast.Module(body=[deepcopy(entry)],type_ignores=[])),str(P),'exec')
  code_terminal=compile(ast.fix_missing_locations(ast.Module(body=[deepcopy(terminal)],type_ignores=[])),str(P),'exec')
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tiny').write_bytes(b'known')
   value={'sha256':hashlib.sha256(b'known').hexdigest(),'bytes':5}
   exec(code_entry,{**m.__dict__,'ROOT':root,'manifest':{'files':{'tiny':value}}})
   for invalid in [value['sha256'],{**value,'bytes':6}]:
    with self.subTest(invalid=invalid),self.assertRaises(m.Unknown):exec(code_entry,{**m.__dict__,'ROOT':root,'manifest':{'files':{'tiny':invalid}}})
  inner={'time_begin_s':0,'time_end_s':1,'accounting_complete':True}
  wrapper={'time_s':0,'retained_receipts':[inner],'pending':None,'last_accounted_s':1,'last_completed_s':1}
  rows=[deepcopy(wrapper)];exec(code_terminal,{**m.__dict__,'post':rows});self.assertEqual(rows,[inner])
  for invalid in [{**wrapper,'pending':{}},{**wrapper,'last_accounted_s':0}]:
   with self.subTest(invalid=invalid),self.assertRaises(m.Unknown):exec(code_terminal,{**m.__dict__,'post':[invalid]})

if __name__=='__main__':unittest.main()
