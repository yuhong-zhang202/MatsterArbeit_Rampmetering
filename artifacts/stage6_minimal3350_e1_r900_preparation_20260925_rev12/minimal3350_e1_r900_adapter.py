from __future__ import annotations
import hashlib,json
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET
M_FIELDS=("id","type","route","depart","departPos","departLane","departSpeed","speedFactor")
EXPECTED_M,EXPECTED_R,R_BEGIN_MS,R_INTERVAL_MS=1396,240,540000,4000
def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ms(s):
 v=Decimal(s)*1000
 if v!=v.to_integral_value(): raise ValueError("non-integer-ms departure")
 return int(v)
def vm(path,prefix):
 out={}
 for n in ET.parse(path).getroot():
  if n.tag=="vehicle" and (n.get("id") or "").startswith(prefix):
   if n.get("id") in out: raise ValueError("duplicate vehicle ID")
   out[n.get("id")]=n
 return out
def sig(n):
 if any(n.get(k) is None for k in M_FIELDS): raise ValueError("required attribute missing")
 return tuple(n.get(k) for k in M_FIELDS)
def validate_treatment_card(card,demand,common_manifest,r_source,repo,control_demand):
 if sha256(common_manifest)!=card["common_m_manifest"]["sha256"]: raise ValueError("common M manifest hash mismatch")
 mf=json.loads(Path(common_manifest).read_text()); expected={f"M_flow.{i}" for i in range(EXPECTED_M)}
 if mf.get("planned_count")!=EXPECTED_M or len(mf.get("records",[]))!=EXPECTED_M: raise ValueError("M manifest count mismatch")
 cm,tm=vm(control_demand,"M_flow."),vm(demand,"M_flow.")
 if set(cm)!=expected or set(tm)!=expected: raise ValueError("M ID/count mismatch")
 rows={x["id"]:x for x in mf["records"]}
 for vid in expected:
  row=rows[vid]
  if sig(cm[vid])!=tuple(str(row[k]) for k in M_FIELDS) or sig(tm[vid])!=tuple(str(row[k]) for k in M_FIELDS): raise ValueError(f"M field mismatch: {vid}")
  if row["desired_depart_ms"]!=ms(tm[vid].get("depart")): raise ValueError("M schedule mismatch")
 if sha256(r_source)!=card["r_vehicle_source"]["sha256"]: raise ValueError("R vector hash mismatch")
 tr,sr=vm(demand,"R_flow."),vm(r_source,"R_flow."); rids={f"R_flow.{i}" for i in range(EXPECTED_R)}
 if set(tr)!=rids or set(sr)!=rids: raise ValueError("R count/ID mismatch")
 for i in range(EXPECTED_R):
  vid=f"R_flow.{i}"; expected_ms=R_BEGIN_MS+i*R_INTERVAL_MS
  if sig(tr[vid])!=sig(sr[vid]) or ms(tr[vid].get("depart"))!=expected_ms: raise ValueError(f"R source/schedule mismatch: {vid}")
 if ms(tr["R_flow.239"].get("depart"))!=1496000: raise ValueError("last R depart must be 1496000ms")
 if any(ms(n.get("depart"))>=1500000 for n in tr.values()): raise ValueError("R outside half-open [540,1500) window")
 ids={n.get("id") for n in ET.parse(demand).getroot() if n.tag=="vehicle"}
 if ids!=expected|rids: raise ValueError("treatment-only delta is not exact R240")
 return {"status":"PASS","m_count":1396,"m_exact_matches":1396,"r_count":240,"r_only_delta":"R_flow.0..239","u_explicit_zero":True,"x_explicit_zero":True,"r_schedule_ms":[540000,1496000,4000]}
