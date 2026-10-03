"""Pure/static S1 checks; no SUMO or TraCI session is started."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "scripts/stage6/standard_metering_20261003"
sys.path.insert(0, str(SOURCE))
from control import (Feedback, FeedbackParameters, PulseScheduler, assess_storage_safety,
                     classify_service_window, front_at_stopline)

spec = importlib.util.spec_from_file_location("standard_metering_runner", SOURCE / "runner.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.feedback = Feedback(FeedbackParameters(**runner.PARAMETERS))

    def test_direction_units_clip_no_windup(self):
        first = self.feedback.update(630,600,630,14,14)
        self.assertEqual(first["rate_clipped_veh_h"],690)
        self.assertEqual(first["occ_mean_pct"],14)
        for t in range(660,930,30):
            self.feedback.update(t,t-30,t,100,100)
        self.assertEqual(self.feedback.rate,300)
        recovery=self.feedback.update(930,900,930,10,10)
        self.assertEqual(recovery["rate_raw_veh_h"],370)
        self.assertEqual(self.feedback.rate,370)

    def test_invalid_time_and_occupancy_fail_closed(self):
        for args in ((630,570,600,11,11),(660,630,660,11,11),
                     (630,600,630,float("nan"),11),(630,600,630,-1,11)):
            with self.assertRaises(ValueError):self.feedback.update(*args)
        self.assertEqual(self.feedback.rate,900)

    def test_119_updates_and_no_4200_command(self):
        for t in range(630,4171,30):
            row=self.feedback.update(t,t-30,t,11,11)
            self.assertEqual((row["interval_begin_s"],row["interval_end_s"]),(t-30,t))
        self.assertEqual(self.feedback.last_update,4170)
        with self.assertRaises(ValueError):self.feedback.update(4200,4170,4200,11,11)

    def test_event_ledger_cross_step_early_exit_and_duplicate(self):
        ledger=runner.DetectorEventLedger()
        for end in range(601,631):
            events={d:[] for d in runner.DETECTORS}
            if end==601:events[runner.DETECTORS[0]]=[("cross",5,600.75,-1,"car")]
            if end==602:events[runner.DETECTORS[0]]=[("cross",5,600.75,601.25,"car")]
            if end==611:events[runner.DETECTORS[1]]=[("early",5,610.2,610.7,"car")]
            if end in (612,613):events[runner.DETECTORS[1]]=[("repeat",5,611.8,612.0,"car")]
            ledger.add_step(end,events)
        (l0,n0),(l1,n1)=ledger.finish_window(630)
        self.assertAlmostEqual(l0,0.5/30*100)
        self.assertAlmostEqual(l1,0.7/30*100)
        self.assertEqual((n0,n1),(1,2))

    def test_event_ledger_carries_ongoing_across_thirty_second_reset(self):
        ledger=runner.DetectorEventLedger()
        for end in range(601,631):
            events={d:[] for d in runner.DETECTORS}
            if end==630:events[runner.DETECTORS[0]]=[("boundary",5,629.5,-1,"car")]
            ledger.add_step(end,events)
        self.assertAlmostEqual(ledger.finish_window(630)[0][0],0.5/30*100)
        for end in range(631,661):
            events={d:[] for d in runner.DETECTORS}
            if end==631:events[runner.DETECTORS[0]]=[("boundary",5,629.5,630.4,"car")]
            ledger.add_step(end,events)
        self.assertAlmostEqual(ledger.finish_window(660)[0][0],0.4/30*100)
        self.assertEqual(ledger.events[runner.DETECTORS[0]],{})

    def test_event_ledger_sums_overlaps_without_capping_and_clips_boundaries(self):
        ledger=runner.DetectorEventLedger()
        for end in range(601,631):
            events={d:[] for d in runner.DETECTORS}
            events[runner.DETECTORS[0]]=[("a",5,600,-1,"car"),("b",5,600,-1,"car")]
            if end==601:events[runner.DETECTORS[1]]=[("old",5,599.5,600,"car")]
            if end==630:events[runner.DETECTORS[1]]=[("new",5,630,-1,"car")]
            ledger.add_step(end,events)
        (l0,n0),(l1,n1)=ledger.finish_window(630)
        self.assertEqual((l0,n0),(200,2))
        self.assertEqual((l1,n1),(0,0))

    def test_event_ledger_rejects_missing_step_disappearing_and_conflict(self):
        ledger=runner.DetectorEventLedger()
        with self.assertRaises(ValueError):ledger.finish_window(630)
        with self.assertRaises(ValueError):ledger.add_step(602,{d:[] for d in runner.DETECTORS})
        ledger.add_step(601,{runner.DETECTORS[0]:[("a",5,600.2,-1,"car")],runner.DETECTORS[1]:[]})
        with self.assertRaises(ValueError):ledger.add_step(602,{d:[] for d in runner.DETECTORS})
        ledger=runner.DetectorEventLedger()
        ledger.add_step(601,{runner.DETECTORS[0]:[("a",5,600.2,600.8,"car")],runner.DETECTORS[1]:[]})
        with self.assertRaises(ValueError):ledger.add_step(602,{runner.DETECTORS[0]:[("a",5,600.2,601.1,"car")],runner.DETECTORS[1]:[]})
        with self.assertRaises(ValueError):runner.DetectorEventLedger().add_step(601,
            {runner.DETECTORS[0]:[("a",5,600.2,float("nan"),"car")],runner.DETECTORS[1]:[]})


class PulseTests(unittest.TestCase):
    def test_first_slot_and_minimum_red(self):
        schedule=PulseScheduler()
        rows=[schedule.step(t,900) for t in range(600,630)]
        self.assertEqual([600+i for i,x in enumerate(rows) if x["slot_scheduled"]][0],603)
        self.assertEqual([x["requested_state"] for x in rows[:4]],["r","r","r","G"])
        for t in range(630,660):rows.append(schedule.step(t,1200))
        slots=[600+i for i,x in enumerate(rows) if x["slot_scheduled"]]
        self.assertTrue(all(b-a>=3 for a,b in zip(slots,slots[1:])))
        self.assertLessEqual(schedule.credit,1)

    def test_credit_continues_at_rate_update_and_empty_slots_do_not_accumulate(self):
        schedule=PulseScheduler()
        for t in range(600,630):schedule.step(t,900)
        before=schedule.credit
        after=schedule.step(630,300)
        self.assertAlmostEqual(after["credit_after"],before+300/3600,places=9)
        for t in range(631,4200):schedule.step(t,300)
        self.assertLessEqual(schedule.credit,1)
        with self.assertRaises(ValueError):schedule.step(4200,300)

    def test_safety_reject_defers_one_credit_without_burst(self):
        schedule=PulseScheduler()
        rows=[schedule.step(t,1200,False) for t in range(600,610)]
        self.assertEqual([600+i for i,x in enumerate(rows) if x["nominal_slot_scheduled"]],
                         list(range(602,610)))
        self.assertTrue(all(not x["slot_scheduled"] and x["credit_after"]<=1 for x in rows))
        self.assertGreater(schedule.dropped_credit,0)
        rows += [schedule.step(t,1200,True) for t in range(610,617)]
        self.assertEqual([600+i for i,x in enumerate(rows) if x["slot_scheduled"]],[610,613,616])
        self.assertTrue(all(b-a>=3 for a,b in zip([610,613,616],[613,616])))

    def test_storage_guard_stopped_front_and_all_followers(self):
        states={"front":(204.0,0.0,"car"),"safe":(175.0,4.0,"car")}
        params={"car":2.6}; braking={"car":4.5}
        allowed=assess_storage_safety(states,"front",True,204.49,params,braking)
        self.assertEqual((allowed["allowed"],allowed["reason"]),(True,"ALLOW"))
        states["unsafe"]=(190.0,9.0,"car")
        rejected=assess_storage_safety(states,"front",True,204.49,params,braking)
        self.assertEqual((rejected["allowed"],rejected["reason"]),
                         (False,"FOLLOWER_STOP_DISTANCE"))
        self.assertEqual(rejected["unsafe_follower_ids"],["unsafe"])
        self.assertAlmostEqual(next(x["required_stop_gap_m"] for x in rejected["vehicle_states"]
                                    if x["vehicle_id"]=="unsafe"),
                               1.1+11.6+11.6**2/9)
        self.assertEqual(assess_storage_safety(states,"front",False,204.49,params,braking)["reason"],
                         "FRONT_OR_RECEIVER_NOT_READY")
        self.assertEqual(assess_storage_safety({},"",False,204.49,params,braking)["reason"],
                         "NO_FRONT")

    def test_service_gate(self):
        self.assertEqual(classify_service_window(queued_unblocked_slots=19,crossings_in_slots=19,
                         red_crossings=0,repeated_slots=0),"NOT_SUFFICIENTLY_TESTED")
        self.assertEqual(classify_service_window(queued_unblocked_slots=20,crossings_in_slots=18,
                         red_crossings=0,repeated_slots=0),"PASS_TECHNICAL_SERVICE")
        self.assertEqual(classify_service_window(queued_unblocked_slots=20,crossings_in_slots=17,
                         red_crossings=0,repeated_slots=0),"FAIL_SATURATED_SERVICE")
        self.assertEqual(classify_service_window(queued_unblocked_slots=20,crossings_in_slots=20,
                         red_crossings=1,repeated_slots=0),"FAIL_RED_MULTIPLE_OR_WRONG_VEHICLE")

    def test_only_true_front_qualifies(self):
        front,ready,_,_=front_at_stopline({"fast_front":(204.2,5,5,2.5),
                                          "slow_follower":(203.9,0,5,2.5)}, {},204.49)
        self.assertEqual((front,ready),("fast_front",False))
        front,ready,_,_=front_at_stopline({"queued_front":(204.15,0,5,2.5),
                                          "follower":(197,0,5,2.5)}, {},204.49)
        self.assertEqual((front,ready),("queued_front",True))
        _,ready,clearance,required=front_at_stopline({"queued_front":(204.15,0,5,2.5)},
                                                      {"downstream":(10,5)},204.49)
        self.assertFalse(ready)
        self.assertEqual((clearance,required),(5,7.5))
        self.assertEqual(front_at_stopline({}, {},204.49)[:2],("",False))


class StaticCardTests(unittest.TestCase):
    def test_actual_single_link(self):
        self.assertAlmostEqual(runner.assert_network_controlled_link(),204.49,places=2)

    def test_d016_budget_keeps_physical_and_charges_only_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            old=root/"old"; new=root/"new"
            (old/"reservations").mkdir(parents=True)
            (new/"reservations").mkdir(parents=True)
            for index in range(18):(old/"reservations"/f"old{index}.json").write_text("{}")
            for run_id,mode in (("technical","NOOP"),("controlled","ALINEA")):
                package=new/run_id;package.mkdir()
                (package/"card.json").write_text(json.dumps({"run_id":run_id,"mode":mode}))
                (new/"reservations"/f"{run_id}.json").write_text(json.dumps(
                    {"run_id":run_id,"card_sha256":runner.sha(package/"card.json")}))
            with patch.object(runner,"BASE_PACKAGES",old),patch.object(runner,"PACKAGES",new):
                snapshot=runner.budget_snapshot()
            self.assertEqual((snapshot["physical_starts"],snapshot["technical_starts"],
                              snapshot["experiment_starts"],snapshot["new_experiment_starts"]),
                             (20,1,19,1))

    def test_d016_explicit_technical_alinea_does_not_erase_old_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);old=root/"old";new=root/"new"
            (old/"reservations").mkdir(parents=True)
            (new/"reservations").mkdir(parents=True)
            for index in range(18):(old/"reservations"/f"old{index}.json").write_text("{}")
            for run_id,purpose,technical in (("oldcontrol","EXPLORATORY_COMPARISON",False),
                                             ("repair","TECHNICAL_ACTUATOR_REPAIR_VALIDATION",True)):
                package=new/run_id;package.mkdir()
                card={"run_id":run_id,"mode":"ALINEA","purpose":purpose,
                      "budget_accounting":{"policy":"D-016","technical_start":technical,
                                           "experiment_start":not technical}}
                (package/"card.json").write_text(json.dumps(card))
                (new/"reservations"/f"{run_id}.json").write_text(json.dumps(
                    {"run_id":run_id,"card_sha256":runner.sha(package/"card.json")}))
            with patch.object(runner,"BASE_PACKAGES",old),patch.object(runner,"PACKAGES",new):
                snapshot=runner.budget_snapshot()
            self.assertEqual((snapshot["physical_starts"],snapshot["technical_starts"],
                              snapshot["experiment_starts"],snapshot["new_experiment_starts"]),
                             (20,1,19,1))

    def test_preparation_has_no_raw_and_preserves_demand(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake=Path(tmp).resolve()
            with patch.object(runner,"PACKAGES",fake/"cards"),patch.object(runner,"RAW",fake/"raw"):
                with patch.object(runner,"budget_snapshot",return_value={"old_starts":18,"new_starts":0,
                          "global_starts":18,"physical_starts":18,"technical_starts":0,
                          "new_experiment_starts":0,"experiment_starts":18,
                          "old_raw_bytes":1,"new_raw_bytes":0,"shared_raw_bytes":1}):
                    result=runner.prepare("NOOP",17)
                    self.assertEqual(result["status"],"PREPARED_NO_SIMULATION")
                    self.assertFalse((fake/"raw").exists())
                    card=Path(result["card"])
                    self.assertEqual(runner.sha(card.parent/"demand.rou.xml"),
                                     runner.sha(runner.base_path(17)/"demand.rou.xml"))
                    checked=runner.preflight(card,result["card_sha256"])
                    self.assertEqual(checked["mode"],"NOOP")
                    self.assertEqual(checked["occupancy_sampling"],runner.OCCUPANCY_SAMPLING)
                    self.assertEqual(checked["startup_deadline_s"],60.0)
                    self.assertEqual(checked["budget_accounting"],
                                     {"policy":"D-016","technical_start":True,"experiment_start":False})

    def test_execution_receipt_uses_boundary_manifest_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp)
            (raw/"sample.xml").write_text("<sample/>")
            files={"sample.xml":{"sha256":runner.sha(raw/"sample.xml"),
                                 "bytes":(raw/"sample.xml").stat().st_size}}
            child=type("Child",(),{"returncode":0,"pid":123})()
            receipt=runner.build_receipt(card={"run_id":"UNIT_TEST"},approved_hash="a"*64,
                release_sha="b"*64,started="2026-10-03T00:00:00Z",wall_s=1,
                child=child,reason=None,failure=None,files=files,budget_after={})
            self.assertEqual(receipt["status"],"COMPLETED")
            self.assertEqual(receipt["output_manifest"],files)
            self.assertEqual(receipt["output_bytes"],len("<sample/>"))
            runner.write_json_exclusive(raw/"execution_receipt.json",receipt)
            boundary_source=SOURCE.parent/"boundary_search_20261002"/"analyze.py"
            analyzer_spec=importlib.util.spec_from_file_location("boundary_analyze_for_contract",boundary_source)
            analyzer=importlib.util.module_from_spec(analyzer_spec)
            analyzer_spec.loader.exec_module(analyzer)
            self.assertEqual(analyzer.validate_receipt(raw)["run_id"],"UNIT_TEST")

    def test_traci_startup_passes_child_and_localhost_without_sumo(self):
        class FakeTraCI:
            def __init__(self):self.called=None
            def connect(self,**kwargs):
                self.called=kwargs
                return "MOCK_CONNECTION"
        fake=FakeTraCI();child=type("Child",(),{"poll":lambda self:None})()
        records=[]
        self.assertEqual(runner.connect_traci(fake,55555,child,records.append,enforce_alarm=False),"MOCK_CONNECTION")
        self.assertEqual(fake.called,{"port":55555,"host":"localhost","proc":child,
                                      "numRetries":0,"waitBetweenRetries":0})
        self.assertEqual(records[0]["outcome"],"CONNECTED")

    def test_traci_startup_delayed_ready_early_exit_and_timeout(self):
        class FatalTraCIError(Exception):pass
        class Clock:
            def __init__(self):self.value=0.0
            def now(self):return self.value
            def sleep(self,n):self.value+=n
        class Child:
            def __init__(self):self.code=None
            def poll(self):return self.code

        clock=Clock();child=Child();records=[]
        class Delayed:
            def __init__(self):self.attempts=0
            def connect(self,**kwargs):
                self.attempts+=1
                if self.attempts<=150:raise FatalTraCIError("refused")
                return "READY"
        delayed=Delayed()
        self.assertEqual(runner.connect_traci(delayed,55555,child,records.append,
                clock=clock.now,sleeper=clock.sleep,enforce_alarm=False),"READY")
        self.assertGreaterEqual(clock.value,14.99)
        self.assertLess(clock.value,60)
        self.assertEqual(len(records),151)
        self.assertEqual(records[-1]["outcome"],"CONNECTED")

        clock=Clock();child=Child();records=[]
        class Early:
            attempts=0
            def connect(self,**kwargs):
                self.attempts+=1
                child.code=12
                raise FatalTraCIError("refused")
        early=Early()
        with self.assertRaisesRegex(RuntimeError,"SUMO exited during TraCI startup: 12"):
            runner.connect_traci(early,55555,child,records.append,
                                 clock=clock.now,sleeper=clock.sleep,enforce_alarm=False)
        self.assertEqual(early.attempts,1)
        self.assertEqual(records[0]["poll_after"],12)

        clock=Clock();child=Child();records=[]
        class Never:
            attempts=0
            def connect(self,**kwargs):
                self.attempts+=1
                raise FatalTraCIError("refused")
        never=Never()
        with self.assertRaisesRegex(TimeoutError,"startup deadline 60.0s"):
            runner.connect_traci(never,55555,child,records.append,
                                 clock=clock.now,sleeper=clock.sleep,enforce_alarm=False)
        self.assertGreater(never.attempts,150)
        self.assertLessEqual(clock.value,60.1)
        self.assertEqual(records[-1]["outcome"],"FAILED")

    def test_traci_blocking_handshake_obeys_independent_deadline(self):
        import time
        class Child:
            def poll(self):return None
        class Blocking:
            def connect(self,**kwargs):
                time.sleep(0.3)
                return "TOO_LATE"
        records=[]
        with self.assertRaisesRegex(TimeoutError,"expired during handshake"):
            runner.connect_traci(Blocking(),55555,Child(),records.append,deadline_s=0.05)
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]["error_type"],"TimeoutError")

    def test_passive_probes_are_fixed_and_never_connect_to_traci(self):
        calls=[]
        class Result:
            returncode=0;stdout="LISTEN test";stderr=""
        def fake_run(command,**kwargs):
            calls.append((command,kwargs))
            return Result()
        with tempfile.TemporaryDirectory() as tmp:
            evidence=runner.passive_startup_probe(1234,Path(tmp),6,
                deadline_at=runner.time.monotonic()+10,run=fake_run)
        self.assertEqual([x[0][0] for x in calls],["/usr/sbin/lsof","/bin/ps","/usr/bin/sample"])
        self.assertTrue(all(x[1]["timeout"]<=1.75 for x in calls))
        self.assertTrue(all("sumo" not in Path(x[0][0]).name.lower() for x in calls))
        self.assertEqual(evidence["pid"],1234)
        self.assertTrue(all("elapsed_since_start_s" in x for x in evidence["checks"].values()))
        done=set()
        self.assertEqual(runner.due_startup_probes({"outcome":"FAILED","elapsed_since_start_s":1.9},done),[])
        self.assertEqual(runner.due_startup_probes({"outcome":"FAILED","elapsed_since_start_s":2.0},done),[2])
        done.add(2)
        self.assertEqual(runner.due_startup_probes({"outcome":"FAILED","elapsed_since_start_s":6.0},done),[6])
        self.assertEqual(runner.due_startup_probes({"outcome":"CONNECTED","elapsed_since_start_s":6.0},done),[])

    def test_passive_probe_obeys_group_deadline(self):
        class Clock:
            value=6.0
            def now(self):return self.value
        clock=Clock()
        class Result:
            returncode=0;stdout="";stderr=""
        def slow_mock(command,**kwargs):
            clock.value+=kwargs["timeout"]
            return Result()
        with tempfile.TemporaryDirectory() as tmp:
            evidence=runner.passive_startup_probe(1234,Path(tmp),6,deadline_at=10,
                run=slow_mock,clock=clock.now)
        self.assertLessEqual(clock.value,10)
        self.assertEqual(list(evidence["checks"]),["tcp_listeners","process_state","stack_sample"])
        clock.value=9.5
        with tempfile.TemporaryDirectory() as tmp:
            evidence=runner.passive_startup_probe(1234,Path(tmp),6,deadline_at=10,
                run=slow_mock,clock=clock.now)
        self.assertLessEqual(clock.value,10)
        self.assertEqual(evidence["checks"]["stack_sample"]["status"],"SKIPPED_DEADLINE")


if __name__=="__main__":unittest.main()
