# hb_busnet_runnable — Thời gian chạy theo từng step

_Ngày lập: 2026-11-16. Nguồn: 9 log file trong `myPy/` (liệt kê ở §6) + `myPy/profile.out` (cProfile của step 2)._
_Phần cứng (theo log): server Linux, `cpu_count() = 50`, RAM ≈ 125,8 GiB (`vm_total = 128798.6 MiB`), swap 8 GiB. Python 3.13 (miniconda env `htt_env`)._

**Quy ước**
- Mọi thời gian đều ghi ở 4 đơn vị: **Giây | Phút | Giờ | Ngày**. Quy đổi: 1 phút = 60 s, 1 giờ = 3.600 s, 1 ngày = 86.400 s.
- Định dạng số kiểu Việt Nam: `.` ngăn cách hàng nghìn, `,` là dấu thập phân.
- Nguồn của từng con số: **[log]** = đọc trực tiếp từ dòng `Time taken*` hoặc timestamp trong log; **[tính]** = tôi tính từ hiệu hai timestamp; **[profile]** = lấy từ `profile.out`; **[suy luận]** = chưa kiểm chứng.

---

## 1. Tổng quan pipeline (`main.py`)

| Step | Tên trong `main.py` | Hàm chính | #process | Giây | Phút | Giờ | Ngày | % tổng | Nguồn |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | CONSTRUCTS GRAPH IN L-SPACE AND DFROUTES | `graph_v2.construct_G_dfRoutes` | 1 | 756 | 12,6 | 0,21 | 0,009 | 0,04% | [log] |
| 2 | TOPOLOGICAL ANALYSIS | `topoAnalysis.topoMain` | 2 (betweenness) | 130.644 | 2.177,4 | 36,29 | 1,512 | 6,39% | [log] |
| 3 | TOPO ANALYSIS POSTPROCESSING | `topoPostproc.main_topoPostproc` | 1 | 31,75 | 0,53 | 0,009 | 0,0004 | ≈0% | [log] |
| 4 | TEMPORAL TOPOLOGICAL ANALYSIS | `ttGraph_v2.makeTopoTempGraphMultip` | 10 | 137.915 | 2.298,6 | 38,31 | 1,596 | 6,75% | [log] |
| 5a | TEMPORAL SHORTEST PATH — 07:00–10:00 | `ttgAnalysisMultip_v2.calcShortestPathsMultip` | 50 | 512.462 | 8.541,0 | 142,35 | 5,931 | 25,07% | [log] |
| 5b | TEMPORAL SHORTEST PATH — 12:00–15:00 | như trên | 50 | 445.007 | 7.416,8 | 123,61 | 5,151 | 21,77% | [log] |
| 5c | TEMPORAL SHORTEST PATH — 17:00–20:00 | như trên | 50 | 414.164 | 6.902,7 | 115,05 | 4,794 | 20,26% | [log] |
| 6 | TEMPORAL SHORTEST PATH POSTPROCESSING (3 khung giờ) | `ttgPostprocMultip.main_ttgPostprocMultip` | 1 | 403.320 | 6.722,0 | 112,03 | 4,668 | 19,73% | [log] |
| | **Tổng** | | | **2.044.300** | **34.071,7** | **567,86** | **23,661** | **100%** | [tính] |

**Gộp theo nhóm**

| Nhóm | Giây | Phút | Giờ | Ngày | % tổng |
|---|---:|---:|---:|---:|---:|
| Step 5 (cả 3 khung giờ) | 1.371.632 | 22.860,5 | 381,01 | 15,875 | 67,10% |
| Step 6 | 403.320 | 6.722,0 | 112,03 | 4,668 | 19,73% |
| Step 4 | 137.915 | 2.298,6 | 38,31 | 1,596 | 6,75% |
| Step 2 | 130.644 | 2.177,4 | 36,29 | 1,512 | 6,39% |
| Step 1 + 3 | 788 | 13,1 | 0,22 | 0,009 | 0,04% |

> Lưu ý: các step được chạy **tách rời**. Mỗi lần chạy, `main.py` được comment/uncomment để chỉ chạy một step và load pickle của step trước. Các run nằm trong khoảng 2025-11-09 đến 2025-12-19. Tổng 23,7 ngày là tổng thời gian tính toán của các step, không phải một lần chạy liên tục.

---

## 2. Chi tiết từng step

### Step 1 — Construct G (L-space) & dfRoutes

| Trường hợp | Giây | Phút | Giờ | Ngày | Nguồn |
|---|---:|---:|---:|---:|---|
| Dựng từ đầu (2025-11-09 15:24:53 → 15:37:30) | 756 | 12,6 | 0,21 | 0,009 | [log] |
| Đã có `G.pkl` + `dfRoutes.pkl`, chỉ load pickle (đầu log `time_taken2`) | 1,90 | 0,03 | 0,0005 | 0,00002 | [log] |

### Step 2 — Topological analysis (2025-11-12 14:25:10 → 2025-11-14 02:42:35)

| Phần | Hàm | Giây | Phút | Giờ | Ngày | % step | Nguồn |
|---|---|---:|---:|---:|---:|---:|---|
| **Tổng step 2** | | **130.644** | **2.177,4** | **36,29** | **1,512** | 100% | [log] |
| Static betweenness (2 process × 2.175 stop) | `topoNode.calcBetwCentralMultip` | 114.309 | 1.905,2 | 31,75 | 1,323 | 87,5% | [profile] |
| Proximity density | `topoNode.calcProxDensity` | 15.049 | 250,8 | 4,18 | 0,174 | 11,5% | [profile] |
|  └ lọc boolean pandas (`==`, `>`, `<=`, `&`, `astype`, `nonzero`) | | ≈ 8.900 | 148,3 | 2,47 | 0,103 | | [profile] |
|  └ geodesic distance (`geopy`, 18.740.377 lần gọi) | `calcGeoDist` | ≈ 4.680 | 78,0 | 1,30 | 0,054 | | [profile] |
| Shortest path → DataFrame | `topoPath.convertToDataframe` | 755 | 12,6 | 0,21 | 0,009 | 0,6% | [profile] |
| Shortest paths tĩnh (networkx Dijkstra, 13.050 lần) | `topoPath.calcShortestPaths_v3` | 323 | 5,4 | 0,09 | 0,004 | 0,2% | [profile] |
| `pickle.dump` (10 file) | | 123 | 2,0 | 0,03 | 0,001 | 0,1% | [profile] |
| `assignProxDensityToG` + `assignBetwCentralityToG` | | 37 | 0,6 | 0,01 | 0,0004 | ≈0% | [profile] |

- Tổng thời gian trong profile là 130.649 s, khớp với số trong log.
- Run này chậm hơn các run tháng 10 (≈ 70.500 s ≈ 19,6 h). Nguyên nhân chính là betweenness chỉ chạy **2 process**, theo log `calcBetwCentralMultip part 0/1 started, 2175 stops`.

### Step 3 — Topo postprocessing

| Run | Giây | Phút | Giờ | Ngày | Nguồn |
|---|---:|---:|---:|---:|---|
| 2025-11-14 08:07:59 → 08:08:31 | 31,75 | 0,53 | 0,009 | 0,0004 | [log] |
| Run tháng 10 (`20251008_2_10_time_taken4`) | 32,95 | 0,55 | 0,009 | 0,0004 | [log] |

### Step 4 — Temporal graph (2025-11-14 08:36:15 → 2025-11-15 22:54:50)

| Phần | Hàm | Giây | Phút | Giờ | Ngày | Nguồn |
|---|---|---:|---:|---:|---:|---|
| **Tổng step 4** | | **137.915** | **2.298,6** | **38,31** | **1,596** | [log] |
| Dựng transit graph (253 route, chạy tuần tự), 08:36:15 → 15:59:43 | `addTransitEdges` | 26.608 | 443,5 | 7,39 | 0,308 | [tính] |
| Sinh transfer edges (10 process × 435 stop) + consolidate + pickle, 15:59:43 → 22:54:50 | `mkTransferEdgesMultip` + `consolidateTransferEdges` | 111.307 | 1.855,1 | 30,92 | 1,288 | [tính] |
|  └ riêng sinh transfer edges (xấp xỉ) | `mkTransferEdgesSubset` | ≈ 110.000 | 1.833,3 | 30,56 | 1,273 | [tính, xấp xỉ] |
|  └ riêng đọc 10 file CSV | | 248 | 4,1 | 0,07 | 0,003 | [log] |
| Run tháng 10: transit graph load từ pickle, 10 process | | 94.294 | 1.571,6 | 26,19 | 1,091 | [log] |

Dòng `finished mkTransferEdgesMultip` trong log không có timestamp. Vì vậy ranh giới giữa phần sinh edge và phần consolidate chỉ là xấp xỉ. Tổng 111.307 s của hai phần thì chính xác.

### Step 5 — Temporal shortest paths (50 process × 87 stopFr → 4.350 stopTo)

**5.1 Tổng theo khung giờ**

| Khung giờ | Bắt đầu → kết thúc | Giây | Phút | Giờ | Ngày | Nguồn |
|---|---|---:|---:|---:|---:|---|
| 07–10 | 2025-12-06 17:17:30 → 2025-12-12 15:38:32 | 512.462 | 8.541,0 | 142,35 | 5,931 | [log] |
| 12–15 | 2025-11-26 05:22:29 → 2025-12-01 08:59:16 | 445.007 | 7.416,8 | 123,61 | 5,151 | [log] |
| 17–20 | 2025-12-01 11:55:54 → 2025-12-06 06:58:38 | 414.164 | 6.902,7 | 115,05 | 4,794 | [log] |
| **Tổng 3 khung** | | **1.371.632** | **22.860,5** | **381,01** | **15,875** | [tính] |

**5.2 Load dữ liệu + `addTransferEdgesAllStops` (trước khi tách process)**

| Khung giờ | Wait / walk edges | Giây | Phút | Giờ | Ngày | Nguồn |
|---|---|---:|---:|---:|---:|---|
| 07–10 | 2.643.551 / 11.729.368 | 102 (add edges 80,4) | 1,7 | 0,03 | 0,001 | [tính]/[log] |
| 12–15 | 2.092.179 / 9.264.335 | 86 (add edges 64,9) | 1,4 | 0,02 | 0,001 | [tính]/[log] |
| 17–20 | 1.889.011 / 8.616.697 | 80 (add edges 60,5) | 1,3 | 0,02 | 0,001 | [tính]/[log] |

**5.3 Thời điểm hoàn thành của từng process** (min / trung vị / max trên 50 process) [tính]

| Khung giờ | Thống kê | Giây | Phút | Giờ | Ngày |
|---|---|---:|---:|---:|---:|
| 07–10 | Sớm nhất | 483.800 | 8.063,3 | 134,39 | 5,600 |
| | Trung vị | 502.400 | 8.373,3 | 139,56 | 5,815 |
| | Muộn nhất | 512.300 | 8.538,3 | 142,31 | 5,929 |
| 12–15 | Sớm nhất | 426.400 | 7.106,7 | 118,44 | 4,935 |
| | Trung vị | 435.850 | 7.264,2 | 121,07 | 5,045 |
| | Muộn nhất | 444.900 | 7.415,0 | 123,58 | 5,149 |
| 17–20 | Sớm nhất | 370.500 | 6.175,0 | 102,92 | 4,288 |
| | Trung vị | 392.450 | 6.540,8 | 109,01 | 4,542 |
| | Muộn nhất | 414.100 | 6.901,7 | 115,03 | 4,793 |

**5.4 Thời gian trung bình cho mỗi stopFr trên một process** (= trung vị / 87) [tính]

| Khung giờ | Giây | Phút | Giờ | Ngày |
|---|---:|---:|---:|---:|
| 07–10 | 5.775 | 96,2 | 1,60 | 0,067 |
| 12–15 | 5.010 | 83,5 | 1,39 | 0,058 |
| 17–20 | 4.511 | 75,2 | 1,25 | 0,052 |

- Hơn 99,9% thời gian của step 5 nằm trong vòng lặp `calcShortestPathsSubset_v3`.
- Thời gian tỉ lệ khá sát với số transfer edges của từng khung giờ [suy luận].
- Mỗi khung giờ có 6–7 stopFr bị bỏ qua (`WARNING: … has no nodes`).

### Step 6 — Temporal postprocessing (2025-12-14 12:38:12 → 2025-12-19 04:40:12)

| Khung giờ | Phần | Hàm | Giây | Phút | Giờ | Ngày | Nguồn |
|---|---|---|---:|---:|---:|---:|---|
| 07–10 | Consolidate + route IDs + prox. density | `runStuffOnBUDF` (trước betweenness) | 12.395 | 206,6 | 3,44 | 0,143 | [tính] |
| | └ trong đó `allRouteIDList` | `getRouteIDs` | 2.539 | 42,3 | 0,71 | 0,029 | [log] |
| | **Temporal betweenness** (1 process, 4.350 stop) | `calcBetwCentralities` | **122.740** | 2.045,7 | 34,09 | 1,421 | [tính] |
| 12–15 | Consolidate + route IDs + prox. density | | 12.513 | 208,6 | 3,48 | 0,145 | [tính] |
| | └ trong đó `allRouteIDList` | | 2.533 | 42,2 | 0,70 | 0,029 | [log] |
| | **Temporal betweenness** | | **124.532** | 2.075,5 | 34,59 | 1,441 | [tính] |
| 17–20 | Consolidate + route IDs + prox. density | | 10.678 | 178,0 | 2,97 | 0,124 | [tính] |
| | └ trong đó `allRouteIDList` | | 1.979 | 33,0 | 0,55 | 0,023 | [log] |
| | **Temporal betweenness** | | **115.664** | 1.927,7 | 32,13 | 1,339 | [tính] |
| — | Vẽ violin plot / bản đồ cuối | | 4.798 | 80,0 | 1,33 | 0,056 | [tính] |
| | **Tổng step 6** | | **403.320** | **6.722,0** | **112,03** | **4,668** | [log] |
| | └ tổng betweenness 3 khung (90,0%) | | 362.936 | 6.048,9 | 100,82 | 4,201 | [tính] |

- Thời gian cho mỗi stop: 07–10 ≈ 28,2 s (0,47 phút), 12–15 ≈ 28,6 s (0,48 phút), 17–20 ≈ 26,6 s (0,44 phút).
- Betweenness chạy 1 process vì `ttgPostprocMultip.py:457` gọi với `nProcesses=1`.

---

## 3. Xếp hạng điểm nóng (hotspot)

| # | Hotspot | File:hàm | Giây | Phút | Giờ | Ngày | % tổng |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | Temporal shortest paths (3 khung) | `ttgAnalysisMultip_v2.py:calcShortestPathsSubset_v3` | 1.371.632 | 22.860,5 | 381,01 | 15,875 | 67,1% |
| 2 | Temporal betweenness, 1 process (3 khung) | `ttgPostprocMultip.py:calcBetwCentralities` | 362.936 | 6.048,9 | 100,82 | 4,201 | 17,8% |
| 3 | Static betweenness, 2 process | `topoNode.py:calcBetwCentralities` | 114.309 | 1.905,2 | 31,75 | 1,323 | 5,6% |
| 4 | Sinh transfer edges, 10 process | `ttGraph_v2.py:mkTransferEdgesSubset` | ≈ 110.000 | 1.833,3 | 30,56 | 1,273 | ≈ 5,4% |
| 5 | Consolidate + route IDs + temporal prox. density (3 khung) | `ttgPostprocMultip.py:runStuffOnBUDF` | 35.586 | 593,1 | 9,88 | 0,412 | 1,7% |
| 6 | Dựng transit graph tuần tự | `ttGraph_v2.py:addTransitEdges` | 26.608 | 443,5 | 7,39 | 0,308 | 1,3% |
| 7 | Static proximity density | `topoNode.py:calcProxDensity` | 15.049 | 250,8 | 4,18 | 0,174 | 0,7% |

Bốn hotspot đầu (#1–#4) đã chiếm khoảng **96%** tổng thời gian.

---

## 4. Run dở dang (không tính vào tổng)

| Log | Nội dung | Giây | Phút | Giờ | Ngày | Nguồn |
|---|---|---:|---:|---:|---:|---|
| `20251008_2_10_time_taken4.txt` | Step 5, 10 process × 435 stopFr. Dừng khi mới xong 3.674/4.350 stopFr (84,5%) | 1.750.000 | 29.166,7 | 486,11 | 20,255 | [log] |

Log này không ghi khung giờ. Số wait edges (2.643.551) trùng với khung 07–10, nhưng điều đó chưa đủ để kết luận đây là khung 07–10 (chưa xác minh).

## 5. Lưu ý khi dùng các số này
- Các step chạy với **số process khác nhau** (1, 2, 10, 50). Vì vậy đây là wall-clock thực tế, không dùng để so chi phí CPU giữa các step.
- Ba khung giờ của step 5 chạy trên cùng server ở các thời điểm khác nhau. Chưa kiểm chứng được máy có bị tải từ job khác trong lúc chạy hay không.

## 6. Log file đã đọc

| File | Nội dung |
|---|---|
| `myPy/log_busnet_20251008_2_10_time_taken4.txt` | Step 3 (32,95 s), Step 4 (94.294 s), Step 5 dở dang (10 process); không có timestamp |
| `myPy/log_busnet_20251109_2_10_time_taken1.txt` | Step 1 = 756 s |
| `myPy/log_busnet_20251109_2_10_time_taken2.txt` | Step 1 (load pickle 1,9 s) + Step 2 = 130.644 s |
| `myPy/log_busnet_20251109_2_10_time_taken3.txt` | Step 3 = 31,75 s |
| `myPy/log_busnet_20251109_2_10_time_taken4.txt` | Step 4 = 137.915 s |
| `myPy/log_busnet_20251109_2_50_time_taken5_7_10_nodelete.txt` | Step 5, 07–10 = 512.462 s |
| `myPy/log_busnet_20251109_2_50_time_taken5_12_15_nodelete.txt` | Step 5, 12–15 = 445.007 s |
| `myPy/log_busnet_20251109_2_50_time_taken5_17_20_nodelete.txt` | Step 5, 17–20 = 414.164 s |
| `myPy/log_busnet_20251109_2_50_time_taken6.txt` | Step 6 = 403.320 s |
| `myPy/profile.out` | cProfile của Step 2 (dùng cho breakdown ở §2) |
