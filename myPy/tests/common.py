"""Helpers dung chung cho T0/T1 (hb_busnet_runnable_v2, buoc 5).

- Khong sua code goc; chi import tu myPy (constants, ttgAnalysisMultip_v2).
- Moi duong dan input/ref/out truyen tuong minh qua tham so.
- Mau stopFr/stopTo lay tu allStops da SAP XEP + random.Random(seed) => tai lap duoc,
  khong phu thuoc thu tu cua set() va khong dung random.shuffle cua partition().
"""
import json
import os
import pickle
import platform
import random
import resource
import socket
import sys
import time

MYPY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if MYPY_DIR not in sys.path:
    sys.path.insert(0, MYPY_DIR)

import constants as const  # noqa: E402
import ttgAnalysisMultip_v2 as ttg  # noqa: E402

# Thu muc goc cua ban code nay (hb_busnet_runnable_v2); constants.PROJECT_ROOT duoc suy tu __file__.
V2_ROOT = os.path.realpath(const.PROJECT_ROOT)
DEFAULT_PICKLES = const.picklesFolder


def require_inside(path, what, root=V2_ROOT):
    """Chan contaminate: path (sau khi resolve symlink) phai nam trong root."""
    rp = os.path.realpath(path)
    if not (rp == root or rp.startswith(root + os.sep)):
        raise SystemExit('ERROR: %s = %s (realpath %s) nam NGOAI %s. Input/output cua runnable_v2 phai nam trong '
                         'folder runnable_v2 (copy file vao, khong symlink); golden chi doc qua --ref.'
                         % (what, path, rp, root))
    return path


COL_STN = const.dfNdDetailsCols.StationId.name
COL_TIME = const.dfNdDetailsCols.time.name
COL_ARRDEP = const.dfNdDetailsCols.arrOrDep.name
COL_ARR = const.dfNdDetailsCols.arr.name
COL_DEP = const.dfNdDetailsCols.dep.name
COL_NDID = const.dfNdDetailsCols.gttNdID.name
WEIGHT = const.GttEdgeAttribs.transfer.name


def parse_window(s):
    """'7,10' -> [25200, 36000] (giong main_ttgAnalysisMultip_v2)."""
    a, b = [int(x) for x in s.split(',')]
    return [a * 3600, b * 3600]


def window_tag(window):
    return '%02d00_%02d00' % (window[0] // 3600, window[1] // 3600)


def env_info():
    import igraph
    import numpy
    import pandas
    return {
        'host': socket.gethostname(),
        'platform': platform.platform(),
        'python': sys.version.split()[0],
        'igraph': igraph.__version__,
        'pandas': pandas.__version__,
        'numpy': numpy.__version__,
        'cpu_count': os.cpu_count(),
    }


def max_rss_mib():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux: KiB, macOS: bytes
    return r / 1024.0 if sys.platform.startswith('linux') else r / (1024.0 * 1024.0)


def load_inputs(pickles_dir, window):
    """Load 4 pickle + addTransferEdgesAllStops + allStops, DUNG nhu calcShortestPathsMultip."""
    require_inside(pickles_dir, '--pickles')
    t0 = time.perf_counter()
    gtt = pickle.load(open(os.path.join(pickles_dir, 'GttTransit_v2.pkl'), 'rb'))
    dfNd = pickle.load(open(os.path.join(pickles_dir, 'dfNdDetails_v2.pkl'), 'rb'))
    dfTr = pickle.load(open(os.path.join(pickles_dir, 'dfAllTransfers.pkl'), 'rb'))
    spd = pickle.load(open(os.path.join(pickles_dir, 'stopPairsDist.pkl'), 'rb'))
    print('[load] 4 pickles loaded - %.1f s' % (time.perf_counter() - t0), flush=True)

    t1 = time.perf_counter()
    ttg.addTransferEdgesAllStops(gtt, dfTr, window)  # ham goc
    print('[load] addTransferEdgesAllStops - %.1f s' % (time.perf_counter() - t1), flush=True)
    del dfTr

    # giong calcShortestPathsMultip (dong 385-387)
    allStops = dfNd[COL_STN].loc[(dfNd[COL_TIME] >= window[0]) &
                                 (dfNd[COL_TIME] <= window[1])].values.tolist()
    allStops = list(set(allStops))
    print('[load] |V|=%d |E|=%d allStops=%d' % (gtt.vcount(), gtt.ecount(), len(allStops)), flush=True)
    return gtt, dfNd, spd, allStops


def make_sample(allStops, n_stopfr, n_stopto, seed, stopfr=None):
    """Mau tai lap: stopFr va stopTo lay tu sorted(allStops) voi random.Random(seed).
    n_stopto <= 0 => toan bo allStops (giu thu tu sorted)."""
    pool = sorted(int(s) for s in allStops)
    rng = random.Random(seed)
    if stopfr:
        stopFrList = [int(s) for s in stopfr]
    else:
        stopFrList = rng.sample(pool, n_stopfr)
    if n_stopto and n_stopto > 0:
        stopToList = sorted(rng.sample(pool, n_stopto))
    else:
        stopToList = pool
    return stopFrList, stopToList


def save_json(obj, path):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2, default=str)


def load_json(path):
    with open(path) as f:
        return json.load(f)
