"""T2 (EXP-HB-004) - tong hop thoi gian P0 vs P2 va ket qua so sanh cua mot run_id. Chi co o hb_runnable_v2.

Doc manifest.json cua moi lan chay (P2 trong repo nay, P0 trong --ref-repo-root, chi doc) va cac
compare_vs_*.json. Ghi out/<run_id>/t2_summary.json va t2_summary.md (repo nay).

Thoi gian: chi tinh thoi gian ham buoc 5 (elapsed_s), khong gom load/sha. Speedup = mean(P0) / mean(P2)
tren cung test_id (cung mau, cung may, 1 process, chay tuan tu). Khoang [min, max] = min(P0)/max(P2) .. max(P0)/min(P2).
"""
import argparse
import glob
import os
import re
import statistics as st

import t2_common as C


def collect(root, run_id):
    rows = []
    for mp in sorted(glob.glob(os.path.join(root, 'myPy', 'tests_t2', 'out', run_id, '*', 'manifest.json'))):
        m = C.load_json(mp)
        log = os.path.join(os.path.dirname(mp), 'run.log')
        m['nSpCalls'] = m['maxTargets'] = None
        if os.path.isfile(log):
            hit = re.findall(r'P2 finished - nSpCalls (\d+) maxTargets (\d+)', open(log).read())
            if hit:
                m['nSpCalls'], m['maxTargets'] = int(hit[-1][0]), int(hit[-1][1])
        m['per_stopfr_cum_s'] = []
        if os.path.isfile(log):
            # v3 va v4 deu in: 'process 0 - k stopFr completed (...) - elapsed time x mins (y secs)' (cong don)
            m['per_stopfr_cum_s'] = [float(x) for x in re.findall(
                r'process \d+ - \d+ stopFr completed .*?mins \(([-+.\deE]+) secs\)', open(log).read())]
        rows.append(m)
    return rows


def per_stopfr(cum):
    return [b - a for a, b in zip([0.0] + cum[:-1], cum)]


def ms(xs):
    return (st.mean(xs), st.stdev(xs) if len(xs) > 1 else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--ref-repo-root', required=True, help='thu muc goc hb_runnable (chi doc)')
    a = ap.parse_args()

    runs = collect(C.REPO_ROOT, a.run_id) + collect(os.path.realpath(a.ref_repo_root), a.run_id)
    cmps = [C.load_json(p) for p in sorted(glob.glob(os.path.join(C.OUT_ROOT, a.run_id, '*', 'compare_vs_*.json')))]
    out = {'run_id': a.run_id, 'tests': {}}
    md = ['# T2 (EXP-HB-004) - %s' % a.run_id, '',
          '| Test | Bien the | n | s/stopFr (mean ± std) | elapsed_s cac lan | maxRSS MiB | nSpCalls (P2) | maxTargets (P2) |',
          '|---|---|---|---|---|---|---|---|']
    for tid in sorted({r['test_id'] for r in runs}):
        t = {}
        for lab in ('P0', 'P2'):
            rs = sorted([r for r in runs if r['test_id'] == tid and r['label'] == lab], key=lambda r: r['rep'])
            if not rs:
                continue
            el = [r['elapsed_s'] for r in rs]
            ps = [r['elapsed_per_stopfr_s'] for r in rs]
            t[lab] = {'reps': [r['rep'] for r in rs], 'elapsed_s': el, 'per_stopfr_s': ps,
                      'mean_s': ms(el)[0], 'std_s': ms(el)[1], 'mean_per_stopfr_s': ms(ps)[0],
                      'std_per_stopfr_s': ms(ps)[1], 'max_rss_mib': max(r['max_rss_mib'] for r in rs),
                      'nSpCalls': [r['nSpCalls'] for r in rs], 'maxTargets': [r['maxTargets'] for r in rs],
                      'repo_commit': sorted({'%s@%s' % (r['repo'], r['commit_short']) for r in rs}),
                      'n_stopfr': rs[0]['n_stopfr'], 'n_stopto': rs[0]['n_stopto'], 'seed': rs[0]['seed']}
            md.append('| %s | %s (%s) | %d | %.1f ± %.1f | %s | %.0f | %s | %s |' % (
                tid, lab, ', '.join(t[lab]['repo_commit']), len(rs), t[lab]['mean_per_stopfr_s'],
                t[lab]['std_per_stopfr_s'], ', '.join('%.1f' % x for x in el), t[lab]['max_rss_mib'],
                ', '.join(str(x) for x in t[lab]['nSpCalls']) if lab == 'P2' else '-',
                ', '.join(str(x) for x in t[lab]['maxTargets']) if lab == 'P2' else '-'))
        if 'P0' in t and 'P2' in t:
            p0, p2 = t['P0']['elapsed_s'], t['P2']['elapsed_s']
            t['speedup_mean'] = st.mean(p0) / st.mean(p2)
            t['speedup_range'] = [min(p0) / max(p2), max(p0) / min(p2)]
        c = [x for x in cmps if x['test_id'] == tid]
        t['compares'] = [{'P2_rep': x['test_rep'], 'P0_rep': x['ref_rep'], 'match': x['match'],
                          'exact_list_equal': x['exact_list_equal'], 'n_records': x['n_records_ref'],
                          'n_path': x['n_path_ref'], 'n_walk': x['n_walk_ref']} for x in c]
        t['all_match'] = bool(c) and all(x['match'] for x in c)
        # thoi gian tung stopFr (lan chay dau moi ben) -> speedup tung stopFr
        r0 = [r for r in runs if r['test_id'] == tid and r['label'] == 'P0' and r['rep'] == 1]
        r2 = [r for r in runs if r['test_id'] == tid and r['label'] == 'P2' and r['rep'] == 1]
        if r0 and r2:
            d0, d2 = per_stopfr(r0[0]['per_stopfr_cum_s']), per_stopfr(r2[0]['per_stopfr_cum_s'])
            if len(d0) == len(d2) and d0:
                t['per_stopfr_r1'] = [{'P0_s': x, 'P2_s': y, 'speedup': (x / y if y > 0 else None)}
                                      for x, y in zip(d0, d2)]
        out['tests'][tid] = t

    md += ['', '| Test | Mau (seed) | Speedup P0/P2 (mean) | Khoang [min, max] | So sanh P2 vs P0 |', '|---|---|---|---|---|']
    for tid, t in out['tests'].items():
        base = t.get('P0') or t.get('P2')
        sp = ('%.1f×' % t['speedup_mean']) if 'speedup_mean' in t else '-'
        rg = ('%.1f× – %.1f×' % tuple(t['speedup_range'])) if 'speedup_range' in t else '-'
        cm = '; '.join('P2 r%d vs P0 r%d: %s (%d record)' % (x['P2_rep'], x['P0_rep'],
                       'KHỚP' if x['match'] else 'SAI KHÁC', x['n_records']) for x in t['compares']) or 'chua so'
        md.append('| %s | %d × %d (%d) | %s | %s | %s |' % (tid, base['n_stopfr'], base['n_stopto'], base['seed'], sp, rg, cm))
    for tid, t in out['tests'].items():
        if 'per_stopfr_r1' in t:
            sps = [x['speedup'] for x in t['per_stopfr_r1'] if x['speedup']]
            md += ['', '%s - tung stopFr (lan 1; do chinh xac 4 chu so tu log): speedup median %.1f×, min %.1f×, max %.1f×' %
                   (tid, st.median(sps), min(sps), max(sps)) if sps else '', '',
                   '| # | P0 s | P2 s | speedup |', '|---|---|---|---|']
            md += ['| %d | %.1f | %.2f | %s |' % (i + 1, x['P0_s'], x['P2_s'],
                   ('%.1f×' % x['speedup']) if x['speedup'] else '-') for i, x in enumerate(t['per_stopfr_r1'])]
    md += ['', 'Thoi gian = chi ham buoc 5, 1 process, cung may, chay tuan tu; khong gom load (~1 phut 42 giay) va sha256.']

    C.save_json(out, os.path.join(C.OUT_ROOT, a.run_id, 't2_summary.json'))
    with open(os.path.join(C.OUT_ROOT, a.run_id, 't2_summary.md'), 'w') as f:
        f.write('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
