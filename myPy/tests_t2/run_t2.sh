#!/usr/bin/env bash
# T2 (EXP-HB-004) - P2 (hb_runnable_v2, calcShortestPathsSubset_v4) vs P0 (hb_runnable, calcShortestPathsSubset_v3):
#   (1) tinh dung: output P2 phai giong het P0 tren cung mau; (2) thoi gian ham buoc 5 cua P2 so voi P0.
# Chay trong tmux (session 't2'), sau khi da chay t2_setup_inputs.sh. Moi buoc 1 process, chay TUAN TU.
#
#   RUN_ID=T2-$(date +%Y%m%d) bash run_t2.sh            # mac dinh: T2a + T2b
#   TESTS="T2a" RUN_ID=... bash run_t2.sh                # chi T2a
#
# Bien moi truong (mac dinh trong ngoac):
#   V1 ($HOME/hb_runnable)  V2 ($HOME/hb_runnable_v2)  PY (python)  WINDOW (7,10)  MAX_LOAD (2.0)
#   T2a: T2A_NFR (3) T2A_NTO (200) T2A_SEED (11) T2A_REPS (3)        -> P0 x REPS, P2 x REPS, xen ke
#   T2b: T2B_NFR (5) T2B_NTO (0 = toan bo stopTo) T2B_SEED (13) T2B_P2_REPS (3) -> P0 x 1, P2 x REPS
set -uo pipefail
V1=${V1:-$HOME/hb_runnable}
V2=${V2:-$HOME/hb_runnable_v2}
PY=${PY:-python}
RUN_ID=${RUN_ID:?dat RUN_ID, vd RUN_ID=T2-20261201}
TESTS=${TESTS:-"T2a T2b"}
WINDOW=${WINDOW:-7,10}
MAX_LOAD=${MAX_LOAD:-2.0}
T2A_NFR=${T2A_NFR:-3}; T2A_NTO=${T2A_NTO:-200}; T2A_SEED=${T2A_SEED:-11}; T2A_REPS=${T2A_REPS:-3}
T2B_NFR=${T2B_NFR:-5}; T2B_NTO=${T2B_NTO:-0};   T2B_SEED=${T2B_SEED:-13}; T2B_P2_REPS=${T2B_P2_REPS:-3}
T1=$V1/myPy/tests_t2; T2D=$V2/myPy/tests_t2
O1=$T1/out/$RUN_ID; O2=$T2D/out/$RUN_ID

die() { echo "PREFLIGHT ERROR: $*"; exit 2; }
ts() { date '+%Y-%m-%d %H:%M:%S'; }

# ---------- preflight ----------
case "$RUN_ID" in T2-*) ;; *) die "RUN_ID phai bat dau bang 'T2-' (tranh nham voi T0/T1)";; esac
[ "$(basename "$(git -C "$V1" remote get-url origin)" .git)" = hb_runnable ]    || die "$V1 khong phai hb_runnable"
[ "$(basename "$(git -C "$V2" remote get-url origin)" .git)" = hb_runnable_v2 ] || die "$V2 khong phai hb_runnable_v2"
for R in "$V1" "$V2"; do
  [ -z "$(git -C "$R" status --porcelain --untracked-files=no)" ] || die "$R co file da track bi sua chua commit"
done
grep -q "def calcShortestPathsSubset_v4" "$V2/myPy/ttgAnalysisMultip_v2.py" || die "V2 chua co P2 (git pull?)"
grep -q -E "def calcShortestPathsSubset_v(3p|4)" "$V1/myPy/ttgAnalysisMultip_v2.py" && die "V1 khong phai code golden"
for f in t2_common.py t2_run.py t2_make_sample.py; do
  cmp -s "$T1/$f" "$T2D/$f" || die "$f o 2 repo khac nhau (git pull ca 2 repo)"
done
for R in "$V1" "$V2"; do
  for f in GttTransit_v2.pkl dfNdDetails_v2.pkl dfAllTransfers.pkl stopPairsDist.pkl; do
    p=$R/myPy/outputs/pickles/$f
    [ -f "$p" ] && [ ! -L "$p" ] || die "thieu $p hoac la symlink (chay t2_setup_inputs.sh)"
  done
done
[ -e "$O1" ] && die "$O1 da ton tai - doi RUN_ID"
[ -e "$O2" ] && die "$O2 da ton tai - doi RUN_ID"
LOAD=$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || sysctl -n vm.loadavg | awk '{print $2}')
awk -v l="$LOAD" -v m="$MAX_LOAD" 'BEGIN{exit !(l<=m)}' || die "load average $LOAD > $MAX_LOAD (may dang ban, thoi gian se sai)"

mkdir -p "$O1" "$O2"
exec > >(tee -a "$O2/run_t2.log") 2>&1
echo "[$(ts)] ===== run_t2 START RUN_ID=$RUN_ID TESTS=$TESTS"
echo "V1=$V1 @ $(git -C "$V1" rev-parse --short HEAD)   V2=$V2 @ $(git -C "$V2" rev-parse --short HEAD)   load=$LOAD"
FAIL=0

run() {  # run <repo_tests_dir> <variant> <test_id> <rep>
  echo "[$(ts)] START $3 $2 r$4 ($1)"
  (cd "$1" && $PY t2_run.py --run-id "$RUN_ID" --test-id "$3" --variant "$2" --rep "$4" \
      --sample "out/$RUN_ID/sample_$3.json") || { echo "RUN FAILED $3 $2 r$4"; FAIL=1; }
  echo "[$(ts)] END   $3 $2 r$4"
}
cmpr() {  # cmpr <test_id> <P2 rep> <P0 rep>
  echo "[$(ts)] COMPARE $1 P2 r$2 vs P0 r$3"
  (cd "$T2D" && $PY t2_compare.py --test "out/$RUN_ID/$1_P2_r$2" --ref "$O1/$1_P0_r$3" --ref-repo-root "$V1")
  local rc=$?; echo "[$(ts)] COMPARE $1 P2 r$2 vs P0 r$3 EXIT=$rc"; [ $rc -eq 0 ] || FAIL=1
}
sample() {  # sample <test_id> <nfr> <nto> <seed>
  (cd "$T2D" && $PY t2_make_sample.py --run-id "$RUN_ID" --test-id "$1" --window "$WINDOW" \
      --n-stopfr "$2" --n-stopto "$3" --seed "$4") || die "khong sinh duoc sample $1"
  cp -p "$O2/sample_$1.json" "$O1/sample_$1.json"   # moi repo doc sample trong chinh no
}

for T in $TESTS; do
  case $T in
    T2a)  # mau nho: P0 va P2 moi ben REPS lan, xen ke de trung hoa troi thoi gian
      sample T2a "$T2A_NFR" "$T2A_NTO" "$T2A_SEED"
      for r in $(seq 1 "$T2A_REPS"); do run "$T1" v3 T2a "$r"; run "$T2D" v4 T2a "$r"; done
      for r in $(seq 1 "$T2A_REPS"); do cmpr T2a "$r" "$r"; done ;;
    T2b)  # mau chinh: toan bo stopTo; P0 rat lau nen chay 1 lan, P2 REPS lan
      sample T2b "$T2B_NFR" "$T2B_NTO" "$T2B_SEED"
      run "$T2D" v4 T2b 1; run "$T1" v3 T2b 1
      for r in $(seq 2 "$T2B_P2_REPS"); do run "$T2D" v4 T2b "$r"; done
      for r in $(seq 1 "$T2B_P2_REPS"); do cmpr T2b "$r" 1; done ;;
    T2x)  # chi dung cho tu kiem tren du lieu gia lap (SMOKE): 1 lan moi ben
      sample T2x "$T2A_NFR" "$T2A_NTO" "$T2A_SEED"
      run "$T1" v3 T2x 1; run "$T2D" v4 T2x 1; cmpr T2x 1 1 ;;
    *) echo "TESTS khong hop le: $T"; FAIL=1 ;;
  esac
done

(cd "$T2D" && $PY t2_summary.py --run-id "$RUN_ID" --ref-repo-root "$V1") || FAIL=1
echo "[$(ts)] ===== run_t2 XONG"
echo "EXIT=$FAIL"
exit $FAIL
