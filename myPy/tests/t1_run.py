"""T1 - chay MOT bien the buoc 5 (v3 = P0 goc, v3p = P1, v4 = P2) tren mot mau (stopFr x stopTo) co dinh.

Goi TRUC TIEP ham goc trong ttgAnalysisMultip_v2 (procNumber=0, 1 process), khong qua main.py
va khong qua partition() (random.shuffle khong seed).

Output trong --out:
  shortestPaths_0.pkl  : list record y nhu pipeline ([stopFr, stopTo, timeFr, timeTo, path, flag])
  sample.json          : mau stopFr/stopTo, seed, window -> dung lai cho bien the khac va cho t1_compare
  meta.json            : bien the, thoi gian, max RSS, phien ban thu vien, may

Dung lai mau cua mot lan chay truoc: --sample <out_cu>/sample.json (dam bao v3 va v3p chay CUNG mau).
Luu y: so loi goi igraph (nSpCalls) cua v3p chi in ra stdout -> chay kem `| tee <out>/run.log`.
"""
import argparse
import os
import time

import common as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pickles', default=C.DEFAULT_PICKLES,
                    help='thu muc chua GttTransit_v2.pkl, dfNdDetails_v2.pkl, dfAllTransfers.pkl, stopPairsDist.pkl '
                         '(mac dinh: myPy/outputs/pickles cua runnable_v2; phai nam trong runnable_v2)')
    ap.add_argument('--variant', required=True, choices=['v3', 'v3p', 'v4'])
    ap.add_argument('--window', default='7,10', help="vd '7,10'")
    ap.add_argument('--n-stopfr', type=int, default=3)
    ap.add_argument('--n-stopto', type=int, default=200, help='<=0: toan bo allStops')
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--stopfr', default='', help='danh sach stopFr cu the, vd "12,345" (bo qua --n-stopfr)')
    ap.add_argument('--sample', default='', help='sample.json cua lan chay truoc (uu tien hon cac tham so mau)')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    C.require_inside(a.out, '--out')
    C.require_inside(a.pickles, '--pickles')
    if a.sample:
        C.require_inside(a.sample, '--sample')
    os.makedirs(a.out, exist_ok=True)
    if os.path.exists(os.path.join(a.out, 'shortestPaths_0.pkl')):
        raise SystemExit('ERROR: %s da co shortestPaths_0.pkl - chon --out khac de khong ghi de' % a.out)

    if a.sample:
        smp = C.load_json(a.sample)
        window = smp['window']
        if a.window and C.parse_window(a.window) != window:
            print('[warn] --window bi bo qua, dung window cua sample: %s' % window)
    else:
        smp = None
        window = C.parse_window(a.window)

    gtt, dfNd, spd, allStops = C.load_inputs(a.pickles, window)

    if smp:
        stopFrList, stopToList = smp['stopFr'], smp['stopTo']
        missing = set(stopToList) - set(int(s) for s in allStops)
        if missing:
            raise SystemExit('ERROR: %d stopTo trong sample khong co trong allStops' % len(missing))
    else:
        stopFrList, stopToList = C.make_sample(allStops, a.n_stopfr, a.n_stopto, a.seed,
                                               [s for s in a.stopfr.split(',') if s] or None)
        smp = {'window': window, 'seed': a.seed, 'n_stopfr': len(stopFrList),
               'n_stopto': len(stopToList), 'all_stopto': not (a.n_stopto and a.n_stopto > 0),
               'stopFr': stopFrList, 'stopTo': stopToList}
    C.save_json(smp, os.path.join(a.out, 'sample.json'))
    print('[T1] variant=%s window=%s stopFr=%s |stopTo|=%d' %
          (a.variant, window, stopFrList, len(stopToList)), flush=True)

    func = {'v3': C.ttg.calcShortestPathsSubset_v3, 'v3p': C.ttg.calcShortestPathsSubset_v3p,
            'v4': C.ttg.calcShortestPathsSubset_v4}[a.variant]
    t0 = time.perf_counter()
    func(gtt, stopFrList, stopToList, window, dfNd, spd, 0, a.out)
    elapsed = time.perf_counter() - t0

    meta = {'variant': a.variant, 'window': window, 'n_stopfr': len(stopFrList), 'n_stopto': len(stopToList),
            'elapsed_s': elapsed, 'elapsed_per_stopfr_s': elapsed / max(1, len(stopFrList)),
            'max_rss_mib': C.max_rss_mib(), 'env': C.env_info(), 'pickles': os.path.abspath(a.pickles),
            'finished': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    C.save_json(meta, os.path.join(a.out, 'meta.json'))
    print('[T1] done variant=%s elapsed=%.1f s (%.1f s/stopFr) maxRSS=%.0f MiB' %
          (a.variant, elapsed, meta['elapsed_per_stopfr_s'], meta['max_rss_mib']), flush=True)


if __name__ == '__main__':
    main()
