import unittest

from analyze_b import compare_core,cohort_rows,summarize_cohort


class BAnalysisTests(unittest.TestCase):
    def test_all_fixed_bins_and_speed_difference(self):
        a=[];b=[]
        for c in range(13,18):
            for t in range(0,2700,30):
                window='pre' if t<540 else 'active' if t<1500 else 'tail'
                base={'cell':c,'begin':t,'end':t+30,'window':window,'M_samples':10,
                      'M_mean_speed_mps':20.0,'M_mean_simultaneous_count':2.0,'M_density_veh_per_km':10.0}
                a.append(base)
                b.append({**base,'M_mean_speed_mps':22.0 if c==14 and window=='active' else 20.0,
                          'M_mean_simultaneous_count':1.0 if c==14 and window=='active' else 2.0})
        result=compare_core(a,b)
        self.assertEqual(len(result),450)
        target=next(r for r in result if r['cell']==14 and r['begin']==540)
        self.assertEqual(target['B_minus_A_speed_mps'],2.0)
        self.assertEqual(target['B_minus_A_mean_count'],-1.0)

    def test_incomplete_u_stays_in_complete_cohort(self):
        p={'vehicles':{'M_flow.0':{'depart':'0'},'U_flow.0':{'depart':'10'}}}
        trip={'A':{'M_flow.0':{'depart':'0','departDelay':'0','duration':'50','timeLoss':'5'},
                   'U_flow.0':{'depart':'10','departDelay':'0','duration':'40','timeLoss':'4'}},
              'B':{'M_flow.0':{'depart':'0','departDelay':'0','duration':'45','timeLoss':'3'}}}
        veh={'A':{'M_flow.0':{'arrival':'50'},'U_flow.0':{'arrival':'50'}},
             'B':{'M_flow.0':{'arrival':'45'}}}
        rows=cohort_rows(p,trip,veh)
        self.assertEqual(len(rows),4)
        bu=next(r for r in rows if r['arm']=='B' and r['class']=='U')
        self.assertIsNone(bu['actual_depart_s'])
        self.assertTrue(bu['unfinished_or_not_inserted'])
        summary=summarize_cohort(rows)
        bu_sum=next(r for r in summary if r['arm']=='B' and r['class']=='U')
        self.assertEqual(bu_sum['planned'],1)
        self.assertEqual(bu_sum['arrived'],0)
        self.assertFalse(bu_sum['complete_cohort_mean_available'])


if __name__=='__main__':unittest.main()
