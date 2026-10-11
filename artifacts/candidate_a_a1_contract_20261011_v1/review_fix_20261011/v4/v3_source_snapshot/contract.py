"""Offline source subpredicates and conservative rejection diagnostics.

NOT a runtime guard. No SUMO, TraCI, production actuator or native movement.
The full A1 safety/coverage proof is unresolved; this helper cannot grant
ELIGIBLE from self-attested booleans, forged certificates or branch arithmetic.
"""
from enum import Enum
import math

SOURCE_COMMIT = 'fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3'
POSITION_EPS = 0.1   # pinned src/config.h.cmake:233, native numerical geometry
NUMERICAL_EPS = 0.001  # pinned src/config.h.cmake:230, not project clearance
# C++ guarantees int minimum width16; steps+1 must also fit. This is a
# portable source-arithmetic domain, NOT actual compiler width or safety limit.
CPP_PORTABLE_MAX_STEPS = 32766


class Decision(str, Enum):
    ELIGIBLE = 'ELIGIBLE'
    INELIGIBLE = 'INELIGIBLE'
    UNKNOWN = 'UNKNOWN'


def finite_number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def reliable(value, *, positive=False):
    """Reject unrepresentable scalar arithmetic, without a physical cutoff."""
    if not finite_number(value) or (positive and value <= 0):
        raise ValueError('non-finite or underflowed intermediate arithmetic')
    return value


def product(left, right):
    """Finite product; reject lost nonzero products due to underflow."""
    result=reliable(left*right)
    if result==0 and left!=0 and right!=0:
        raise ValueError('nonzero product underflowed to zero')
    return result


def brake_gap_euler(speed_m_s, decel_m_s2, step_s=1.0, headway_s=0.0):
    """MSCFModel.cpp:92-98 on a representable finite SI-domain."""
    if not all(finite_number(x) for x in (speed_m_s, decel_m_s2, step_s, headway_s)):
        raise ValueError('non-finite/missing numerical source input')
    if speed_m_s < 0 or decel_m_s2 <= 0 or step_s <= 0 or headway_s < 0:
        raise ValueError('outside Euler source subpredicate domain')
    try:
        reduction = reliable(product(decel_m_s2,step_s),positive=True)
        quotient = reliable(speed_m_s / reduction)
        count = int(quotient)  # Python truncation is safe before native-domain check
        if count > CPP_PORTABLE_MAX_STEPS:
            raise ValueError('native int conversion/steps+1 outside guaranteed domain')
        first = reliable(count * speed_m_s)
        second = reliable(reduction * count * (count + 1) / 2)
        discrete = product(step_s,reliable(first-second))
        response = product(speed_m_s,headway_s)
        return reliable(discrete + response)
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError('unrepresentable Euler brake arithmetic') from exc


def local_plan_stop(speed, seen, lane_offset, decel, emergency_decel,
                    yellow_min_decel, jm_stopline_gap, step_s=1.0):
    """Conditional local MSVehicle.cpp:2738-2776 arithmetic ONLY.

    seen must be the native planned distance to this exact link, NOT an
    assumed coordinate. No driver/GLOSA/newStopDist/device/rail overrides.
    Return does not select the full native branch or determine final speed.
    """
    vals=(speed, seen, lane_offset, decel, emergency_decel, yellow_min_decel,
          jm_stopline_gap, step_s)
    if not all(finite_number(v) for v in vals):
        raise ValueError('invalid source inputs')
    if (speed < 0 or seen < 0 or lane_offset < 0 or decel <= 0
            or emergency_decel < decel or yellow_min_decel <= 0
            or jm_stopline_gap < 0 or step_s <= 0):
        raise ValueError('unsupported pinned passenger stopping domain')
    stop_decel=max(min(yellow_min_decel, emergency_decel), decel)
    distance=brake_gap_euler(speed, stop_decel, step_s)
    can_lane=seen >= distance
    can_line=seen - lane_offset >= distance
    offset=max(jm_stopline_gap, lane_offset)
    if can_lane:
        offset=min(offset, seen-distance)
    offset=max(POSITION_EPS, offset)
    return {'stop_decel_m_s2':stop_decel,'brake_gap_m':distance,
            'can_brake_before_lane_end':can_lane,
            'can_brake_before_stopline':can_line,
            'native_adjusted_stop_offset_m':offset,
            'native_stop_dist_m':max(0.0,seen-offset),
            'full_branch_selected':None,'next_speed_m_s':None}


def maximum_safe_stop_speed_euler(gap, decel, step_s=1.0, headway_s=1.0):
    """MSCFModel.cpp:849-871 scalar subformula, NOT finalized vehicle speed.

    Driver perception/emergency wrappers are not recreated. Unrepresentable
    intermediate calculations fail closed; no physical cutoff is introduced.
    """
    if not all(finite_number(v) for v in (gap,decel,step_s,headway_s)):
        raise ValueError('invalid stopping formula input')
    if gap<0 or decel<=0 or step_s<=0 or headway_s<=0:
        raise ValueError('outside supported source subformula domain')
    try:
        g=reliable(gap-NUMERICAL_EPS)
        if g<0:
            return 0.0
        b=reliable(product(decel,step_s),positive=True); t=headway_s; s=step_s
        ratio=reliable(reliable(2*g)/b)
        scaled=reliable(s*reliable(ratio-t))
        square_t=reliable(product(t,t),positive=True)
        square_s=reliable(product(s,s),positive=True)
        discriminant=reliable(square_s+reliable(4*reliable(scaled+square_t)))
        if discriminant<0:
            raise ValueError('invalid scalar square-root arithmetic')
        root=reliable(math.sqrt(discriminant))
        n=math.floor(reliable(0.5-reliable((t-0.5*root)/s)))
        h=reliable(reliable(0.5*n*(n-1)*b*s)+reliable(n*b*t))
        denominator=reliable(n*s+t,positive=True)
        residual=reliable((g-h)/denominator)
        return reliable(reliable(n*b)+residual)
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError('unrepresentable scalar stop-speed arithmetic') from exc


def execute_yellow_can_brake(speed, dpi_distance, decel, step_s=1.0):
    """Different strict/equality predicate, MSVehicle.cpp:3714-3716."""
    if not finite_number(dpi_distance) or dpi_distance < 0:
        raise ValueError('invalid native DriveProcessItem distance')
    distance=brake_gap_euler(speed,decel,step_s)
    return dpi_distance > distance or speed < decel * step_s


def old_guard(speed, gap, decel):
    """Historical formula replay, never used as an A1 replacement."""
    if not all(finite_number(v) for v in (speed,gap,decel)) or speed < 0 or gap < 0 or decel <= 0:
        raise ValueError('invalid old guard replay input')
    try:
        required=0.0 if speed==0.0 else reliable(1.1+speed+reliable(speed*speed)/(2*decel))
        return {'required_m':required,'margin_m':reliable(gap-required),'safe':gap+1e-9>=required}
    except (OverflowError,ZeroDivisionError) as exc:
        raise ValueError('unrepresentable historical guard arithmetic') from exc


def one_step_excluded(distance_to_link_m, max_speed_m_s, max_accel_m_s2, step_s=1.0):
    """Conservative kinematic bound only if external source/type/modes bind it.

    Euler upper bound assumes no command/device raises speed/accel beyond
    these bounds, unambiguous front distance and one unchanged 1 s step.
    Strict greater-than avoids an unproved boundary/contact exclusion.
    """
    if not all(finite_number(v) for v in (distance_to_link_m,max_speed_m_s,max_accel_m_s2,step_s)):
        raise ValueError('unknown reachability bound')
    if distance_to_link_m<0 or max_speed_m_s<0 or max_accel_m_s2<0 or step_s<=0:
        raise ValueError('invalid reachability bound')
    try:
        bound=product(reliable(max_speed_m_s+product(max_accel_m_s2,step_s)),step_s)
        return distance_to_link_m > bound
    except OverflowError as exc:
        raise ValueError('unrepresentable reachability arithmetic') from exc


def diagnostic_decision(state):
    """Classify demonstrable local blockers; UNKNOWN otherwise.

    Schema uses direct measurements, not proof-complete/safe booleans.
    No ELIGIBLE path exists because global native-speed/coverage proofs are
    absent. This is intentionally NOT_IMPLEMENTABLE_YET as a runtime gate.
    INELIGIBLE denotes a conservative policy prohibition, not proven danger.
    """
    unknown=[];deny=[]
    if not isinstance(state,dict) or state.get('schema')!='A1_LOCAL_DIAGNOSTIC_V1':
        return {'decision':Decision.UNKNOWN.value,'reasons':['SCHEMA_UNBOUND']}
    if state.get('source_commit')!=SOURCE_COMMIT:
        unknown.append('SOURCE_UNBOUND')
    numeric=['time_s','measurement_time_s','next_switch_s','step_s']
    if any(not finite_number(state.get(k)) for k in numeric):
        unknown.append('TIME_MISSING_OR_NONFINITE')
    elif (state['time_s']!=state['measurement_time_s'] or state['next_switch_s']!=state['time_s']
          or state['step_s']!=1.0):
        unknown.append('TIME_OR_EVENT_MISMATCH')
    if state.get('phase_before')!=1 or state.get('state_before')!='y' or state.get('motion_state')!='r':
        unknown.append('PHASE_MISMATCH')
    if state.get('program')!='CA_C24' or state.get('controlled_link')!=['ramp_storage_0','ramp_accel_0',':ramp_mid_0_0']:
        unknown.append('PROGRAM_OR_LINK_MISMATCH')
    rows=state.get('vehicles')
    if not isinstance(rows,list):
        return {'decision':Decision.UNKNOWN.value,'reasons':unknown+['VEHICLE_ENUMERATION_MISSING']}
    ids=[]
    for row in rows:
        if not isinstance(row,dict):
            unknown.append('VEHICLE_SCHEMA_MISSING');continue
        vid=row.get('vehicle_id')
        if not isinstance(vid,str) or not vid:
            unknown.append('VEHICLE_ID_MISSING');continue
        ids.append(vid)
        if row.get('role') not in ['front','follower','ingress','receiver']:
            unknown.append('ROLE_UNBOUND')
        if row.get('type_id')!='technical_passenger' or row.get('model')!='Krauss':
            unknown.append('TYPE_OR_MODEL_UNBOUND')
        for mode,expected in [('speed_mode',31),('lane_change_mode',1621)]:
            if type(row.get(mode)) is not int:
                unknown.append('MODE_MISSING')
            elif row[mode]!=expected:
                deny.append('MODE_OUTSIDE_PINNED_CONTRACT')
        keys=['speed_m_s','seen_m','lane_offset_m','decel_m_s2','emergency_decel_m_s2',
              'yellow_min_decel_m_s2','jm_stopline_gap_m','action_step_s','tau_s']
        if any(not finite_number(row.get(k)) for k in keys):
            unknown.append('VEHICLE_INPUT_MISSING_OR_NONFINITE');continue
        if row['action_step_s']!=1.0 or row['tau_s']!=1.0:
            deny.append('DYNAMICS_OUTSIDE_PINNED_CONTRACT');continue
        try:
            p=local_plan_stop(row['speed_m_s'],row['seen_m'],row['lane_offset_m'],
                              row['decel_m_s2'],row['emergency_decel_m_s2'],
                              row['yellow_min_decel_m_s2'],row['jm_stopline_gap_m'])
        except (ValueError,OverflowError,ZeroDivisionError):
            unknown.append('VEHICLE_INPUT_OUTSIDE_DOMAIN');continue
        # The pure local arithmetic is trusted only inside this supplied diagnostic schema;
        # real native seen/offset binding remains an external unresolved obligation.
        if row['role']!='receiver' and not p['can_brake_before_stopline']:
            deny.append('COMMITTED_APPROACH_NOT_ADMITTED')
        if row['role']!='receiver' and row['seen_m']<row['lane_offset_m']:
            deny.append('BEYOND_STOPLINE_NOT_ADMITTED')
    if len(set(ids))!=len(ids):
        unknown.append('DUPLICATE_VEHICLE_ID')
    inventory=state.get('affected_inventory_ids')
    if (not isinstance(inventory,list) or any(not isinstance(v,str) for v in inventory)
            or len(set(inventory))!=len(inventory) or set(ids)!=set(inventory)):
        unknown.append('UNENUMERATED_OR_INCONSISTENT_INVENTORY')
    receiver=state.get('receiver')
    if not isinstance(receiver,dict):
        unknown.append('RECEIVER_MISSING')
    else:
        for key in ['rear_clearance_m','vehicle_length_m','min_gap_m']:
            if not finite_number(receiver.get(key)):
                unknown.append('RECEIVER_INPUT_MISSING')
        if all(finite_number(receiver.get(k)) for k in ['rear_clearance_m','vehicle_length_m','min_gap_m']):
            if receiver['vehicle_length_m']<=0 or receiver['min_gap_m']<0 or receiver['rear_clearance_m']<0:
                unknown.append('RECEIVER_INVALID')
            else:
                try:
                    required=reliable(receiver['vehicle_length_m']+receiver['min_gap_m'])
                    if receiver['rear_clearance_m']<required:
                        deny.append('RECEIVER_BLOCKED')
                except (ValueError,OverflowError):
                    unknown.append('RECEIVER_ARITHMETIC_UNREPRESENTABLE')
    if state.get('observed_red_crossing_ids'):
        deny.append('OBSERVED_RED_ANOMALY')
    # An inconsistent diagnostic snapshot cannot be used even for a binding denial.
    if unknown:
        return {'decision':Decision.UNKNOWN.value,'reasons':sorted(set(unknown+deny))}
    if deny:
        return {'decision':Decision.INELIGIBLE.value,'reasons':sorted(set(deny))}
    return {'decision':Decision.UNKNOWN.value,'reasons':['UNPROVEN_NATIVE_SPEED_AND_GLOBAL_COVERAGE',
            'RECEIVER_LEADER_FOLLOWER_FOE_AND_RANDOM_BOUNDS_UNRESOLVED'],
            'eligible_path_implemented':False}
