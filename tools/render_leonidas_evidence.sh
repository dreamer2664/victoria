#!/usr/bin/env bash
# Serial Blender -> standalone OIDN batches. Never run beside another Blender.
# All imagery comes from the delivered source; no concept/image synthesis.
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-$(command -v blender || true)}"
if [[ -z "$BLENDER_BIN" && -x /var/tmp/blender/blender ]]; then BLENDER_BIN=/var/tmp/blender/blender; fi
if [[ -z "$BLENDER_BIN" || ! -x "$BLENDER_BIN" ]]; then echo 'Set BLENDER_BIN to Blender 4.2 LTS.' >&2; exit 2; fi
BLENDER_LIB="$(dirname "$BLENDER_BIN")/lib"
export LD_LIBRARY_PATH="$BLENDER_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" OMP_NUM_THREADS=2
export LII_SAMPLES="${LII_SAMPLES:-12}" LII_AUDIT_SAMPLES="${LII_AUDIT_SAMPLES:-6}" LII_RESUME="${LII_RESUME:-1}"
for group in ${LII_GROUPS:-public accommodation service engineering exterior plans rooms}; do
 echo "EVIDENCE GROUP BEGIN $group $(date -u +%FT%TZ)"
 "$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P blender/leonidas_ii/render.py -- "$group" "${LII_RENDER_PERCENT:-100}"
 OIDN_LIBRARY="$BLENDER_LIB/libOpenImageDenoise.so.2" python3 tools/denoise_leonidas_renders.py
 echo "EVIDENCE GROUP FINISHED $group $(date -u +%FT%TZ)"
done
echo 'Actual-model evidence created. Visual inspection is a separate acceptance step.'
