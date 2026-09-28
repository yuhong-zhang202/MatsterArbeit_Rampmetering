#!/usr/bin/env python3
"""Verify TLS and summary alternatives without changing outcome tables."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import xml.etree.ElementTree as ET
from analyze import digest

def rows(path,tag):
    return [dict(x.attrib) for x in ET.parse(path).getroot() if x.tag==tag]

def main():
    p=argparse.ArgumentParser()
    for n in ('r0','a','phase1','output'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();gate=json.loads(a.phase1.read_text())
    for raw,k in ((a.r0,'R0_raw_hashes'),(a.a,'A_raw_hashes')):
        for n in ('tls_states.xml','sumo_summary.xml'):
            if digest(raw/n)!=gate['provenance'][k][n]:raise ValueError('Raw drift: '+n)
    r0=rows(a.r0/'tls_states.xml','tlsState');treat=rows(a.a/'tls_states.xml','tlsState')
    s0=rows(a.r0/'sumo_summary.xml','step');sa=rows(a.a/'sumo_summary.xml','step')
    result={'TLS_R0_entries':len(r0),'TLS_A_entries':len(treat),
            'TLS_semantically_identical':r0==treat,
            'summary_steps_R0':len(s0),'summary_steps_A':len(sa),
            'R0_final':{k:s0[-1].get(k) for k in ('inserted','arrived','discarded','collisions','teleports','running','waiting')},
            'A_final':{k:sa[-1].get(k) for k in ('inserted','arrived','discarded','collisions','teleports','running','waiting')},
            'phase1_sha256':digest(a.phase1)}
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
