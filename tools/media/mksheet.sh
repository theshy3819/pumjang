#!/bin/bash
# usage: mksheet.sh <srcdir> <name>
SRC="$1"; NAME="$2"
cd "/c/Users/shy38/AppData/Local/Temp/claude/12a9dc120ae2a867/81b09cc5-8455-4f97-8149-c070b55a9564/scratchpad"
OUT="/c/Users/shy38/AppData/Local/Temp/claude/12a9dc120ae2a867/81b09cc5-8455-4f97-8149-c070b55a9564/scratchpad/sheets/$NAME"
mkdir -p "$OUT/t"
i=0
: > "$OUT/index.txt"
find "$SRC" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) ! -name '._*' | sort | while read f; do
  n=$(printf "%03d" $i)
  echo "$n $(basename "$f")" >> "$OUT/index.txt"
  ffmpeg -y -loglevel error -i "$f" -frames:v 1 -vf "scale=260:260:force_original_aspect_ratio=decrease,pad=260:260:(ow-iw)/2:(oh-ih)/2:color=gray,drawtext=fontfile=arialbd.ttf:text='$n':x=4:y=4:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7" "$OUT/t/$n.jpg"
  i=$((i+1))
done
ffmpeg -y -loglevel error -framerate 1 -i "$OUT/t/%03d.jpg" -vf "tile=6x5:color=white" "$OUT/sheet_%02d.jpg"
echo "done $NAME $(wc -l < "$OUT/index.txt")"
