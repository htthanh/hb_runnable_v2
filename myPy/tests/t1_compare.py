"""T1 - so sanh output buoc 5 theo khoa (stopFr, stopTo), gioi han trong mot mau.

  --test : file shortestPaths_0.pkl (do t1_run.py sinh)
  --ref  : (a) THU MUC golden chua shortestPaths_*.pkl (50 file cua lan chay 580h), hoac
           (b) mot file .pkl khac (vd output v3 cua T1a de so v3p voi v3)
  --sample : sample.json cua t1_run.py -> chi xet cap co stopFr trong mau va stopTo trong mau

So theo khoa vi partition() cua golden dung random.shuffle khong seed (thu tu list khong tai lap duoc);
trong v3/v3p moi cap (stopFr, stopTo) duoc tinh doc lap nen so theo khoa la chinh xac.

Kiem tra: cung tap khoa (khong thieu / khong thua), khong trung khoa, tung truong bang nhau
(timeFr, timeTo, path, flag). Exit code 0 = khop 100%, 1 = co sai khac.
"""
import argparse
import glob
import os
import pickle
import sys
from collections import Counter

import common as C

FIELDS = ['timeFr', 'timeTo', 'path', 'flag']


def index_records(records, stopfr_set, stopto_set, src, out, dups):
    n = 0
    for r in records:
        sf, st = int(r[0]), int(r[1])
        if sf not in stopfr_set or st not in stopto_set:
            continue
        key = (sf, st)
        if key in out:
            dups[src] += 1
        out[key] = (r[2], r[3], list(r[4]), r[5])
        n += 1
    return n


def load_side(path, stopfr_set, stopto_set, name, dups):
    out = {}
    files = sorted(glob.glob(os.path.join(path, 'shortestPaths_*.pkl'))) if os.path.isdir(path) else [path]
    if not files:
        raise SystemExit('ERROR: khong tim thay shortestPaths_*.pkl trong %s' % path)
    total = 0
    for fp in files:
        with open(fp, 'rb') as f:
            recs = pickle.load(f)
        total += len(recs)
        index_records(recs, stopfr_set, stopto_set, name, out, dups)
        del recs
    print('[%s] %d file, %d record tong, %d record trong mau' % (name, len(files), total, len(out)), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--test', required=True)
    ap.add_argument('--ref', required=True)
    ap.add_argument('--sample', required=True)
    ap.add_argument('--max-show', type=int, default=20)
    a = ap.parse_args()
    C.require_inside(a.test, '--test')
    C.require_inside(a.sample, '--sample')
    # --ref: output golden cua hb_busnet_runnable (chi DOC) hoac mot output khac trong runnable_v2
    print('[ref] doc (read-only): %s' % os.path.realpath(a.ref))

    smp = C.load_json(a.sample)
    sf_set = set(int(s) for s in smp['stopFr'])
    st_set = set(int(s) for s in smp['stopTo'])
    print('[sample] window=%s |stopFr|=%d |stopTo|=%d' % (smp['window'], len(sf_set), len(st_set)))

    dups = Counter()
    test = load_side(a.test, sf_set, st_set, 'test', dups)
    ref = load_side(a.ref, sf_set, st_set, 'ref', dups)

    # stopFr co trong ref khong? (golden: neu stopFr khong co record nao thi nghi ngo sai window/sai folder)
    sf_in_ref = set(k[0] for k in ref)
    sf_in_test = set(k[0] for k in test)
    for sf in sorted(sf_set):
        if sf not in sf_in_ref or sf not in sf_in_test:
            print('[warn] stopFr %d: co trong ref=%s, test=%s' % (sf, sf in sf_in_ref, sf in sf_in_test))

    only_test = sorted(set(test) - set(ref))
    only_ref = sorted(set(ref) - set(test))
    common_keys = sorted(set(test) & set(ref))
    field_diff = Counter()
    type_only_diff = 0
    bad = []
    for k in common_keys:
        t, r = test[k], ref[k]
        diff = [FIELDS[i] for i in range(4) if not (t[i] == r[i])]
        if diff:
            for d in diff:
                field_diff[d] += 1
            bad.append((k, diff, t, r))
        elif any(type(t[i]) is not type(r[i]) for i in (0, 1, 3)):
            type_only_diff += 1

    flags = Counter(v[3] for v in ref.values())
    print('\n===== T1 compare =====')
    print('cap trong ref : %d (di bo flag -1: %d, co path flag -2: %d)' % (len(ref), flags.get(-1, 0), flags.get(-2, 0)))
    print('cap trong test: %d' % len(test))
    print('trung khoa    : test=%d ref=%d' % (dups['test'], dups['ref']))
    print('chi co o test : %d' % len(only_test))
    print('chi co o ref  : %d' % len(only_ref))
    print('khac truong   : %d cap %s' % (len(bad), dict(field_diff)))
    print('chi khac kieu (gia tri bang nhau): %d' % type_only_diff)
    for k in only_test[:a.max_show]:
        print('  only_test', k, test[k][:2], test[k][3])
    for k in only_ref[:a.max_show]:
        print('  only_ref ', k, ref[k][:2], ref[k][3])
    for k, diff, t, r in bad[:a.max_show]:
        print('  diff %s %s\n    test=%s\n    ref =%s' % (k, diff, t, r))

    ok = not (only_test or only_ref or bad or dups['test'] or dups['ref'])
    print('\nKET QUA: %s' % ('KHOP 100%' if ok else 'CO SAI KHAC'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
