"""T0 - kiem tra gia thuyet cua P2: path igraph tra ve cho mot dinh dich KHONG phu thuoc tap `to`.

Voi moi stopFr trong mau va moi candidate (nodeFr, timeFr) cua stopFr (thu tu nhu v3):
  (a) per-stopTo : get_shortest_paths(nodeFr, to=nodeToList(stopTo))       <- cach v3 goi
  (b) full       : 1 loi goi voi to = noi nodeToList cua MOI stopTo khong di bo duoc, cat theo offset
  (c) p2         : 1 loi goi voi to = noi nodeToList cua cac stopTo CHUA GIAI (mo phong dung P2), cat theo offset
So TOAN BO list path cua tung stopTo trong mau: (a)==(b) va (a)==(c).
Ngoai ra so QUYET DINH cuoi (candidate nao, path nao) cua v3 (suy tu (a)) va cua P2 (suy tu (c)).

nodeToList dung DUNG cach cua P1 (arrByStop + loc time >= timeFr + maxWalkTime + sort_values),
nen T1 (v3p == v3 == golden) phai qua truoc.

Chi phi: moi candidate = 2 loi goi lon + n_stopto loi goi nho + ~|allStops| lan loc pandas nho.
Golden trung binh ~1,3 s/loi goi (gom ca pandas) => dat --n-stopfr/--n-stopto nho truoc, xem thoi gian
tung loai loi goi trong report roi moi tang. --max-seconds dung som mot cach an toan va van ghi report.
Exit code 0 = khop 100%, 1 = co sai khac, 2 = chua chay het (het thoi gian) nhung khong sai khac.
"""
import argparse
import os
import random
import time
import warnings

import common as C

warnings.filterwarnings('ignore', message=".*Couldn't reach some vertices.*")


def first_valid(paths):
    """Quy tac chon cua v3: path dau tien co len > 1 (theo thu tu nodeToList)."""
    for p in paths:
        if len(p) > 1:
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pickles', default=C.DEFAULT_PICKLES, help='mac dinh: myPy/outputs/pickles cua runnable_v2')
    ap.add_argument('--window', default='7,10')
    ap.add_argument('--n-stopfr', type=int, default=3)
    ap.add_argument('--n-stopto', type=int, default=50, help='so stopTo (khong di bo) duoc so voi (a) cho moi stopFr')
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--stopfr', default='', help='danh sach stopFr cu the, vd "12,345"')
    ap.add_argument('--max-cand', type=int, default=0, help='<=0: moi candidate')
    ap.add_argument('--max-seconds', type=float, default=0, help='<=0: khong gioi han')
    ap.add_argument('--max-show', type=int, default=20)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    C.require_inside(a.out, '--out')
    C.require_inside(a.pickles, '--pickles')
    os.makedirs(a.out, exist_ok=True)

    import igraph
    window = C.parse_window(a.window)
    gtt, dfNd, spd, allStops = C.load_inputs(a.pickles, window)
    const = C.const

    # ---- arrByStop: DUNG cach cua calcShortestPathsSubset_v3p (P1) ----
    dfArr = dfNd.loc[(dfNd[C.COL_ARRDEP] == C.COL_ARR) & (dfNd[C.COL_TIME] <= window[1])]
    arrByStop = {stn: grp for stn, grp in dfArr.groupby(C.COL_STN, sort=False)}
    dfArrEmpty = dfArr.iloc[0:0]

    def node_to_list(stopTo, timeFr):
        g = arrByStop.get(stopTo, dfArrEmpty)
        d = g.loc[g[C.COL_TIME] >= timeFr + const.maxWalkTime]
        d = d.sort_values(by=[C.COL_TIME])
        return d[C.COL_NDID].values.tolist()

    def gsp(nodeFr, to):
        return igraph.GraphBase.get_shortest_paths(gtt, v=nodeFr, to=to, weights=C.WEIGHT)

    stopFrList, _ = C.make_sample(allStops, a.n_stopfr, 0, a.seed,
                                  [s for s in a.stopfr.split(',') if s] or None)
    rngTo = random.Random(a.seed + 1)
    allSorted = sorted(allStops)

    stats = {'n_cand': 0, 'n_call_a': 0, 'n_call_b': 0, 'n_call_c': 0,
             't_a': 0.0, 't_b': 0.0, 't_c': 0.0, 't_pandas': 0.0,
             'targets_b_max': 0, 'targets_c_max': 0,
             'cmp_ab': 0, 'mis_ab': 0, 'cmp_ac': 0, 'mis_ac': 0,
             'empty_to_calls': 0, 'empty_to_nonempty_result': 0,
             'decisions_cmp': 0, 'decisions_mis': 0}
    examples = []
    per_stopfr = []
    tstart = time.perf_counter()
    timed_out = False

    for sf in stopFrList:
        if timed_out:
            break
        dfStopFrNds = dfNd.loc[(dfNd[C.COL_STN] == sf) & (dfNd[C.COL_TIME] >= window[0]) &
                               (dfNd[C.COL_TIME] <= window[1]) & (dfNd[C.COL_ARRDEP] == C.COL_DEP)]
        nodesFrNP = C.ttg.getMinTimeNodeEachDirRoute(dfStopFrNds)  # ham goc
        if nodesFrNP.size == 0:
            per_stopfr.append({'stopFr': sf, 'n_cand': 0, 'note': 'no nodes'})
            continue
        cands = nodesFrNP if a.max_cand <= 0 else nodesFrNP[:a.max_cand]

        nonwalk = [st for st in allSorted
                   if st != sf and spd['%d_%d' % (sf, st)] > const.maxWalkDist]
        sampleTo = rngTo.sample(nonwalk, min(a.n_stopto, len(nonwalk)))
        sampleSet = set(sampleTo)
        unresolved = list(nonwalk)
        dec_v3, dec_p2 = {}, {}
        done_all = True

        for ci, row in enumerate(cands):
            if a.max_seconds > 0 and time.perf_counter() - tstart > a.max_seconds:
                timed_out, done_all = True, False
                break
            nodeFr, timeFr = row[0], row[1]
            stats['n_cand'] += 1

            t = time.perf_counter()
            lists = {st: node_to_list(st, timeFr) for st in nonwalk}
            stats['t_pandas'] += time.perf_counter() - t

            # (b) full
            offB, allTo = {}, []
            for st in nonwalk:
                offB[st] = (len(allTo), len(allTo) + len(lists[st]))
                allTo.extend(lists[st])
            t = time.perf_counter()
            pB = gsp(nodeFr, allTo)
            stats['t_b'] += time.perf_counter() - t
            stats['n_call_b'] += 1
            stats['targets_b_max'] = max(stats['targets_b_max'], len(allTo))

            # (c) p2: chi cac stopTo chua giai
            unresSet = set(unresolved)
            offC, toC = {}, []
            for st in unresolved:
                offC[st] = (len(toC), len(toC) + len(lists[st]))
                toC.extend(lists[st])
            t = time.perf_counter()
            pC = gsp(nodeFr, toC) if toC else []
            stats['t_c'] += time.perf_counter() - t
            stats['n_call_c'] += 1
            stats['targets_c_max'] = max(stats['targets_c_max'], len(toC))
            still = []
            for st in unresolved:
                s, e = offC[st]
                p = first_valid(pC[s:e])
                if p is not None:
                    dec_p2[st] = (ci, p)
                else:
                    still.append(st)
            unresolved = still

            # (a) per-stopTo cho mau
            for st in sampleTo:
                to = lists[st]
                t = time.perf_counter()
                pA = gsp(nodeFr, to)
                stats['t_a'] += time.perf_counter() - t
                stats['n_call_a'] += 1
                if len(to) == 0:
                    stats['empty_to_calls'] += 1
                    if len(pA) != 0:
                        stats['empty_to_nonempty_result'] += 1
                s, e = offB[st]
                stats['cmp_ab'] += 1
                if pA != pB[s:e]:
                    stats['mis_ab'] += 1
                    if len(examples) < a.max_show:
                        examples.append({'kind': 'a!=b', 'stopFr': sf, 'stopTo': st, 'cand': ci,
                                         'nodeFr': nodeFr, 'n_to': len(to)})
                if st in unresSet:
                    s, e = offC[st]
                    stats['cmp_ac'] += 1
                    if pA != pC[s:e]:
                        stats['mis_ac'] += 1
                        if len(examples) < a.max_show:
                            examples.append({'kind': 'a!=c', 'stopFr': sf, 'stopTo': st, 'cand': ci,
                                             'nodeFr': nodeFr, 'n_to': len(to)})
                if st not in dec_v3:
                    p = first_valid(pA)
                    if p is not None:
                        dec_v3[st] = (ci, p)
            del pB, pC
            if not unresolved and all(st in dec_v3 for st in sampleSet):
                break  # nhu `break` cua v3/P2: khong con gi de giai

        n_dec_mis = 0
        if done_all:
            for st in sampleTo:
                stats['decisions_cmp'] += 1
                if dec_v3.get(st) != dec_p2.get(st):
                    n_dec_mis += 1
                    if len(examples) < a.max_show:
                        examples.append({'kind': 'decision', 'stopFr': sf, 'stopTo': st,
                                         'v3': dec_v3.get(st), 'p2': dec_p2.get(st)})
            stats['decisions_mis'] += n_dec_mis
        per_stopfr.append({'stopFr': sf, 'n_cand_total': int(len(nodesFrNP)), 'complete': done_all,
                           'n_nonwalk': len(nonwalk), 'n_sample': len(sampleTo),
                           'decision_mismatch': n_dec_mis if done_all else None,
                           'elapsed_total_s': time.perf_counter() - tstart})
        print('[T0] stopFr %d done (complete=%s) - elapsed %.1f s, mis_ab=%d mis_ac=%d dec_mis=%d' %
              (sf, done_all, time.perf_counter() - tstart, stats['mis_ab'], stats['mis_ac'],
               stats['decisions_mis']), flush=True)

    avg = lambda k, n: stats[k] / stats[n] if stats[n] else None  # noqa: E731
    report = {'window': window, 'seed': a.seed, 'stopFr': stopFrList, 'n_stopto': a.n_stopto,
              'max_cand': a.max_cand, 'timed_out': timed_out, 'stats': stats,
              'avg_s_per_call': {'a': avg('t_a', 'n_call_a'), 'b': avg('t_b', 'n_call_b'),
                                 'c': avg('t_c', 'n_call_c')},
              'max_rss_mib': C.max_rss_mib(), 'elapsed_s': time.perf_counter() - tstart,
              'per_stopfr': per_stopfr, 'examples': examples, 'env': C.env_info()}
    C.save_json(report, os.path.join(a.out, 't0_report.json'))

    mismatch = stats['mis_ab'] + stats['mis_ac'] + stats['decisions_mis']
    print('\n===== T0 report =====')
    for k in ['n_cand', 'n_call_a', 'n_call_b', 'n_call_c', 'cmp_ab', 'mis_ab', 'cmp_ac', 'mis_ac',
              'decisions_cmp', 'decisions_mis', 'empty_to_calls', 'empty_to_nonempty_result',
              'targets_b_max', 'targets_c_max']:
        print('%-26s %s' % (k, stats[k]))
    print('avg s/call a=%s b=%s c=%s ; pandas total %.1f s' %
          (report['avg_s_per_call']['a'], report['avg_s_per_call']['b'], report['avg_s_per_call']['c'],
           stats['t_pandas']))
    print('max RSS %.0f MiB ; elapsed %.1f s ; timed_out=%s' % (report['max_rss_mib'], report['elapsed_s'], timed_out))
    for ex in examples:
        print('  ', ex)
    if mismatch:
        print('\nKET QUA: CO SAI KHAC -> dung P2, phan tich examples')
        raise SystemExit(1)
    if timed_out:
        print('\nKET QUA: chua sai khac nao, nhung CHUA CHAY HET (timed_out)')
        raise SystemExit(2)
    print('\nKET QUA: KHOP 100%')


if __name__ == '__main__':
    main()
