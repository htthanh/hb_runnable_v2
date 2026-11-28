"""T2 (EXP-HB-004) - sinh mau (stopFr x stopTo) cho mot test_id. FILE NAY GIONG HET o 2 repo.

Chay o hb_runnable_v2; run_t2.sh COPY file sample sang hb_runnable (moi repo doc sample trong chinh no).
Chi load dfNdDetails_v2.pkl (khong can do thi) de lay allStops cua window.
Output: <repo>/myPy/tests_t2/out/<run_id>/sample_<test_id>.json
"""
import argparse
import os
import pickle

import t2_common as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--test-id', required=True, choices=C.TEST_IDS)
    ap.add_argument('--window', default='7,10')
    ap.add_argument('--n-stopfr', type=int, required=True)
    ap.add_argument('--n-stopto', type=int, required=True, help='<=0: toan bo allStops')
    ap.add_argument('--seed', type=int, required=True)
    a = ap.parse_args()

    out_dir = os.path.join(C.OUT_ROOT, a.run_id)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'sample_%s.json' % a.test_id)
    if os.path.exists(path):
        raise SystemExit('ERROR: %s da ton tai - khong ghi de' % path)

    window = C.parse_window(a.window)
    dfNd = pickle.load(open(os.path.join(C.PICKLES_DIR, 'dfNdDetails_v2.pkl'), 'rb'))
    stops = C.all_stops(dfNd, window)
    stopFr, stopTo = C.make_sample(stops, a.n_stopfr, a.n_stopto, a.seed)
    smp = {'experiment': 'EXP-HB-004', 'run_id': a.run_id, 'test_id': a.test_id, 'window': window,
           'seed': a.seed, 'n_stopfr': len(stopFr), 'n_stopto': len(stopTo),
           'all_stopto': not (a.n_stopto and a.n_stopto > 0), 'n_allstops': len(stops),
           'stopFr': stopFr, 'stopTo': stopTo}
    C.save_json(smp, path)
    print('[sample] %s %s seed=%d |stopFr|=%d |stopTo|=%d -> %s' %
          (a.run_id, a.test_id, a.seed, len(stopFr), len(stopTo), path))


if __name__ == '__main__':
    main()
