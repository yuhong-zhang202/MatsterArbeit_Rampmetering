"""Remove only explicitly empty optional detector filters; preserve non-empty filters."""
import re
DETECTORS={'laneAreaDetector','inductionLoop'}
def repair(text):
 count=0
 def node(match):
  nonlocal count
  tag,attrs=match.group(1),match.group(2)
  if tag not in DETECTORS:return match.group(0)
  attrs,n=re.subn(r'\s+(?:vTypes|nextEdges)=""','',attrs);count+=n
  return '<'+tag+attrs+'/>'
 output=re.sub(r'<(\w+)([^<>]*?)/>',node,text)
 return output,count
