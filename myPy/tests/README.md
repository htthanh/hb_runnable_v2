# T0 / T1 — kiểm tra P1 (`calcShortestPathsSubset_v3p`) và giả thuyết của P2

Mọi script chạy từ thư mục `myPy/tests/` (chúng tự thêm `myPy/` vào `sys.path`). Không script nào sửa code gốc.

| File | Việc |
|---|---|
| `common.py` | load 4 pickle + `addTransferEdgesAllStops` + `allStops` (đúng như `calcShortestPathsMultip`), lấy mẫu tái lập (sorted + `random.Random(seed)`) |
| `t1_run.py` | chạy **một** biến thể (`v3` = P0 gốc, `v3p` = P1) trên mẫu (stopFr × stopTo), 1 process, gọi thẳng hàm gốc |
| `t1_compare.py` | so output theo khoá `(stopFr, stopTo)` với golden (thư mục 50 pickle) hoặc với một pickle khác |
| `t0_target_set.py` | kiểm tra path của igraph không phụ thuộc tập `to` + so quyết định v3 vs P2 mô phỏng |

## Bước 0 — cách ly (bắt buộc, trên server)
- `PROJECT_ROOT` trong `constants.py` được suy từ vị trí file (thư mục cha của `myPy/`), nên mỗi bản code chỉ đọc/ghi trong folder của chính nó. Clone `hb_runnable_v2` vào một thư mục **khác** golden.
- Input của v2 phải nằm **trong** v2: **copy** (không symlink) 4 pickle từ golden vào `<V2>/myPy/outputs/pickles/` và kiểm sha256.
- Script tự chặn: `--pickles`, `--out`, `--test`, `--sample` phải nằm trong folder v2 (kiểm bằng realpath). Golden chỉ được **đọc** qua `--ref`. `t1_run.py` từ chối ghi nếu `--out` đã có `shortestPaths_0.pkl`.

```bash
GOLD=/home/htthanh/htthanhdata/src/busnet-master-original      # golden 580h (chỉ đọc)
V2=<thư mục hb_runnable_v2 trên server>
REF=$GOLD/myPy/trashSite/gttShortestPaths/0700_1000
OUT=$V2/myPy/tests/out
mkdir -p $V2/myPy/outputs/pickles $OUT
for f in GttTransit_v2 dfNdDetails_v2 dfAllTransfers stopPairsDist; do cp -p $GOLD/myPy/outputs/pickles/$f.pkl $V2/myPy/outputs/pickles/; done
(cd $GOLD/myPy/outputs/pickles && sha256sum GttTransit_v2.pkl dfNdDetails_v2.pkl dfAllTransfers.pkl stopPairsDist.pkl) > $OUT/sha_gold.txt
(cd $V2/myPy/outputs/pickles   && sha256sum GttTransit_v2.pkl dfNdDetails_v2.pkl dfAllTransfers.pkl stopPairsDist.pkl) > $OUT/sha_v2.txt
diff $OUT/sha_gold.txt $OUT/sha_v2.txt && echo "pickles identical"
conda activate htt_env
cd $V2/myPy/tests
```
`--pickles` mặc định là `$V2/myPy/outputs/pickles`, nên các lệnh dưới không cần truyền.

## Bước 1 — oracle còn dùng được?
```bash
ls $REF/shortestPaths_*.pkl | wc -l                                  # phải = 50
ls -l --time-style=full-iso $REF | head -3                           # mtime ~ 2025-12-06 .. 12
ls -l --time-style=full-iso $GOLD/myPy/outputs/pickles/{GttTransit_v2,dfNdDetails_v2,dfAllTransfers,stopPairsDist}.pkl   # phải CŨ hơn 2025-12-06
python -c "import sys,igraph,pandas,numpy;print(sys.version,igraph.__version__,pandas.__version__,numpy.__version__)"
```

## Bước 2 — T1
```bash
# T1a: v3 gốc, 3 stopFr x 200 stopTo, so với golden  (=> môi trường tái lập được golden)
python t1_run.py --variant v3  --window 7,10 --n-stopfr 3 --n-stopto 200 --seed 2026 --out $OUT/t1a_v3  | tee $OUT/t1a_v3.log
python t1_compare.py --test $OUT/t1a_v3/shortestPaths_0.pkl --ref $REF --sample $OUT/t1a_v3/sample.json

# T1b: v3p trên CÙNG mẫu, so với golden và với v3
python t1_run.py --variant v3p --sample $OUT/t1a_v3/sample.json --out $OUT/t1b_v3p | tee $OUT/t1b_v3p.log
python t1_compare.py --test $OUT/t1b_v3p/shortestPaths_0.pkl --ref $REF --sample $OUT/t1a_v3/sample.json
python t1_compare.py --test $OUT/t1b_v3p/shortestPaths_0.pkl --ref $OUT/t1a_v3/shortestPaths_0.pkl --sample $OUT/t1a_v3/sample.json
grep "P1 finished" $OUT/t1b_v3p.log            # nSpCalls (= số lời gọi igraph của v3 trên cùng mẫu)

# T1c: v3p, 10 stopFr x TOÀN BỘ stopTo, so với golden (seed khác)
python t1_run.py --variant v3p --window 7,10 --n-stopfr 10 --n-stopto 0 --seed 7 --out $OUT/t1c_v3p | tee $OUT/t1c_v3p.log
python t1_compare.py --test $OUT/t1c_v3p/shortestPaths_0.pkl --ref $REF --sample $OUT/t1c_v3p/sample.json
```
`meta.json` trong mỗi `--out` có thời gian, s/stopFr, max RSS, phiên bản thư viện. So thời gian v3 vs v3p ở T1a/T1b là cùng máy, cùng mẫu.

## Bước 3 — T0 (sau khi T1 khớp 100%)
```bash
# chạy nhỏ trước, giới hạn 1 giờ; xem avg s/call rồi mới tăng --n-stopfr / --n-stopto
python t0_target_set.py --window 7,10 --n-stopfr 3 --n-stopto 50 --seed 2026 --max-seconds 3600 --out $OUT/t0 | tee $OUT/t0.log
```
Exit code: `0` khớp 100%, `1` có sai khác (dừng P2), `2` hết giờ nhưng chưa thấy sai khác. Report đầy đủ ở `$OUT/t0/t0_report.json`
(gồm `targets_b_max` / `max_rss_mib` để quyết định có cần P2b hay không, và `empty_to_nonempty_result` để kiểm hành vi igraph khi `to=[]`).
