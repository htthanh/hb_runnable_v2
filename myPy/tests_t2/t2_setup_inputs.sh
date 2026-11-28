#!/usr/bin/env bash
# T2 (EXP-HB-004) - Buoc 0: dat 4 pickle input VAO TRONG moi repo (copy, khong symlink) va doi chieu sha256.
# Chi chay khi Thanh ra lenh. Khong xoa/ghi de file da co: neu file da co thi chi kiem sha256.
#   GOLD : thu muc busnet-master-original (nguon pickle, chi doc)
#   V1   : clone hb_runnable   (P0)      V2 : clone hb_runnable_v2 (P2)
set -euo pipefail
GOLD=${GOLD:-$HOME/htthanhdata/src/busnet-master-original}
V1=${V1:-$HOME/hb_runnable}
V2=${V2:-$HOME/hb_runnable_v2}
FILES="GttTransit_v2.pkl dfNdDetails_v2.pkl dfAllTransfers.pkl stopPairsDist.pkl"
SHA=$(command -v sha256sum >/dev/null && echo "sha256sum" || echo "shasum -a 256")

for R in "$V1" "$V2"; do
  D=$R/myPy/outputs/pickles
  mkdir -p "$D" "$R/myPy/tests_t2/out"
  for f in $FILES; do
    if [ -L "$D/$f" ]; then echo "ERROR: $D/$f la symlink"; exit 1; fi
    if [ -e "$D/$f" ]; then echo "[keep] $D/$f da co"; else echo "[copy] $GOLD/myPy/outputs/pickles/$f -> $D/"; cp -p "$GOLD/myPy/outputs/pickles/$f" "$D/"; fi
  done
done

echo "[sha256] tinh cho GOLD, V1, V2 (moi ben ~5 GB)..."
(cd "$GOLD/myPy/outputs/pickles" && $SHA $FILES) > /tmp/t2_sha_gold.$$
for R in "$V1" "$V2"; do
  (cd "$R/myPy/outputs/pickles" && $SHA $FILES) > "$R/myPy/tests_t2/out/pickles_sha256.txt"
  if diff -q /tmp/t2_sha_gold.$$ "$R/myPy/tests_t2/out/pickles_sha256.txt" >/dev/null; then
    echo "[ok] $R: 4 pickle trung sha256 voi GOLD"
  else
    echo "ERROR: $R: sha256 khac GOLD"; diff /tmp/t2_sha_gold.$$ "$R/myPy/tests_t2/out/pickles_sha256.txt" || true; rm -f /tmp/t2_sha_gold.$$; exit 1
  fi
done
rm -f /tmp/t2_sha_gold.$$
echo "XONG: input da nam trong ca 2 repo."
