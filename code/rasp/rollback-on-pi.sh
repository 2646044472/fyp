#!/usr/bin/env bash
set -eu
dir="$HOME/.local/share/palm-capture-station"
bak="${1:?Pass the backup directory printed by install-on-pi.sh}"
case "$bak" in "$dir"/best-frame-rollback-*) ;; *) echo "Unknown backup path" >&2; exit 2;; esac
test -f "$bak/capture_station.py"
cp -p "$bak/capture_station.py" "$dir/"
for x in enrollment_best_frame.py enrollment_review.py ranked_window.py enrollment_window_adapter.py; do
 if test -f "$bak/$x"; then cp -p "$bak/$x" "$dir/"; else rm -f "$dir/$x"; fi
done
systemctl --user restart palm-capture-station
