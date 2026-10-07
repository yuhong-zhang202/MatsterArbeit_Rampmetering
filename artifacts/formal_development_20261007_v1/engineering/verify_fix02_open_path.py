"""Static partial evaluation of complete worker with mode=NOOP. No simulation."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path.cwd(); E=ROOT/'artifacts/formal_development_20261007_v1/engineering'
old=E/'pre_fix02_sources/v15_worker.py';new=ROOT/'scripts/formal_development_20261007_v1/v15_worker.py'
class Noop(ast.NodeTransformer):
 def visit_Compare(self,node):
  node=self.generic_visit(node)
  if isinstance(node.left,ast.Name) and node.left.id=='mode' and len(node.ops)==1 and isinstance(node.comparators[0],ast.Constant):
   value=node.comparators[0].value
   if isinstance(node.ops[0],ast.Eq): return ast.copy_location(ast.Constant(value=='NOOP'),node)
   if isinstance(node.ops[0],ast.NotEq): return ast.copy_location(ast.Constant(value!='NOOP'),node)
  return node
 def visit_BoolOp(self,node):
  node=self.generic_visit(node)
  constant=lambda n:isinstance(n,ast.Constant) and isinstance(n.value,bool)
  if isinstance(node.op,ast.And):
   if any(constant(n) and not n.value for n in node.values):return ast.Constant(False)
   node.values=[n for n in node.values if not(constant(n) and n.value)]
   if not node.values:return ast.Constant(True)
  else:
   if any(constant(n) and n.value for n in node.values):return ast.Constant(True)
   node.values=[n for n in node.values if not(constant(n) and not n.value)]
   if not node.values:return ast.Constant(False)
  return node.values[0] if len(node.values)==1 else node
 def visit_If(self,node):
  node=self.generic_visit(node)
  if isinstance(node.test,ast.Constant) and isinstance(node.test.value,bool):return node.body if node.test.value else node.orelse
  return node
 def visit_IfExp(self,node):
  node=self.generic_visit(node)
  if isinstance(node.test,ast.Constant) and isinstance(node.test.value,bool):return node.body if node.test.value else node.orelse
  return node

def worker(path):
 tree=ast.parse(path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='worker')
 return ast.dump(Noop().visit(fn),include_attributes=False)
assert worker(old)==worker(new),'NOOP execution path changed'
result={'status':'PASS_NOOP_WORKER_AST_EQUIVALENCE','old_source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'new_source_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'method':'Specialize all mode comparisons and Boolean conditionals with mode=NOOP; complete worker AST including traffic commands, step loop and output code remains byte-identical as AST. New helper import is pure; extra card field validation only occurs before TraCI import/spawn.','limits':'Static equivalence for validated new card and same runtime inputs. Not a new empirical run; existing full OPEN A03 neutrality remains its empirical evidence.','simulation_starts':0}
with (E/'FIX02_OPEN_EQUIVALENCE.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
