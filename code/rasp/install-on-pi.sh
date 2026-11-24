#!/usr/bin/env bash
set -eu
cd -- "$(dirname -- "$0")"
dir="$HOME/.local/share/palm-capture-station"
venv="$HOME/palm_demo/.venv/bin/python"
test -x "$venv" && test -f "$dir/capture_station.py"
systemctl --user cat palm-capture-station | grep -qF '/palm-capture-station/capture_station.py'
"$venv" verify_best_frame.py
"$venv" verify_review.py
"$venv" verify_ranked_window.py
"$venv" verify_adapter.py
module_files=(enrollment_archive.py enrollment_best_frame.py enrollment_review.py ranked_window.py enrollment_window_adapter.py)
stamp="$(date -u +%Y%m%dT%H%M%SZ)-$$"
backup="$dir/best-frame-rollback-$stamp"
mkdir -m 700 "$backup"
cp -p "$dir/capture_station.py" "$backup/"
for x in "${module_files[@]}"; do
 if test -f "$dir/$x"; then cp -p "$dir/$x" "$backup/"; fi
done
rollback() {
  cp -p "$backup/capture_station.py" "$dir/capture_station.py"
  for x in "${module_files[@]}"; do
   if test -f "$backup/$x"; then cp -p "$backup/$x" "$dir/"; else rm -f "$dir/$x"; fi
  done
  systemctl --user restart palm-capture-station || true
}
trap 'rollback; printf "%s\n" "Update failed; restored original capture station." >&2' ERR
install -m 600 "${module_files[@]}" "$dir/"
install -m 600 capture_station.py "$dir/capture_station.py"
systemctl --user restart palm-capture-station
ready=no
for i in $(seq 1 20); do
 if curl --noproxy '*' -fsS --max-time 1 http://127.0.0.1:8088/enroll >/dev/null 2>&1; then ready=yes; break; fi
 sleep 1
done
test "$ready" = yes
trap - ERR
printf 'Capture station restarted. Previous code backed up under %s\n' "$backup"
printf 'Open /enroll with a new capture session. Real camera/candidate flow not tested by this installer.\n'
