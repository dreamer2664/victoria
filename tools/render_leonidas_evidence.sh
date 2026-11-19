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
# Refuse a mixed-generation serial run if a source/renderer is edited while
# earlier groups are rendering. Exact pixel/source hashes are still checked
# separately by the delivery validator and manual-review register.
source_file=models/leonidas_ii/Aurelian_1889.blend
renderer_file=blender/leonidas_ii/render.py
source_sha="$(sha256sum "$source_file" | cut -d' ' -f1)"
renderer_sha="$(sha256sum "$renderer_file" | cut -d' ' -f1)"
verify_identity() {
 [[ "$(sha256sum "$source_file" | cut -d' ' -f1)" == "$source_sha" && "$(sha256sum "$renderer_file" | cut -d' ' -f1)" == "$renderer_sha" ]] || {
  echo 'Master/renderer changed during serial evidence run; refusing mixed-source continuation.' >&2
  return 1
 }
}
echo "EVIDENCE MASTER $source_sha / RENDERER $renderer_sha"
for group in ${LII_GROUPS:-public accommodation service engineering exterior plans rooms crew_details refinement micro_details}; do
 verify_identity
 echo "EVIDENCE GROUP BEGIN $group $(date -u +%FT%TZ)"
 post_subdir=''
 if [[ "$group" == crew_details ]]; then
  # Additional 1600x1000 wall/roof-removed diagnostics; requires final
  # public images and preserves every common-renderer evidence identity.
  "$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P blender/leonidas_ii/render_crew_details.py
 elif [[ "$group" == refinement ]]; then
  post_subdir=refinement
  LII_RENDER_SUBDIR=refinement LII_SAMPLES=24 LII_ONLY=Detail_Exterior_Bridge,Detail_Exterior_Promenade,Detail_Promenade_Bench,Detail_Mast_Ladder,Detail_Funnel_Ladder,Detail_Lifebuoy_Hook,Detail_Wheelhouse_Framing "$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P blender/leonidas_ii/render.py -- refinement 100
 elif [[ "$group" == micro_details ]]; then
  post_subdir=micro
  # Retain the five sound original views, then replace four cameras that
  # were rejected during real pixel review. Per-view driver hashes stay
  # truthful: old pixels are never assigned the corrected driver's hash.
  LII_RENDER_SUBDIR=micro LII_SAMPLES=24 LII_ONLY="${LII_ONLY:-Micro_Dining_Tableware,Micro_Dining_Underside,Micro_Piano_Stool_Feet,Micro_Pantry_Crockery,Micro_Thrust_Bearings}" "$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P tools/render_leonidas_contact_details.py
  LII_RENDER_SUBDIR=micro LII_SAMPLES=24 "$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P tools/render_leonidas_contact_rechecks.py
 elif [[ "$group" == plans ]]; then
  # The three upper plans need explicit roof-object omission. The original
  # ceiling-only filter left the actual weather roofs opaque over rooms.
  LII_ONLY="${LII_ONLY:-Engineering_Structural_Skeleton,Plan_orlop,Plan_lower,Plan_main,Plan_saloon}" "$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P blender/leonidas_ii/render.py -- plans "${LII_RENDER_PERCENT:-100}"
  "$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P tools/render_leonidas_plan_rechecks.py
 else
  "$BLENDER_BIN" -b models/leonidas_ii/Aurelian_1889.blend -t 2 --python-exit-code 1 -P blender/leonidas_ii/render.py -- "$group" "${LII_RENDER_PERCENT:-100}"
 fi
 LII_RENDER_SUBDIR="$post_subdir" OIDN_LIBRARY="$BLENDER_LIB/libOpenImageDenoise.so.2" python3 tools/denoise_leonidas_renders.py
 verify_identity
 echo "EVIDENCE GROUP FINISHED $group $(date -u +%FT%TZ)"
done
echo 'Actual-model evidence created. Visual inspection is a separate acceptance step.'
