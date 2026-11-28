"""T2 (EXP-HB-004) - chay buoc 5 cua CHINH repo nay tren mot mau co dinh, 1 process.
FILE NAY GIONG HET o hb_runnable va hb_runnable_v2.

  hb_runnable    : chi cho phep --variant v3 (P0 = calcShortestPathsSubset_v3 cua code golden)
  hb_runnable_v2 : chi cho phep --variant v4 (P2 = calcShortestPathsSubset_v4)

Input : <repo>/myPy/outputs/pickles/ (4 pickle) va --sample (phai nam trong repo).
Output: <repo>/myPy/tests_t2/out/<run_id>/<test_id>_<P0|P2>_r<rep>/
        shortestPaths_0.pkl, manifest.json, run.log
"""
import argparse
import os
import sys
import time

import t2_common as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', required=True, help='vd T2-20261201 (cung mot gia tri cho ca 2 repo)')
    ap.add_argument('--test-id', required=True, choices=C.TEST_IDS)
    ap.add_argument('--variant', required=True, choices=['v3', 'v4'])
    ap.add_argument('--rep', type=int, default=1, help='lan lap (1, 2, 3, ...)')
    ap.add_argument('--sample', required=True, help='sample_<test_id>.json (nam trong repo nay)')
    a = ap.parse_args()

    ident = C.repo_identity()
    if C.REPO_VARIANT[ident['repo']] != a.variant:
        raise SystemExit('ERROR: repo %s chi duoc chay variant %s (nhan %s)' %
                         (ident['repo'], C.REPO_VARIANT[ident['repo']], a.variant))
    if ident['dirty_tracked_files']:
        raise SystemExit('ERROR: repo co file da track bi sua chua commit: %s' % ident['dirty_tracked_files'])

    C.require_inside(a.sample, '--sample')
    smp = C.load_json(a.sample)
    if smp.get('test_id') != a.test_id or smp.get('run_id') != a.run_id:
        raise SystemExit('ERROR: sample thuoc test_id=%s run_id=%s, khong khop tham so' %
                         (smp.get('test_id'), smp.get('run_id')))
    if smp['seed'] in C.FORBIDDEN_SEEDS:
        raise SystemExit('ERROR: sample dung seed cua T0/T1')

    label = C.VARIANT_LABEL[a.variant]
    out = os.path.join(C.OUT_ROOT, a.run_id, '%s_%s_r%d' % (a.test_id, label, a.rep))
    C.require_inside(out, 'out')
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, 'shortestPaths_0.pkl')):
        raise SystemExit('ERROR: %s da co shortestPaths_0.pkl - khong ghi de' % out)
    sys.stdout = C.Tee(os.path.join(out, 'run.log'))

    print('[T2] %s %s %s rep=%d repo=%s@%s' % (a.run_id, a.test_id, label, a.rep, ident['repo'],
                                              ident['commit_short']), flush=True)
    t_sha = time.perf_counter()
    psha = C.pickles_sha()
    sample_sha = C.sha256_file(a.sample)
    print('[T2] sha256 pickles + sample - %.1f s' % (time.perf_counter() - t_sha), flush=True)

    window = smp['window']
    t_load = time.perf_counter()
    gtt, dfNd, spd, stops = C.load_inputs(window)
    load_s = time.perf_counter() - t_load
    missing = set(smp['stopTo']) - set(int(s) for s in stops)
    if missing:
        raise SystemExit('ERROR: %d stopTo trong sample khong co trong allStops' % len(missing))

    import ttgAnalysisMultip_v2 as ttg
    func = {'v3': 'calcShortestPathsSubset_v3', 'v4': 'calcShortestPathsSubset_v4'}[a.variant]
    print('[T2] goi %s.%s |stopFr|=%d |stopTo|=%d window=%s' %
          (ident['repo'], func, len(smp['stopFr']), len(smp['stopTo']), window), flush=True)
    t0 = time.perf_counter()
    getattr(ttg, func)(gtt, smp['stopFr'], smp['stopTo'], window, dfNd, spd, 0, out)
    elapsed = time.perf_counter() - t0

    manifest = {
        'experiment': 'EXP-HB-004', 'test_id': a.test_id, 'run_id': a.run_id, 'rep': a.rep,
        'variant': a.variant, 'label': label, 'function': func, **ident,
        'sample_file': os.path.abspath(a.sample), 'sample_sha256': sample_sha, 'seed': smp['seed'],
        'window': window, 'n_stopfr': len(smp['stopFr']), 'n_stopto': len(smp['stopTo']),
        'pickles_sha256': psha, 'load_s': load_s, 'elapsed_s': elapsed,
        'elapsed_per_stopfr_s': elapsed / max(1, len(smp['stopFr'])), 'max_rss_mib': C.max_rss_mib(),
        'env': C.env_info(), 'finished': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    C.save_json(manifest, os.path.join(out, 'manifest.json'))
    print('[T2] done %s %s r%d elapsed=%.1f s (%.1f s/stopFr) maxRSS=%.0f MiB' %
          (a.test_id, label, a.rep, elapsed, manifest['elapsed_per_stopfr_s'], manifest['max_rss_mib']), flush=True)


if __name__ == '__main__':
    main()
