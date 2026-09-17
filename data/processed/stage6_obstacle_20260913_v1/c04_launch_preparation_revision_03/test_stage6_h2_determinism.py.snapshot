"""Offline Python-only serialization checks; no simulator process is used."""
import os
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = r'''
import os
import sys
from src.analysis import stage6_h2_measurement as m
from src.analysis import stage6_h2_pipeline as p
from src.scenarios import stage6_h2_offline as o
ids = {"M_flow.0", "M_flow.1", "M_flow.10", "M_flow.11"}
order = list(ids)
if os.environ["FIXTURE_ORDER"] == "reverse":
    order.reverse()
trajectories = {}
trips = {}
for vid in order:
    speed = 10 + int(vid.split(".")[1])
    trajectories[vid] = [m.Sample(t, "main_up_0", pos, speed)
                         for t, pos in ((300,100),(301,200),(302,500),(303,1199),(304,1200))]
    trips[vid] = {"depart":300, "arrival":305, "timeLoss":1, "duration":5}
observations = {"trajectories":trajectories, "tripinfo":trips,
                "regional_stops":m.regional_stops(trajectories,2700),
                "inlet":{"supported":True}, "analysis_qualification":"qualified",
                "tls_states":["GG"]*2700, "endpoints":{}}
common = {vid:[m.Sample(s.time,"main_down_0",pos,s.speed)
               for s,pos in zip(samples,(0,100,300,699,700))]
          for vid,samples in trajectories.items()}
result = {"common_background_cohort":m.domain_cohort(common,trips,"main_down",100,700),
          "feeder":m.feeder_science_inputs(observations),
          "companions":p.descriptive_companions(observations)}
for domain in (result["common_background_cohort"],result["feeder"]["cohort"]):
    assert [r["vehicle_id"] for r in domain["records"]] == sorted(ids)
sys.stdout.buffer.write(o.encode(result))
'''


class DeterminismTests(unittest.TestCase):
    def test_hashseeds_and_reversed_input_are_byte_identical(self):
        outputs = []
        for seed in ("1", "17", "23", "91"):
            for order in ("forward", "reverse"):
                with self.subTest(hashseed=seed, input_order=order):
                    environment = dict(os.environ, PYTHONHASHSEED=seed,
                                       PYTHONDONTWRITEBYTECODE="1", FIXTURE_ORDER=order)
                    result = subprocess.run([sys.executable, "-B", "-c", SCRIPT],
                                            cwd=Path(__file__).resolve().parents[1],
                                            env=environment, capture_output=True, timeout=20,
                                            check=True)
                    self.assertEqual(result.stderr, b"")
                    outputs.append(result.stdout)
                    self.assertEqual(outputs[0], outputs[-1])


if __name__ == "__main__":
    unittest.main()
