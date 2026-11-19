#!/usr/bin/env bash
# Ordered, reproducible build. Never run the one-off revision patch here.
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-$(command -v blender || true)}"
if [[ -z "$BLENDER_BIN" && -x /var/tmp/blender/blender ]]; then BLENDER_BIN=/var/tmp/blender/blender; fi
if [[ -z "$BLENDER_BIN" || ! -x "$BLENDER_BIN" ]]; then echo 'Install Blender 4.2 LTS and set BLENDER_BIN to its executable.' >&2; exit 2; fi
BLENDER_LIB="$(dirname "$BLENDER_BIN")/lib"
export LD_LIBRARY_PATH="$BLENDER_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export OMP_NUM_THREADS=2
python3 -m shipdesign.leonidas_ii
python3 tools/leonidas_materials.py
"$BLENDER_BIN" -b -t 2 --python-exit-code 1 -P blender/leonidas_ii/build.py
python3 tools/compact_leonidas_blend.py
"$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P blender/leonidas_ii/audit_structure.py
"$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P blender/leonidas_ii/audit_details.py
LII_GAME_DETAIL=1 "$BLENDER_BIN" -b -t 2 --python-exit-code 1 -P blender/leonidas_ii/build.py
python3 tools/prepare_leonidas_game.py
# The independent micro-part screens operate on both actual matching saved
# sources, with no old-source override/candidate escape. Not visual approval.
BLENDER_BIN="$BLENDER_BIN" bash tools/audit_leonidas_micro.sh
# Source-matched actual stair polygons and exposed-side overlap negatives.
"$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P tools/audit_leonidas_stair_joinery.py
LII_GAME_DETAIL=1 "$BLENDER_BIN" -b exports/leonidas_ii/build/Aurelian_Game_Source.blend -t 2 --python-exit-code 1 -P tools/audit_leonidas_stair_joinery.py
python3 tools/record_leonidas_export_inputs.py --begin
"$BLENDER_BIN" -b exports/leonidas_ii/build/Aurelian_Game_Source.blend -t 2 --python-exit-code 1 -P blender/leonidas_ii/export_game.py
python3 tools/record_leonidas_export_inputs.py --complete
python3 tools/package_leonidas_ii.py
# Fresh builds MUST recheck the actual saved GAME .blend/data. Receipt-only
# delivered-package mode is never a substitute for these present build inputs.
python3 tools/check_leonidas_micro_delivery.py --require-saved-sources
python3 tools/audit_leonidas_volumes.py
python3 tools/validate_leonidas_ii.py
python3 tools/publish_leonidas_dimensions.py
if [[ "${LII_RENDER:-0}" == 1 ]]; then
 export BLENDER_BIN
 bash tools/render_leonidas_evidence.sh
fi
echo 'Built artifacts. No Studio/live-playtest acceptance or git publication is implied.'
