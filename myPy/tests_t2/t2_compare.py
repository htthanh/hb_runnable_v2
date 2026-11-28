"""T2 (EXP-HB-004) - so output P2 (hb_runnable_v2) voi P0 (hb_runnable). Chi co o hb_runnable_v2.

  --test : thu muc output P2, nam trong hb_runnable_v2 (vd .../out/<run_id>/T2a_P2_r1)
  --ref  : thu muc output P0, nam trong hb_runnable (chi DOC)  (vd ~/hb_runnable/myPy/tests_t2/out/<run_id>/T2a_P0_r1)
  --ref-repo-root : thu muc goc cua hb_runnable (de kiem --ref nam trong do)

Buoc 1 - kiem manifest (exit 3 neu sai): test la hb_runnable_v2/v4, ref la hb_runnable/v3; cung run_id,
  test_id, window, sample_sha256, pickles_sha256 va phien ban python/igraph/pandas/numpy; ca 2 repo khong dirty.
  Output cua T0/T1 khong co manifest.json => bi tu choi.
Buoc 2 - so ket qua (exit 1 neu sai khac):
  (a) list shortestPaths giong het tung phan tu VA thu tu (hai ben chay cung mau, cung thu tu stopTo);
  (b) so theo khoa (stopFr, stopTo): thieu/thua/trung khoa, sai khac tung truong timeFr, timeTo, path, flag.
Ghi compare.json vao --test. Exit 0 = khop 100%.
"""
import argparse
import os
import pickle
import sys
from collections import Counter

import t2_common as C

FIELDS = ['timeFr', 'timeTo', 'path', 'flag']
SAME_KEYS = ['run_id', 'test_id', 'window', 'seed', 'n_stopfr', 'n_stopto', 'sample_sha256', 'pickles_sha256']
SAME_ENV = ['python', 'igraph', 'pandas', 'numpy', 'host']


def check_manifests(mt, mr):
    errs = []
    if (mt.get('repo'), mt.get('variant')) != ('hb_runnable_v2', 'v4'):
        errs.append('test phai la hb_runnable_v2/v4, nhan %s/%s' % (mt.get('repo'), mt.get('variant')))
    if (mr.get('repo'), mr.get('variant')) != ('hb_runnable', 'v3'):
        errs.append('ref phai la hb_runnable/v3, nhan %s/%s' % (mr.get('repo'), mr.get('variant')))
    for k in SAME_KEYS:
        if mt.get(k) != mr.get(k):
            errs.append('%s khac nhau: test=%s ref=%s' % (k, mt.get(k), mr.get(k)))
    for k in SAME_ENV:
        if mt['env'].get(k) != mr['env'].get(k):
            errs.append('env.%s khac nhau: test=%s ref=%s' % (k, mt['env'].get(k), mr['env'].get(k)))
    for side, m in (('test', mt), ('ref', mr)):
        if m.get('dirty_tracked_files'):
            errs.append('%s repo dirty: %s' % (side, m['dirty_tracked_files']))
    return errs


def index(records, name, dups):
    out = {}
    for r in records:
        k = (int(r[0]), int(r[1]))
        if k in out:
            dups[name] += 1
        out[k] = (r[2], r[3], list(r[4]), r[5])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--test', required=True)
    ap.add_argument('--ref', required=True)
    ap.add_argument('--ref-repo-root', required=True)
    ap.add_argument('--max-show', type=int, default=20)
    a = ap.parse_args()

    C.require_inside(a.test, '--test')
    C.require_inside(a.ref, '--ref', root=os.path.realpath(a.ref_repo_root))
    if os.path.realpath(a.ref_repo_root) == C.REPO_ROOT:
        raise SystemExit('ERROR: --ref-repo-root trung voi repo hien tai')

    mt_p, mr_p = os.path.join(a.test, 'manifest.json'), os.path.join(a.ref, 'manifest.json')
    for p in (mt_p, mr_p):
        if not os.path.isfile(p):
            print('ERROR: thieu %s (output khong phai cua T2?)' % p)
            sys.exit(3)
    mt, mr = C.load_json(mt_p), C.load_json(mr_p)
    errs = check_manifests(mt, mr)
    print('[manifest] test: %s@%s %s %s r%s' % (mt['repo'], mt['commit_short'], mt['label'], mt['test_id'], mt['rep']))
    print('[manifest] ref : %s@%s %s %s r%s (read-only)' % (mr['repo'], mr['commit_short'], mr['label'], mr['test_id'], mr['rep']))
    if errs:
        print('KET QUA: MANIFEST KHONG KHOP - khong so')
        for e in errs:
            print('  - ' + e)
        sys.exit(3)

    test = pickle.load(open(os.path.join(a.test, 'shortestPaths_0.pkl'), 'rb'))
    ref = pickle.load(open(os.path.join(a.ref, 'shortestPaths_0.pkl'), 'rb'))
    exact_list = (test == ref)

    dups = Counter()
    ti, ri = index(test, 'test', dups), index(ref, 'ref', dups)
    only_test = sorted(set(ti) - set(ri))
    only_ref = sorted(set(ri) - set(ti))
    field_diff, bad = Counter(), []
    for k in sorted(set(ti) & set(ri)):
        d = [FIELDS[i] for i in range(4) if ti[k][i] != ri[k][i]]
        if d:
            field_diff.update(d)
            bad.append((k, d, ti[k], ri[k]))
    flags = Counter(v[3] for v in ri.values())
    ok = exact_list and not (only_test or only_ref or bad or dups['test'] or dups['ref'])

    res = {'test': os.path.abspath(a.test), 'ref': os.path.realpath(a.ref), 'run_id': mt['run_id'],
           'test_id': mt['test_id'], 'test_rep': mt['rep'], 'ref_rep': mr['rep'],
           'n_records_test': len(test), 'n_records_ref': len(ref),
           'n_path_ref': flags.get(-2, 0), 'n_walk_ref': flags.get(-1, 0),
           'exact_list_equal': exact_list, 'dup_keys': dict(dups), 'only_test': len(only_test),
           'only_ref': len(only_ref), 'field_diff': dict(field_diff), 'n_field_diff_pairs': len(bad), 'match': ok}
    C.save_json(res, os.path.join(a.test, 'compare_vs_%s_P0_r%d.json' % (mt['test_id'], mr['rep'])))

    print('\n===== T2 compare: %s P2 r%d vs P0 r%d =====' % (mt['test_id'], mt['rep'], mr['rep']))
    print('record ref (P0): %d (path flag -2: %d, di bo flag -1: %d)' % (len(ref), flags.get(-2, 0), flags.get(-1, 0)))
    print('record test(P2): %d' % len(test))
    print('list giong het ca thu tu: %s' % exact_list)
    print('trung khoa: test=%d ref=%d | chi co o test: %d | chi co o ref: %d' %
          (dups['test'], dups['ref'], len(only_test), len(only_ref)))
    print('khac truong: %d cap %s' % (len(bad), dict(field_diff)))
    for k in only_test[:a.max_show]:
        print('  only_test', k)
    for k in only_ref[:a.max_show]:
        print('  only_ref ', k)
    for k, d, t, r in bad[:a.max_show]:
        print('  diff %s %s\n    test=%s\n    ref =%s' % (k, d, t, r))
    print('\nKET QUA: %s' % ('KHOP 100%' if ok else 'CO SAI KHAC'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
