"""Small synthetic normalized certificates, not traffic/native observations."""
import unittest
from copy import deepcopy
from scripts.actuator_acceptance_20261015_v1.accuracy import evaluate, SUPPORTS, OPPORTUNITY, SCHEMA, LOCAL_DOMAIN

REF = {'path':'synthetic_fixture_projection', 'sha256':'a'*64}


def fixture():
    rows=[]
    for a,b in SUPPORTS:
        rows.append(dict(begin_s=a,end_s=b,observed_seconds=b-a,partial=False,
            C='25',N=25,E_scheduled=24,E_executed=24,C_selected='25',C_applied='25',
            measurement_source=deepcopy(REF), pending=[], application_delays=[],
            event_support='COMPLETIONS_A_LT_END_LE_B_ENTRIES_A_LE_BEGIN_LT_B',
            opportunity=dict(definition=OPPORTUNITY,source=deepcopy(REF),domain='LOCAL_STORAGE_20M_AND_DOWNSTREAM_BOUNDARY',
                supply_covered_seconds=b-a,receiver_covered_seconds=b-a,minimum_ordered_R_count=2, geometry_source=deepcopy(REF),receiver_geometry_source=deepcopy(REF),receiver_lane_ids=['synthetic_bound_receiver'],
                lane_domains=deepcopy(LOCAL_DOMAIN),count_basis='ACTUAL_R_FRONTS_IN_FIXED_DOMAIN_PER_1S',
                classification_unknown=False, external_blockers=[])))
    rows[-1].update(C='300',N=300,E_scheduled=300,E_executed=300,C_selected='300',C_applied='300')
    return dict(schema=SCHEMA, identity=dict(run_id='SYNTHETIC_NOT_NATIVE',card_sha256='a'*64,
        execution_source_sha256='a'*64,raw_manifest_sha256='a'*64,normalized_projection_sha256='a'*64,
        preregistration_sha256='a'*64,network_sha256='a'*64),preregistration=dict(opportunity_definition=OPPORTUNITY,source=deepcopy(REF),
            opportunity_geometry=dict(source=deepcopy(REF),receiver_domain_source=deepcopy(REF),receiver_lane_ids=['synthetic_bound_receiver'],network_sha256='a'*64,lane_domains=deepcopy(rows[0]['opportunity']['lane_domains']))),
        measurement_status='INDEPENDENT_NORMALIZED_PROJECTION_VALIDATED',safety_status='NOT_TESTED_SYNTHETIC',windows=rows)


class AccuracyTests(unittest.TestCase):
    def test_boundary_and_real_failure_without_cancellation(self):
        d=fixture(); d['windows'][0]['N']=23
        r=evaluate(d);self.assertEqual(r['conditional_accuracy'],'ACCEPTED_ON_OBSERVED_OPPORTUNITY')
        self.assertEqual(r['safety_status'],'NOT_TESTED_SYNTHETIC')
        self.assertEqual(r['qualification'],'NO_QUALIFICATION_VERDICT')
        d['windows'][0]['N']=22;d['windows'][1]['N']=28
        r=evaluate(d);self.assertEqual(r['eligible_aggregate']['signed_error_vehicles'],'0')
        self.assertEqual(r['conditional_accuracy'],'NOT_ACCEPTABLE_ACCURACY')
        d['windows'][1]['N']=22
        self.assertTrue(evaluate(d)['persistent_underdischarge'])

    def test_supply_shortage_keeps_raw_error_without_fault(self):
        d=fixture()
        for w in d['windows']:
            w['opportunity']['minimum_ordered_R_count']=0;w['N']=0
        r=evaluate(d);self.assertEqual(r['conditional_accuracy'],'NOT_TESTED')
        self.assertEqual(r['windows'][0]['raw_target'],'NOT_MET')
        self.assertEqual(r['windows'][0]['signed_error_vehicles'],'25')
        self.assertEqual(r['fixed_evaluation_union']['signed_error_vehicles'],'150')
        self.assertEqual(r['fixed_evaluation_union']['raw_target'],'NOT_MET')
        self.assertEqual(r['windows'][0]['opportunity'],'BACKLOG_OPPORTUNITY_NOT_ESTABLISHED')
        self.assertTrue(r['raw_persistent_underdischarge_any_adjacent_windows'])

    def test_policy_blockage_cannot_exclude_bad_service(self):
        d=fixture();w=d['windows'][0];w['N']=20
        w['opportunity']['available']=False
        w['opportunity']['external_blockers']=[dict(vehicle_id='prior_release',lane_id='internal',route_connection='same_route',source=deepcopy(REF),policy_independent=False)]
        r=evaluate(d);self.assertEqual(r['windows'][0]['opportunity'],'POLICY_COUPLED_OPPORTUNITY')
        self.assertEqual(r['conditional_accuracy'],'NOT_ACCEPTABLE_ACCURACY')
        w['opportunity']['external_blockers'][0]['policy_independent']=True
        self.assertEqual(evaluate(d)['windows'][0]['opportunity'],'UNKNOWN')
        w['opportunity']={'available':True}
        self.assertNotEqual(evaluate(d)['conditional_accuracy'],'ACCEPTED_ON_OBSERVED_OPPORTUNITY')

    def test_unknown_partial_missing_and_identity_do_not_pass(self):
        for mutation in ('identity','coverage','partial','missing','duplicate'):
            with self.subTest(mutation=mutation):
                d=fixture()
                if mutation=='identity':del d['identity']['raw_manifest_sha256']
                if mutation=='coverage':d['windows'][0]['opportunity']['receiver_covered_seconds']=299
                if mutation=='partial':d['windows'][0]['observed_seconds']=62;d['windows'][0]['partial']=True
                if mutation=='missing':d['windows'].pop()
                if mutation=='duplicate':d['windows'].append(deepcopy(d['windows'][0]))
                r=evaluate(d)
                if mutation=='coverage':self.assertEqual(r['windows'][0]['conditional_accuracy'],'NOT_TESTED')
                self.assertNotEqual(r['conditional_accuracy'],'ACCEPTED_ON_OBSERVED_OPPORTUNITY')
                self.assertEqual(len(r['windows']),len(d['windows']))

    def test_small_denominators_and_nonadjacent_coverage(self):
        d=fixture()
        for w in d['windows']:w['C']='0';w['N']=0
        r=evaluate(d);self.assertIsNone(r['windows'][0]['relative_error'])
        self.assertEqual(r['conditional_accuracy'],'NOT_TESTED')
        d=fixture()
        for i,w in enumerate(d['windows']):
            if i in (1,3,5):w['opportunity']['minimum_ordered_R_count']=0
        r=evaluate(d);self.assertFalse(r['minimum_opportunity_coverage_met'])
        self.assertEqual(r['conditional_accuracy'],'NOT_TESTED')

    def test_unreached_pending_and_decomposition(self):
        d=fixture();w=d['windows'][5]
        w.update(observed_seconds=0,partial=True,C=None,N=None,E_scheduled=None,E_executed=None,C_selected=None,C_applied=None)
        d['windows'][0]['pending']=[dict(request_id='latest',status='PENDING')]
        d['windows'][0]['application_delays']=[dict(request_id='older',delay_s=24,source=deepcopy(REF))]
        r=evaluate(d);self.assertEqual(r['windows'][5]['measurement'],'NOT_REACHED')
        self.assertEqual(r['windows'][0]['input']['pending'],d['windows'][0]['pending'])
        self.assertTrue(r['windows'][0]['decomposition']['sum_equals_C_minus_N'])
        self.assertEqual(r['conditional_accuracy'],'NOT_TESTED')


if __name__=='__main__':unittest.main()
