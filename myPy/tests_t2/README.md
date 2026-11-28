# T2 (EXP-HB-004) — P2 (`hb_runnable_v2`) so với P0 (`hb_runnable`, code golden)

Mục tiêu:
1. **Tính đúng:** output bước 5 của P2 (`calcShortestPathsSubset_v4`) phải **giống hệt** output của P0 (`calcShortestPathsSubset_v3` trong code golden) trên cùng mẫu, cả về giá trị lẫn thứ tự record.
2. **Thời gian:** đo thời gian hàm bước 5 của P2 so với P0 trên cùng máy, cùng mẫu, 1 process, chạy tuần tự.

## Khác T0/T1 ở đâu (tránh nhầm kết quả)

| | T0/T1 (EXP-HB-003) | T2 (EXP-HB-004) |
|---|---|---|
| Thư mục script | `myPy/tests/` (chỉ v2) | `myPy/tests_t2/` (cả 2 repo) |
| Thư mục output | `myPy/tests/out/` | `myPy/tests_t2/out/<RUN_ID>/` trong **từng** repo |
| Oracle | golden 580h (`busnet-master-original`, ngoài repo) | P0 chạy lại trong `hb_runnable`, input trong `hb_runnable` |
| Seed | 2026, 7 | 11 (T2a), 13 (T2b); script **cấm** 2026 và 7 |
| Tên lần chạy | — | `RUN_ID` bắt buộc bắt đầu bằng `T2-` |
| Manifest | không có | `manifest.json` mỗi lần chạy; `t2_compare.py` từ chối so khi thiếu hoặc lệch manifest |
| tmux / script | `t01` / `run_t01.sh` | `t2` / `run_t2.sh` |

## Cách ly input/output
- Mỗi repo chỉ đọc input trong `<repo>/myPy/outputs/pickles/` (4 pickle, **copy**, không symlink). `t2_setup_inputs.sh` copy từ `busnet-master-original` và kiểm sha256 của cả 2 repo với nguồn.
- `t2_run.py` chỉ import code của **chính repo chứa nó**, chỉ ghi vào `<repo>/myPy/tests_t2/out/`. Repo `hb_runnable` chỉ được chạy `v3` (P0), repo `hb_runnable_v2` chỉ được chạy `v4` (P2) — kiểm qua remote origin.
- File mẫu sinh ở v2 rồi được **copy** sang `hb_runnable` (mỗi repo đọc mẫu trong chính nó); sha256 của mẫu được so trong manifest.
- `t2_compare.py` (ở v2) đọc output P0 trong `hb_runnable` ở chế độ chỉ đọc, sau khi kiểm manifest: đúng repo/biến thể, cùng `RUN_ID`, `test_id`, seed, sha256 mẫu, sha256 4 pickle, cùng host và phiên bản python/igraph/pandas/numpy, cả 2 repo không có file đã track bị sửa.

| File | Có ở | Việc |
|---|---|---|
| `t2_common.py`, `t2_run.py`, `t2_make_sample.py` | cả 2 repo (giống hệt; `run_t2.sh` kiểm bằng `cmp`) | helpers, chạy bước 5 của repo đó, sinh mẫu |
| `t2_compare.py` | v2 | so P2 với P0: list giống hệt (cả thứ tự) + so theo khoá `(stopFr, stopTo)` |
| `t2_summary.py` | v2 | bảng thời gian (mean ± std, speedup, speedup từng stopFr, nSpCalls, maxRSS) |
| `t2_setup_inputs.sh` | v2 | Bước 0: copy 4 pickle vào 2 repo, kiểm sha256 |
| `run_t2.sh` | v2 | preflight + T2a + T2b + compare + summary |

## Thiết kế test

| Test | Mẫu | Lần chạy (thứ tự) | Mục đích |
|---|---|---|---|
| **T2a** | 3 stopFr × 200 stopTo, seed 11 | P0 r1, P2 r1, P0 r2, P2 r2, P0 r3, P2 r3 (xen kẽ) | kiểm nhanh tính đúng; thời gian có lặp lại (mean ± std) cả 2 bên |
| **T2b** | 5 stopFr × **toàn bộ** stopTo, seed 13 | P2 r1, P0 r1, P2 r2, P2 r3 | phép thử chính: đủ stopTo như pipeline thật; speedup tổng và từng stopFr |

Tiêu chí:
- Đúng: mọi phép so `EXIT=0` (list giống hệt, 0 khoá thiếu/thừa/trùng, 0 sai khác trường).
- Thời gian: báo `s/stopFr` mean ± std, speedup = mean(P0)/mean(P2) và khoảng [min, max]; speedup từng stopFr (median, min, max). Chỉ tính thời gian hàm bước 5, không gồm load và sha256.

Ước lượng [suy luận, chưa đo]: T2a ≈ 45 phút (P0 ≈ 9 phút/lần như T1a); T2b ≈ 5,5–6 giờ, gần hết là P0 (≈ 3.900 s/stopFr × 5). Tổng ≈ 6,5 giờ.

## Lệnh trên server (chỉ chạy khi Thanh ra lệnh)
```bash
cd ~/hb_runnable && git pull          # cần có myPy/tests_t2/
cd ~/hb_runnable_v2 && git pull       # cần có P2 + myPy/tests_t2/
bash ~/hb_runnable_v2/myPy/tests_t2/t2_setup_inputs.sh      # Bước 0: input vào trong 2 repo + sha256
tmux new -s t2
conda activate htt_env
cd ~/hb_runnable_v2/myPy/tests_t2
RUN_ID=T2-$(date +%Y%m%d) bash run_t2.sh                     # T2a + T2b; log: out/$RUN_ID/run_t2.log
# Ctrl-b d để rời tmux; job vẫn chạy khi ngắt SSH
```
Kết quả: `~/hb_runnable_v2/myPy/tests_t2/out/<RUN_ID>/` (`run_t2.log`, `t2_summary.md/json`, `T2*_P2_r*/compare_vs_*.json`) và `~/hb_runnable/myPy/tests_t2/out/<RUN_ID>/` (output P0).
Exit code từng phép so: `0` khớp, `1` sai khác, `3` manifest không khớp (không so).
