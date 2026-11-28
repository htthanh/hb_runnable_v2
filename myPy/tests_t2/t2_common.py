"""T2 (EXP-HB-004) - helpers dung chung. FILE NAY GIONG HET o hb_runnable va hb_runnable_v2.

Nguyen tac cach ly:
- REPO_ROOT suy tu vi tri file nay (thu muc cha cua myPy/). Script chi import code cua CHINH repo nay
  (myPy/constants.py, myPy/ttgAnalysisMultip_v2.py), chi doc input trong REPO_ROOT/myPy/outputs/pickles,
  chi ghi vao REPO_ROOT/myPy/tests_t2/out/.
- Moi output co manifest.json (test_id, run_id, repo, commit, variant, sha256 cua pickle va sample)
  de t2_compare.py tu choi so nham voi output cua T0/T1 (khong co manifest) hoac cua lan chay khac.
"""
import hashlib
import json
import os
import pickle
import platform
import random
import resource
import socket
import subprocess
import sys
import time

TESTS_T2_DIR = os.path.dirname(os.path.abspath(__file__))
MYPY_DIR = os.path.dirname(TESTS_T2_DIR)
REPO_ROOT = os.path.realpath(os.path.dirname(MYPY_DIR))
if MYPY_DIR not in sys.path:
    sys.path.insert(0, MYPY_DIR)

PICKLES_DIR = os.path.join(MYPY_DIR, 'outputs', 'pickles')
OUT_ROOT = os.path.join(TESTS_T2_DIR, 'out')
PICKLE_FILES = ['GttTransit_v2.pkl', 'dfNdDetails_v2.pkl', 'dfAllTransfers.pkl', 'stopPairsDist.pkl']

# Bien the hop le cho tung repo: P0 chi chay tu hb_runnable (code golden), P2 chi chay tu hb_runnable_v2.
REPO_VARIANT = {'hb_runnable': 'v3', 'hb_runnable_v2': 'v4'}
VARIANT_LABEL = {'v3': 'P0', 'v4': 'P2'}
# Seed da dung o T0/T1 (EXP-HB-003): cam dung lai de mau T2 khong trung mau T0/T1.
FORBIDDEN_SEEDS = {2026, 7}
TEST_IDS = ('T2a', 'T2b', 'T2x')  # T2x: chi dung khi tu kiem tren du lieu gia lap


def require_inside(path, what, root=REPO_ROOT):
    rp = os.path.realpath(path)
    if not (rp == root or rp.startswith(root + os.sep)):
        raise SystemExit('ERROR: %s = %s (realpath %s) nam NGOAI repo %s. Input/output cua T2 phai nam trong '
                         'chinh repo dang chay (copy file vao, khong symlink).' % (what, path, rp, root))
    return path


def git(*args, cwd=REPO_ROOT):
    return subprocess.run(['git'] + list(args), cwd=cwd, capture_output=True, text=True).stdout.strip()


def repo_identity():
    """Ten repo lay tu remote origin (vd git@...:htthanh/hb_runnable_v2.git -> hb_runnable_v2)."""
    url = git('remote', 'get-url', 'origin')
    name = os.path.basename(url)
    if name.endswith('.git'):
        name = name[:-4]
    if name not in REPO_VARIANT:
        raise SystemExit('ERROR: remote origin = %r, khong phai hb_runnable / hb_runnable_v2' % url)
    dirty = [l for l in git('status', '--porcelain', '--untracked-files=no').splitlines() if l.strip()]
    return {'repo': name, 'root': REPO_ROOT, 'commit': git('rev-parse', 'HEAD'),
            'commit_short': git('rev-parse', '--short', 'HEAD'), 'dirty_tracked_files': dirty}


def sha256_file(path, bufsize=1 << 24):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def pickles_sha():
    out = {}
    for fn in PICKLE_FILES:
        p = os.path.join(PICKLES_DIR, fn)
        if not os.path.isfile(p):
            raise SystemExit('ERROR: thieu input %s (copy vao %s truoc, xem README)' % (p, PICKLES_DIR))
        if os.path.islink(p):
            raise SystemExit('ERROR: %s la symlink - phai copy file that vao repo' % p)
        require_inside(p, 'pickle')
        out[fn] = sha256_file(p)
    return out


def parse_window(s):
    a, b = [int(x) for x in s.split(',')]
    return [a * 3600, b * 3600]


def env_info():
    import igraph
    import numpy
    import pandas
    return {'host': socket.gethostname(), 'platform': platform.platform(), 'python': sys.version.split()[0],
            'igraph': igraph.__version__, 'pandas': pandas.__version__, 'numpy': numpy.__version__,
            'cpu_count': os.cpu_count(), 'loadavg_at_start': list(os.getloadavg())}


def max_rss_mib():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / 1024.0 if sys.platform.startswith('linux') else r / (1024.0 * 1024.0)


def all_stops(dfNd, window):
    """Giong calcShortestPathsMultip: stop co node trong window."""
    import constants as const
    stn, tm = const.dfNdDetailsCols.StationId.name, const.dfNdDetailsCols.time.name
    s = dfNd[stn].loc[(dfNd[tm] >= window[0]) & (dfNd[tm] <= window[1])].values.tolist()
    return list(set(s))


def load_inputs(window):
    """Load 4 pickle trong repo + addTransferEdgesAllStops (ham goc cua repo nay) + allStops."""
    import ttgAnalysisMultip_v2 as ttg
    t0 = time.perf_counter()
    gtt = pickle.load(open(os.path.join(PICKLES_DIR, 'GttTransit_v2.pkl'), 'rb'))
    dfNd = pickle.load(open(os.path.join(PICKLES_DIR, 'dfNdDetails_v2.pkl'), 'rb'))
    dfTr = pickle.load(open(os.path.join(PICKLES_DIR, 'dfAllTransfers.pkl'), 'rb'))
    spd = pickle.load(open(os.path.join(PICKLES_DIR, 'stopPairsDist.pkl'), 'rb'))
    print('[load] 4 pickles - %.1f s' % (time.perf_counter() - t0), flush=True)
    t1 = time.perf_counter()
    ttg.addTransferEdgesAllStops(gtt, dfTr, window)
    print('[load] addTransferEdgesAllStops - %.1f s' % (time.perf_counter() - t1), flush=True)
    del dfTr
    stops = all_stops(dfNd, window)
    print('[load] |V|=%d |E|=%d allStops=%d' % (gtt.vcount(), gtt.ecount(), len(stops)), flush=True)
    return gtt, dfNd, spd, stops


def make_sample(stops, n_stopfr, n_stopto, seed):
    """Mau tai lap tu sorted(allStops) + random.Random(seed). n_stopto <= 0 => toan bo allStops."""
    if seed in FORBIDDEN_SEEDS:
        raise SystemExit('ERROR: seed %d da dung o T0/T1 - chon seed khac' % seed)
    pool = sorted(int(s) for s in stops)
    rng = random.Random(seed)
    stopFr = rng.sample(pool, n_stopfr)
    stopTo = sorted(rng.sample(pool, n_stopto)) if n_stopto and n_stopto > 0 else pool
    return stopFr, stopTo


def save_json(obj, path):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2, default=str)


def load_json(path):
    with open(path) as f:
        return json.load(f)


class Tee:
    """Ghi stdout ra ca man hinh lan file log trong thu muc output (de doc nSpCalls cua P2 ve sau)."""
    def __init__(self, path):
        self.f = open(path, 'a')
        self.s = sys.stdout

    def write(self, x):
        self.s.write(x)
        self.f.write(x)

    def flush(self):
        self.s.flush()
        self.f.flush()
