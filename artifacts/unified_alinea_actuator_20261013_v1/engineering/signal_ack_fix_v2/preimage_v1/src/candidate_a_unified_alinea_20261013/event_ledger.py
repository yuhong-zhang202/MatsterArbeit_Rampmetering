"""Unmodified project E1 ledger class copied with provenance in engineering receipt."""
import math
DETECTORS=('p1_main_down_20_l0','p1_main_down_20_l1')

class DetectorEventLedger:
    """Keep E1 detector events across XML reset boundaries, with no time union."""
    def __init__(self, begin_s=600):
        self.begin_s = begin_s
        self.next_step_end_s = begin_s + 1
        self.events = {detector:{} for detector in DETECTORS}

    def add_step(self, step_end_s, detector_events):
        if step_end_s != self.next_step_end_s or set(detector_events) != set(DETECTORS):
            raise ValueError("missing, out-of-order, or wrong-detector E1 event step")
        normalized = {detector:[] for detector in DETECTORS}
        for detector in DETECTORS:
            seen = set()
            prior_active = {key for key,event in self.events[detector].items() if event[3] == -1}
            for item in detector_events[detector]:
                if len(item) != 5:
                    raise ValueError("invalid E1 vehicle data tuple")
                vehicle_id,length,entry,leave,type_id = item
                if (not isinstance(vehicle_id,str) or not vehicle_id or
                        not isinstance(type_id,str) or not type_id or
                        not all(math.isfinite(v) for v in (length,entry,leave)) or
                        length <= 0 or entry > step_end_s + 1e-6 or
                        (leave != -1 and (leave < entry or leave > step_end_s + 1e-6))):
                    raise ValueError("invalid E1 vehicle data values")
                key = (vehicle_id,entry)
                if key in seen:
                    raise ValueError("duplicate E1 vehicle event in one step")
                seen.add(key)
                previous = self.events[detector].get(key)
                if previous is not None:
                    if previous[1] != length or previous[4] != type_id:
                        raise ValueError("inconsistent E1 event metadata")
                    old_leave = previous[3]
                    if old_leave != -1 and abs(old_leave-leave) > 1e-6:
                        raise ValueError("conflicting completed E1 event")
                    if old_leave == -1 and leave != -1:
                        self.events[detector][key] = (vehicle_id,length,entry,leave,type_id)
                else:
                    self.events[detector][key] = (vehicle_id,length,entry,leave,type_id)
                normalized[detector].append((vehicle_id,length,entry,leave,type_id))
            if prior_active - seen:
                raise ValueError("ongoing E1 vehicle disappeared without completion event")
        self.next_step_end_s += 1
        return normalized

    def finish_window(self, end_s):
        if end_s != self.begin_s + 30 or self.next_step_end_s != end_s + 1:
            raise ValueError("incomplete 30-step E1 vehicle-event window")
        result = []
        for detector in DETECTORS:
            occupied_s = 0.0
            contributors = 0
            retained = {}
            for key,event in self.events[detector].items():
                _,_,entry,leave,_ = event
                segment = max(0.0,min(end_s,end_s if leave == -1 else leave)-max(self.begin_s,entry))
                if segment:
                    occupied_s += segment
                    contributors += 1
                if leave == -1 or leave > end_s:
                    retained[key] = event
            result.append((occupied_s / 30 * 100,contributors))
            self.events[detector] = retained
        self.begin_s = end_s
        return result
