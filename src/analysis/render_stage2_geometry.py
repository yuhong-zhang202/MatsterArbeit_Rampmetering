#!/usr/bin/env python3
"""Render the compiled Stage 2 exploratory geometry without touching raw inputs.

The current renderer uses compiled network coordinates and Pillow from the
bundled runtime. PNG is authoritative; SVG wraps that same raster image.
Older renderer functions are retained as superseded implementation history and
are not used by the command-line entry point.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET


RAW_DEFAULT = Path("/private/tmp/minimal_uncontrolled_eozyn46f/network.net.xml")
ADD_DEFAULT = Path("/private/tmp/minimal_uncontrolled_eozyn46f/scenario.add.xml")
OUT_DEFAULT = Path("results/figures/stage2_geometry_20260909_v4")
MANIFEST_DEFAULT = Path("data/processed/stage2_geometry_20260909/manifest_v4.json")

COLORS = {
    "bg": "#ffffff", "external": "#7a8793", "internal": "#c5ccd3",
    "main": "#1f5a85", "ramp": "#d4772a", "urban": "#367a52",
    "cross": "#8d5a9e", "junction": "#f0f2f4", "boundary": "#c0392b",
    "text": "#20252b", "muted": "#59636d", "highlight": "#cc3d3d",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def points(raw: str):
    return [tuple(map(float, p.split(","))) for p in raw.split()]


def parse_network(path: Path):
    root = ET.parse(path).getroot()
    edges = []
    junctions = []
    connections = []
    for e in root.findall("edge"):
        lanes = []
        for lane in e.findall("lane"):
            lanes.append({"id": lane.get("id"), "length": float(lane.get("length", "nan")),
                          "shape": points(lane.get("shape", ""))})
        edges.append({"id": e.get("id"), "function": e.get("function", "normal"),
                      "from": e.get("from"), "to": e.get("to"), "lanes": lanes})
    for j in root.findall("junction"):
        junctions.append({"id": j.get("id"), "shape": points(j.get("shape", "")),
                          "x": float(j.get("x")), "y": float(j.get("y"))})
    for c in root.findall("connection"):
        connections.append({k: c.get(k) for k in ("from", "to", "via", "dir")})
    return edges, junctions, connections


def parse_add(path: Path):
    root = ET.parse(path).getroot()
    out = []
    for item in root:
        if item.tag in {"laneAreaDetector", "inductionLoop"}:
            out.append({"type": item.tag, "id": item.get("id"), "lane": item.get("lane"),
                        "pos": float(item.get("pos", "0")), "length": float(item.get("length", "0"))})
    return out


def bounds(edges, junctions):
    xy = [p for e in edges for lane in e["lanes"] for p in lane["shape"]]
    xy += [p for j in junctions for p in j["shape"]]
    xs, ys = zip(*xy)
    return min(xs), max(xs), min(ys), max(ys)


def family(edge_id):
    if edge_id.startswith("main_"):
        return "main"
    if edge_id.startswith("ramp_") or edge_id.startswith(":ramp_"):
        return "ramp"
    if edge_id.startswith("urban_") or edge_id.startswith(":urban_"):
        return "urban"
    if edge_id.startswith("cross_"):
        return "cross"
    return "external"


def svg_escape(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(edges, junctions, detectors, out: Path):
    W, H = 1800, 1100
    xmin, xmax, ymin, ymax = bounds(edges, junctions)
    pad = 85
    sx = (W - 2 * pad) / (xmax - xmin)
    sy = (H - 2 * pad) / (ymax - ymin)
    scale = min(sx, sy)
    ox = (W - scale * (xmax - xmin)) / 2 - scale * xmin
    oy = (H + scale * (ymax - ymin)) / 2 + scale * ymin
    def tr(p): return (ox + scale * p[0], oy - scale * p[1])
    def poly(ps): return " ".join(f"{x:.1f},{y:.1f}" for x, y in map(tr, ps))
    def txt(x, y, s, size=22, fill=COLORS["text"], anchor="start", weight="400"):
        return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial,sans-serif" font-size="{size}px" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{svg_escape(s)}</text>'
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
             txt(70, 52, "Exploratory compiled geometry — Stage 2 technical visual check", 30, weight="700"),
             txt(70, 88, "Compiled SUMO network; actual lane shapes and junction polygons; not a SUMO GUI screenshot", 17, COLORS["muted"])]
    # Junction polygons first, then all lanes over them.
    for j in junctions:
        if len(j["shape"]) >= 3:
            lines.append(f'<polygon points="{poly(j["shape"])}" fill="{COLORS["junction"]}" stroke="#aab3bc" stroke-width="1.4"/>')
    for e in edges:
        internal = e["function"] == "internal" or e["id"].startswith(":")
        for lane in e["lanes"]:
            pts = poly(lane["shape"])
            color = COLORS["internal"] if internal else COLORS[family(e["id"])]
            width = 6 if internal else 10
            lines.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    # Highlight the compiled shared-boundary to merge path: named + internal edges.
    # Begin at the downstream end of shared_approach; the named edge itself is
    # not claimed as part of the 494.87 m component sum.
    highlight_ids = {":urban_diverge_1", "ramp_storage", ":ramp_mid_0", "ramp_accel", ":freeway_merge_0"}
    for e in edges:
        if e["id"] in highlight_ids:
            for lane in e["lanes"]:
                lines.append(f'<polyline points="{poly(lane["shape"])}" fill="none" stroke="{COLORS["highlight"]}" stroke-opacity="0.82" stroke-width="5" stroke-dasharray="14 7" stroke-linecap="round"/>')
    # Detector positions, accurately projected along each lane polyline by lane length.
    lane_map = {lane["id"]: lane for e in edges for lane in e["lanes"]}
    for d in detectors:
        lane = lane_map.get(d["lane"])
        if not lane: continue
        frac = max(0.0, min(1.0, (d["pos"] if d["pos"] >= 0 else lane["length"]) / lane["length"]))
        a, b = lane["shape"][0], lane["shape"][-1]
        q = tr((a[0] + frac * (b[0] - a[0]), a[1] + frac * (b[1] - a[1])))
        lines.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="9" fill="{COLORS["boundary"]}" stroke="white" stroke-width="3"/>')
        if d["type"] == "laneAreaDetector":
            lines.append(txt(q[0] + 13, q[1] - 10, d["id"], 15, COLORS["boundary"], weight="700"))
    # Labels placed by actual coordinate anchors.
    labels = [(0, 895, "main_up / main_down (two lanes)", 18), (1020, 867, "ramp_storage 204.49 m", 18),
              (1260, 878, ":ramp_mid_0 internal 81.98 m", 16), (1070, 700, ":urban_diverge_1 internal 113.08 m", 16),
              (1330, 930, "ramp_accel 95.32 m", 18), (1160, 560, "shared approach -> merge path", 20)]
    for x, y, s, size in labels:
        q = tr((x, y)); lines.append(txt(q[0], q[1], s, size, COLORS["text"], weight="600"))
    # Inset with length accounting and semantic legend.
    ix, iy, iw, ih = 1200, 700, 560, 260
    lines.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="white" fill-opacity="0.96" stroke="#7d8790" stroke-width="2"/>')
    lines.append(txt(ix + 20, iy + 32, "Shared boundary → merge path accounting", 20, weight="700"))
    rows = [("internal urban_diverge", "113.08 m"), ("internal ramp_mid", "81.98 m"), ("named ramp_storage", "204.49 m"), ("named ramp_accel", "95.32 m"), ("compiled path total", "494.87 m")]
    yy = iy + 65
    for name, val in rows:
        lines.append(txt(ix + 22, yy, name, 17, COLORS["muted"])); lines.append(txt(ix + iw - 22, yy, val, 17, COLORS["text"], anchor="end", weight="700")); yy += 31
    lines.append(txt(ix + 20, iy + ih - 13, "Lengths are geometric path components; no safe/effective storage designation.", 14, COLORS["boundary"]))
    lines.append(txt(70, 1065, "E1 loops shown as red markers; exact lane/position definitions are in manifest. E2 configured 250 m is detector coverage, not storage length; extension beyond named lanes is unknown.", 14, COLORS["muted"]))
    # Legend.
    lx, ly = 70, H - 45
    legend = [(COLORS["main"], "named mainline edge"), (COLORS["ramp"], "named ramp edge"), (COLORS["urban"], "named urban edge"), (COLORS["internal"], "internal connection"), (COLORS["highlight"], "shared-boundary→merge path")]
    xx = lx
    for c, name in legend:
        lines.append(f'<line x1="{xx}" y1="{ly}" x2="{xx+35}" y2="{ly}" stroke="{c}" stroke-width="8"/>'); lines.append(txt(xx + 45, ly + 6, name, 15)); xx += 255 if name != "shared-boundary→merge path" else 300
    lines.append("</svg>")
    out.write_text("\n".join(lines), encoding="utf-8")
    return (W, H, xmin, xmax, ymin, ymax, scale, ox, oy)


def render_svg_v3(edges, junctions, detectors, out: Path):
    """Two-panel overview/local geometry view for the final manual check."""
    W,H=1900,1050; xmin,xmax,ymin,ymax=bounds(edges,junctions)
    panels=[(70,110,1030,820,xmin,xmax,ymin,ymax),(1160,110,670,820,970,1435,620,930)]
    def panel_transform(panel):
        px,py,pw,ph,x0,x1,y0,y1=panel; s=min(pw/(x1-x0),ph/(y1-y0)); ox=px+(pw-s*(x1-x0))/2-s*x0; oy=py+(ph+s*(y1-y0))/2+s*y0
        return lambda p:(ox+s*p[0],oy-s*p[1])
    def txt(x,y,s,size=20,fill=COLORS["text"],weight="400"): return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial,sans-serif" font-size="{size}px" font-weight="{weight}" fill="{fill}">{svg_escape(s)}</text>'
    lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="white"/>',txt(70,52,"Exploratory compiled geometry — Stage 2",32,weight="700"),txt(70,82,"Actual SUMO lane shapes and junction polygons; exploratory technical visual",18,COLORS["muted"])]
    hi={":urban_diverge_1","ramp_storage",":ramp_mid_0","ramp_accel",":freeway_merge_0"}
    for idx,panel in enumerate(panels):
        px,py,pw,ph,*_=panel; tr=panel_transform(panel); lines.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="white" stroke="#aab3bc" stroke-width="2"/>'); lines.append(txt(px+18,py+30,"OVERVIEW" if idx==0 else "LOCAL GEOMETRY: DIVERGE → MERGE",20,weight="700"))
        for j in junctions:
            if len(j["shape"])>=3: lines.append(f'<polygon points="{" ".join(f"{tr(q)[0]:.1f},{tr(q)[1]:.1f}" for q in j["shape"])}" fill="{COLORS["junction"]}" stroke="#aab3bc" stroke-width="1.2"/>')
        for e in edges:
            internal=e["function"]=="internal" or e["id"].startswith(":"); c=COLORS["internal"] if internal else COLORS[family(e["id"])]
            for lane in e["lanes"]:
                lines.append(f'<polyline points="{" ".join(f"{tr(q)[0]:.1f},{tr(q)[1]:.1f}" for q in lane["shape"])}" fill="none" stroke="{c}" stroke-width="{5 if internal else 8}" stroke-linecap="round" stroke-linejoin="round"/>')
        for e in edges:
            if e["id"] in hi:
                for lane in e["lanes"]: lines.append(f'<polyline points="{" ".join(f"{tr(q)[0]:.1f},{tr(q)[1]:.1f}" for q in lane["shape"])}" fill="none" stroke="{COLORS["highlight"]}" stroke-width="5" stroke-dasharray="12 6"/>')
        if idx==1:
            for q,label in [((1001.60,642.80),"PATH START"),((1393.79,902.13),"PATH END")]:
                x,y=tr(q); lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{COLORS["boundary"]}" stroke="white" stroke-width="3"/>'); lines.append(txt(x+14,y-10,label,16,COLORS["boundary"],"700"))
    lines += [txt(70,970,"Red dashed path starts at the downstream shared-boundary/diverge point and ends at the acceleration-to-merge entry; no safe-storage designation.",16,COLORS["muted"]),txt(70,995,"E2: only named-lane positions are asserted; configured 250 m is detector coverage, not storage length; branch extension unknown.",16,COLORS["muted"]),"</svg>"]
    out.write_text("\n".join(lines),encoding="utf-8")


def png_render_pillow_v3(edges, junctions, out: Path):
    from PIL import Image, ImageDraw, ImageFont
    W,H=2400,1320; im=Image.new("RGB",(W,H),(255,255,255)); d=ImageDraw.Draw(im); fp="/System/Library/Fonts/Helvetica.ttc"
    def font(n,b=False): return ImageFont.truetype(fp,n,index=1 if b else 0)
    rgb=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5)); d.text((80,38),"Exploratory compiled geometry — Stage 2",fill=rgb(COLORS["text"]),font=font(42,True)); d.text((80,86),"Actual SUMO lane shapes and junction polygons; exploratory technical visual",fill=rgb(COLORS["muted"]),font=font(23))
    xmin,xmax,ymin,ymax=bounds(edges,junctions); panels=[(80,140,1120,1020,xmin,xmax,ymin,ymax),(1280,140,1040,1020,970,1435,620,930)]; hi={":urban_diverge_1","ramp_storage",":ramp_mid_0","ramp_accel",":freeway_merge_0"}
    for idx,(px,py,pw,ph,x0,x1,y0,y1) in enumerate(panels):
        s=min(pw/(x1-x0),ph/(y1-y0)); ox=px+(pw-s*(x1-x0))/2-s*x0; oy=py+(ph+s*(y1-y0))/2+s*y0; tr=lambda q:(round(ox+s*q[0]),round(oy-s*q[1])); d.rectangle((px,py,px+pw,py+ph),outline=(170,179,188),width=3); d.text((px+22,py+24),"OVERVIEW" if idx==0 else "LOCAL GEOMETRY: DIVERGE -> MERGE",fill=rgb(COLORS["text"]),font=font(25,True))
        for j in junctions:
            if len(j["shape"])>=3: d.polygon([tr(q) for q in j["shape"]],fill=rgb(COLORS["junction"]),outline=(170,179,188))
        for e in edges:
            internal=e["function"]=="internal" or e["id"].startswith(":"); c=rgb(COLORS["internal"] if internal else COLORS[family(e["id"])])
            for lane in e["lanes"]: d.line([tr(q) for q in lane["shape"]],fill=c,width=8 if internal else 13,joint="curve")
        for e in edges:
            if e["id"] in hi:
                for lane in e["lanes"]: d.line([tr(q) for q in lane["shape"]],fill=rgb(COLORS["highlight"]),width=7,joint="curve")
        if idx==1:
            for q,label in [((1001.60,642.80),"PATH START"),((1393.79,902.13),"PATH END")]:
                x,y=tr(q); d.ellipse((x-12,y-12,x+12,y+12),fill=rgb(COLORS["boundary"]),outline="white",width=3); d.text((x+18,y-25),label,fill=rgb(COLORS["boundary"]),font=font(21,True))
    d.text((80,1200),"Red dashed path starts at downstream shared-boundary/diverge point and ends at acceleration-to-merge entry; no safe-storage designation.",fill=rgb(COLORS["muted"]),font=font(20)); d.text((80,1240),"E2: only named-lane positions asserted; configured 250 m is detector coverage, not storage length; branch extension unknown.",fill=rgb(COLORS["muted"]),font=font(20)); im.save(out,format="PNG",optimize=False)


# Minimal RGB PNG rasterizer: lines, polygons, circles and 5x7 labels.
FONT = {"A":["01110","10001","10001","11111","10001","10001","10001"],"B":["11110","10001","10001","11110","10001","10001","11110"],"C":["01111","10000","10000","10000","10000","10000","01111"],"D":["11110","10001","10001","10001","10001","10001","11110"],"E":["11111","10000","10000","11110","10000","10000","11111"],"F":["11111","10000","10000","11110","10000","10000","10000"],"G":["01111","10000","10000","10111","10001","10001","01111"],"H":["10001","10001","10001","11111","10001","10001","10001"],"I":["11111","00100","00100","00100","00100","00100","11111"],"J":["00111","00010","00010","00010","10010","10010","01100"],"K":["10001","10010","10100","11000","10100","10010","10001"],"L":["10000","10000","10000","10000","10000","10000","11111"],"M":["10001","11011","10101","10101","10001","10001","10001"],"N":["10001","11001","10101","10011","10001","10001","10001"],"O":["01110","10001","10001","10001","10001","10001","01110"],"P":["11110","10001","10001","11110","10000","10000","10000"],"Q":["01110","10001","10001","10001","10101","10010","01101"],"R":["11110","10001","10001","11110","10100","10010","10001"],"S":["01111","10000","10000","01110","00001","00001","11110"],"T":["11111","00100","00100","00100","00100","00100","00100"],"U":["10001","10001","10001","10001","10001","10001","01110"],"V":["10001","10001","10001","10001","10001","01010","00100"],"W":["10001","10001","10001","10101","10101","11011","10001"],"X":["10001","10001","01010","00100","01010","10001","10001"],"Y":["10001","10001","01010","00100","00100","00100","00100"],"Z":["11111","00001","00010","00100","01000","10000","11111"],"0":["01110","10001","10011","10101","11001","10001","01110"],"1":["00100","01100","00100","00100","00100","00100","01110"],"2":["01110","10001","00001","00010","00100","01000","11111"],"3":["11110","00001","00001","01110","00001","00001","11110"],"4":["00010","00110","01010","10010","11111","00010","00010"],"5":["11111","10000","10000","11110","00001","00001","11110"],"6":["01110","10000","10000","11110","10001","10001","01110"],"7":["11111","00001","00010","00100","01000","01000","01000"],"8":["01110","10001","10001","01110","10001","10001","01110"],"9":["01110","10001","10001","01111","00001","00001","01110"],"-":["00000","00000","00000","11111","00000","00000","00000"],".":["00000","00000","00000","00000","00000","00110","00110"],":":["00000","00110","00110","00000","00110","00110","00000"],"/":["00001","00010","00100","01000","10000","00000","00000"]}


def png_render(svg_meta, edges, junctions, detectors, out: Path):
    W, H, xmin, xmax, ymin, ymax, scale, ox, oy = svg_meta
    # Supersample for smooth lines; labels remain intentionally compact.
    S = 2; w, h = W*S, H*S; pix = bytearray([255,255,255])*(w*h)
    def tr(p): return (int(round((ox + scale*p[0])*S)), int(round((oy-scale*p[1])*S)))
    def put(x,y,c):
        if 0<=x<w and 0<=y<h: pix[(y*w+x)*3:(y*w+x)*3+3] = bytes(c)
    def line(a,b,c,width=2):
        x0,y0=tr(a); x1,y1=tr(b); dx=abs(x1-x0); sx=1 if x0<x1 else -1; dy=-abs(y1-y0); sy=1 if y0<y1 else -1; err=dx+dy
        while True:
            for yy in range(y0-width,y0+width+1):
                for xx in range(x0-width,x0+width+1): put(xx,yy,c)
            if x0==x1 and y0==y1: break
            e2=2*err
            if e2>=dy: err+=dy; x0+=sx
            if e2<=dx: err+=dx; y0+=sy
    def line_screen(a,b,c,width=2):
        x0,y0=a; x1,y1=b; dx=abs(x1-x0); sx=1 if x0<x1 else -1; dy=-abs(y1-y0); sy=1 if y0<y1 else -1; err=dx+dy
        while True:
            for yy in range(y0-width,y0+width+1):
                for xx in range(x0-width,x0+width+1): put(xx,yy,c)
            if x0==x1 and y0==y1: break
            e2=2*err
            if e2>=dy: err+=dy; x0+=sx
            if e2<=dx: err+=dx; y0+=sy
    rgb=lambda hx: tuple(int(hx[i:i+2],16) for i in (1,3,5))
    for e in edges:
        c=rgb(COLORS["internal"] if e["function"]=="internal" or e["id"].startswith(":") else COLORS[family(e["id"])] )
        for lane in e["lanes"]:
            for a,b in zip(lane["shape"],lane["shape"][1:]): line(a,b,c,3 if e["function"]=="internal" else 5)
    hi={":urban_diverge_1","ramp_storage",":ramp_mid_0","ramp_accel",":freeway_merge_0"}
    for e in edges:
        if e["id"] in hi:
            for lane in e["lanes"]:
                for a,b in zip(lane["shape"],lane["shape"][1:]): line(a,b,rgb(COLORS["highlight"]),3)
    # Basic labels in uppercase bitmap font; enough for source traceability.
    def label(x,y,text,color=(32,37,43),sc=3):
        xx,yy=tr((x,y)); text=text.upper();
        for ch in text:
            glyph=FONT.get(ch, ["00000"]*7)
            for ry,row in enumerate(glyph):
                for rx,v in enumerate(row):
                    if v=="1":
                        for dy in range(sc):
                            for dx in range(sc): put(xx+rx*sc+dx, yy+ry*sc+dy, color)
            xx += 6*sc
    def label_screen(x,y,text,color=(32,37,43),sc=3):
        xx,yy=int(x*S),int(y*S); text=text.upper()
        for ch in text:
            glyph=FONT.get(ch, ["00000"]*7)
            for ry,row in enumerate(glyph):
                for rx,v in enumerate(row):
                    if v=="1":
                        for dy in range(sc*S):
                            for dx in range(sc*S): put(xx+rx*sc*S+dx, yy+ry*sc*S+dy, color)
            xx += 6*sc*S
    label(0,875,"MAIN UP/DOWN",sc=3); label(1030,847,"RAMP STORAGE 204.49 M",sc=3); label(1260,855,"INTERNAL 81.98 M",sc=2); label(1070,685,"INTERNAL 113.08 M",sc=2); label(1320,920,"ACCEL 95.32 M",sc=3); label(1120,540,"SHARED BOUNDARY TO MERGE",sc=3)
    label_screen(70,27,"EXPLORATORY COMPILED GEOMETRY - STAGE 2",sc=4)
    label_screen(70,64,"ACTUAL SUMO LANE SHAPES AND JUNCTION POLYGONS",color=(89,99,109),sc=2)
    # Keep the accounting inset visible in the PNG as well as the SVG.
    ix,iy,iw,ih=1200,700,560,260
    edge=rgb("#7d8790")
    for a,b in [((ix,iy),(ix+iw,iy)),((ix+iw,iy),(ix+iw,iy+ih)),((ix+iw,iy+ih),(ix,iy+ih)),((ix,iy+ih),(ix,iy))]: line_screen((a[0]*S,a[1]*S),(b[0]*S,b[1]*S),edge,2)
    label_screen(ix+20,iy+18,"PATH ACCOUNTING",color=(32,37,43),sc=3)
    for n,(name,val) in enumerate([("INTERNAL URBAN DIVERGE","113.08 M"),("INTERNAL RAMP MID","81.98 M"),("NAMED RAMP STORAGE","204.49 M"),("NAMED RAMP ACCEL","95.32 M"),("COMPILED PATH TOTAL","494.87 M")]):
        label_screen(ix+20,iy+49+n*31,name,color=(89,99,109),sc=2); label_screen(ix+360,iy+49+n*31,val,color=(32,37,43),sc=2)
    label_screen(ix+20,iy+ih-27,"NO SAFE STORAGE DESIGNATION",color=(192,57,43),sc=2)
    # Compact legend at bottom.
    label_screen(70,1060,"BLUE MAIN  ORANGE RAMP  GREEN URBAN  GREY INTERNAL  RED PATH",color=(32,37,43),sc=2)
    label_screen(70,1080,"E2 CONFIGURED 250 M = DETECTOR COVERAGE, NOT STORAGE LENGTH; EXTENSION NOT INTERPRETED",color=(89,99,109),sc=2)
    # PNG encoder.
    raw=b"".join(b"\x00"+bytes(pix[y*w*3:(y+1)*w*3]) for y in range(h))
    def chunk(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")
    out.write_bytes(data)


def png_render_pillow(svg_meta, edges, junctions, detectors, out: Path):
    """High-quality PNG path when the project runtime provides Pillow."""
    from PIL import Image, ImageDraw, ImageFont
    _, _, xmin, xmax, ymin, ymax, scale0, ox0, oy0 = svg_meta
    W, H = 2400, 1460
    scale = min((W - 180) / (xmax - xmin), (H - 180) / (ymax - ymin))
    ox = (W - scale * (xmax - xmin)) / 2 - scale * xmin
    oy = (H + scale * (ymax - ymin)) / 2 + scale * ymin
    def tr(p): return (round(ox + scale*p[0]), round(oy - scale*p[1]))
    rgb=lambda hx: tuple(int(hx[i:i+2],16) for i in (1,3,5))
    im=Image.new("RGB",(W,H),(255,255,255)); d=ImageDraw.Draw(im)
    font_path="/System/Library/Fonts/Helvetica.ttc"
    def font(sz,bold=False):
        try: return ImageFont.truetype(font_path,sz,index=1 if bold else 0)
        except Exception: return ImageFont.load_default()
    d.text((80,35),"Exploratory compiled geometry — Stage 2",fill=rgb(COLORS["text"]),font=font(40,True))
    d.text((80,82),"Compiled SUMO network; actual lane shapes and junction polygons; not a SUMO GUI screenshot",fill=rgb(COLORS["muted"]),font=font(22))
    for j in junctions:
        if len(j["shape"])>=3: d.polygon([tr(p) for p in j["shape"]],fill=rgb(COLORS["junction"]),outline=(170,179,188))
    for e in edges:
        internal=e["function"]=="internal" or e["id"].startswith(":")
        c=rgb(COLORS["internal"] if internal else COLORS[family(e["id"])])
        for lane in e["lanes"]: d.line([tr(p) for p in lane["shape"]],fill=c,width=8 if internal else 14,joint="curve")
    hi={":urban_diverge_1","ramp_storage",":ramp_mid_0","ramp_accel",":freeway_merge_0"}
    for e in edges:
        if e["id"] in hi:
            for lane in e["lanes"]: d.line([tr(p) for p in lane["shape"]],fill=rgb(COLORS["highlight"]),width=7,joint="curve")
    lane_map={lane["id"]:lane for e in edges for lane in e["lanes"]}
    for det in detectors:
        lane=lane_map.get(det["lane"])
        if not lane: continue
        frac=max(0,min(1,(det["pos"] if det["pos"]>=0 else lane["length"])/lane["length"]))
        a,b=lane["shape"][0],lane["shape"][-1]; q=tr((a[0]+frac*(b[0]-a[0]),a[1]+frac*(b[1]-a[1])))
        d.ellipse((q[0]-12,q[1]-12,q[0]+12,q[1]+12),fill=rgb(COLORS["boundary"]),outline="white",width=3)
        if det["type"] == "laneAreaDetector": d.text((q[0]+17,q[1]-22),det["id"],fill=rgb(COLORS["boundary"]),font=font(18,True))
    labels=[((0,875),"main_up / main_down (two lanes)"),((1030,847),"ramp_storage 204.49 m"),((1260,855),":ramp_mid_0 internal 81.98 m"),((1070,685),":urban_diverge_1 internal 113.08 m"),((1320,920),"ramp_accel 95.32 m"),((1120,540),"shared boundary -> merge path")]
    for p,s in labels: d.text(tr(p),s,fill=rgb(COLORS["text"]),font=font(22,True))
    ix,iy,iw,ih=1540,910,790,410
    d.rectangle((ix,iy,ix+iw,iy+ih),fill=(255,255,255),outline=(125,135,144),width=3)
    d.text((ix+25,iy+22),"Shared boundary → merge path accounting",fill=rgb(COLORS["text"]),font=font(26,True))
    rows=[("internal urban_diverge","113.08 m"),("internal ramp_mid","81.98 m"),("named ramp_storage","204.49 m"),("named ramp_accel","95.32 m"),("compiled path total","494.87 m")]
    for n,(name,val) in enumerate(rows):
        yy=iy+70+n*47; d.text((ix+28,yy),name,fill=rgb(COLORS["muted"]),font=font(21)); d.text((ix+iw-205,yy),val,fill=rgb(COLORS["text"]),font=font(21,True))
    d.text((ix+25,iy+ih-45),"No safe/effective storage designation.",fill=rgb(COLORS["boundary"]),font=font(19))
    d.text((80,H-75),"Blue mainline   Orange ramp   Green urban   Grey internal   Red = compiled component path",fill=rgb(COLORS["text"]),font=font(20))
    d.text((80,H-42),"E1 loops shown as red markers; exact lane/position definitions are in manifest. E2 configured 250 m is detector coverage, not storage length; extension beyond named lane is unknown",fill=rgb(COLORS["muted"]),font=font(18))
    im.save(out,format="PNG",optimize=False)


def render_checked(edges, junctions, png_path, svg_path):
    """Render isolated, equal-scale panels; older renderers are superseded."""
    import base64
    from PIL import Image, ImageDraw, ImageFont

    canvas = Image.new("RGB", (2400, 1250), "white")
    draw = ImageDraw.Draw(canvas)
    def font(size, bold=False):
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size, index=1 if bold else 0)
    draw.text((65, 30), "Stage 2: actual compiled road geometry", fill="#20252b", font=font(39, True))
    draw.text((65, 85), "Static XML rendering, not a SUMO GUI screenshot. No effective storage area has been approved.", fill="#59636d", font=font(24))
    lanes = {lane["id"]: lane for edge in edges for lane in edge["lanes"]}
    component_ids = [":urban_diverge_1_0", "ramp_storage_0", ":ramp_mid_0_0", "ramp_accel_0"]
    assert round(sum(lanes[key]["length"] for key in component_ids), 2) == 494.87
    start = lanes[component_ids[0]]["shape"][0]
    end = lanes[component_ids[-1]]["shape"][-1]
    assert start == lanes["shared_approach_0"]["shape"][-1]
    colors = {"main": "#245e84", "ramp": "#d47622", "urban": "#427a57", "cross": "#8a95a0", "external": "#427a57"}
    for local, left, width, box in [(False, 65, 1090, (-70, 2270, -60, 1020)), (True, 1215, 1120, (960, 1470, 600, 990))]:
        height = 910
        panel = Image.new("RGB", (width, height), "#fbfcfd")
        pd = ImageDraw.Draw(panel)
        x0, x1, y0, y1 = box
        scale = min((width-80)/(x1-x0), (height-175)/(y1-y0))
        ox = (width-scale*(x1-x0))/2-scale*x0
        oy = 85+(height-130+scale*(y1-y0))/2+scale*y0
        def tr(point):
            return (ox+scale*point[0], oy-scale*point[1])
        pd.text((24, 20), "RAMP DETAIL" if local else "NETWORK OVERVIEW", fill="#20252b", font=font(25, True))
        for junction in junctions:
            if len(junction["shape"]) >= 3:
                pd.polygon([tr(p) for p in junction["shape"]], fill="#e0e6ec", outline="#9daab8")
        for edge in edges:
            internal = edge["function"] == "internal" or edge["id"].startswith(":")
            color = "#8552b5" if internal else colors[family(edge["id"])]
            for lane in edge["lanes"]:
                pd.line([tr(p) for p in lane["shape"]], fill=color, width=5 if internal else 6, joint="curve")
        # Separate panel images provide strict clipping, including long mainline edges.
        if local:
            def callout(point, text, target, color="#20252b"):
                p = tr(point)
                pd.line([p, target], fill="#74818c", width=2)
                pd.text(target, text, fill=color, font=font(23, True))
            for point, label, delta in [(start, "START: shared-road end", (16, 18)), (end, "END: before merge", (-235, -66))]:
                px, py = tr(point)
                pd.ellipse((px-8, py-8, px+8, py+8), fill="#b52f2b", outline="white", width=2)
                pd.text((px+delta[0], py+delta[1]), label, fill="#b52f2b", font=font(23, True))
            callout((1030.04, 691.38), "Internal connection: 113.08 m", (190, 760), "#8552b5")
            callout((1140.98, 818.71), "Named storage: 204.49 m", (130, 335), "#a7520d")
            callout((1260.34, 874.07), "Internal connection: 81.98 m", (355, 185), "#8552b5")
            callout((1347.05, 892.78), "Acceleration: 95.32 m", (710, 380), "#a7520d")
        else:
            pd.text((35, 740), "Blue: freeway   Green: urban roads", fill="#245e84", font=font(25))
            pd.text((35, 782), "Orange: named ramp edges   Purple: internal lanes", fill="#59636d", font=font(23))
            pd.text((35, 825), "Pale polygons: compiled junction areas", fill="#59636d", font=font(23))
        pd.rectangle((0, 0, width-1, height-1), outline="#adb7c0", width=2)
        canvas.paste(panel, (left, 155))
    draw.text((65, 1100), "Path between marked endpoints: 113.08 + 204.49 + 81.98 + 95.32 = 494.87 m", fill="#20252b", font=font(28, True))
    draw.text((65, 1150), "Path length is not safe queue capacity. Shared road and merge-internal connection are excluded from this sum.", fill="#59636d", font=font(24))
    draw.text((65, 1190), "Detector coverage is audited separately; successor-lane extension has not been runtime-verified.", fill="#59636d", font=font(23))
    canvas.save(png_path, format="PNG")
    # Exact visual twin, intentionally a raster-backed SVG, not a second geometry renderer.
    encoded = base64.b64encode(png_path.read_bytes()).decode("ascii")
    svg_path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1250"><image width="2400" height="1250" href="data:image/png;base64,{encoded}"/></svg>\n')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--network",type=Path,default=RAW_DEFAULT); ap.add_argument("--additional",type=Path,default=ADD_DEFAULT); ap.add_argument("--svg",type=Path,default=OUT_DEFAULT.with_suffix(".svg")); ap.add_argument("--png",type=Path,default=OUT_DEFAULT.with_suffix(".png")); ap.add_argument("--manifest",type=Path,default=MANIFEST_DEFAULT); args=ap.parse_args()
    if not args.network.is_file() or not args.additional.is_file(): raise SystemExit("missing compiled network or matching additional XML")
    for destination in (args.svg, args.png, args.manifest):
        if destination.exists():
            raise SystemExit(f"Refusing to overwrite existing artifact: {destination}")
    before=sha256(args.network); edges,junctions,connections=parse_network(args.network); detectors=parse_add(args.additional)
    # The requested 494.87 m accounting is the four compiled components from
    # the shared-boundary split to the merge: two internal lanes plus the named
    # storage and acceleration edges.  shared_approach and the merge's short
    # internal connector remain visible but are outside this stated sum.
    path_ids=[":urban_diverge_1","ramp_storage",":ramp_mid_0","ramp_accel"]
    by_id={e["id"]:e for e in edges}; total=sum(by_id[e]["lanes"][0]["length"] for e in path_ids)
    if abs(total-494.87)>0.01: raise SystemExit(f"compiled path length changed: {total}")
    args.svg.parent.mkdir(parents=True,exist_ok=True); args.png.parent.mkdir(parents=True,exist_ok=True); args.manifest.parent.mkdir(parents=True,exist_ok=True)
    render_checked(edges, junctions, args.png, args.svg)
    after=sha256(args.network)
    if before!=after: raise SystemExit("network source changed during rendering")
    manifest={"task":"stage2 compiled geometry exploratory rendering","source":{"network":str(args.network),"network_sha256_before":before,"network_sha256_after":after,"additional":str(args.additional),"additional_sha256":sha256(args.additional)},"checks":{"edge_count":len(edges),"junction_count":len(junctions),"connection_count":len(connections),"compiled_path_edge_ids":path_ids,"compiled_path_length_m":round(total,2),"expected_compiled_path_length_m":494.87,"labels":{"ramp_storage_m":204.49,"internal_urban_diverge_m":113.08,"internal_ramp_mid_m":81.98,"ramp_accel_m":95.32},"detectors":detectors},"outputs":{"svg":str(args.svg),"svg_sha256":sha256(args.svg),"png":str(args.png),"png_sha256":sha256(args.png)},"limitations":["Exploratory technical geometry visual only; no safe/effective storage designation.","E2 coverage is asserted only on the named lane segment from the additional XML; any extension beyond that lane or into a branch is unknown and not interpreted.","PNG uses a deterministic Pillow renderer when available, otherwise the built-in fallback; SVG preserves vector geometry."]}
    manifest["limitations"] = [
        "Static compiled geometry only; no live SUMO GUI or dynamic validation.",
        "No effective/safe storage designation; detector coverage is audited separately, not drawn as verified extent.",
        "Pillow PNG is authoritative; SVG embeds the same raster image and is not independent vector geometry.",
        "Versions before v4 are superseded; retain them for provenance, not interpretation."
    ]
    args.manifest.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__": main()
