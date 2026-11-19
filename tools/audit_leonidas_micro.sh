#!/usr/bin/env bash
# Source-bound finite-part/door/shaft regression gates. Serial Blender only.
# These gates are diagnostic screens, never visual, Studio or strength approval.
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-$(command -v blender || true)}"
if [[ -z "$BLENDER_BIN" && -x /var/tmp/blender/blender ]]; then BLENDER_BIN=/var/tmp/blender/blender; fi
if [[ -z "$BLENDER_BIN" || ! -x "$BLENDER_BIN" ]]; then echo 'Set BLENDER_BIN to Blender 4.2 LTS.' >&2; exit 2; fi
BLENDER_LIB="$(dirname "$BLENDER_BIN")/lib"
export LD_LIBRARY_PATH="$BLENDER_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
# Do not inherit a diagnostic input override, partial room selection, or an
# old-source candidate exemption into a canonical saved-source audit.
unset LII_AUDIT_BUILD_DATA LII_MICRO_CANDIDATE LII_PLANT_CANDIDATE LII_EXTERIOR_CANDIDATE LII_DOOR_CANDIDATE LII_SHAFT_CANDIDATE LII_FITTINGS_FIXTURE_ONLY LII_MICRO_ROOMS
export LII_MICRO_REQUIRE_PASS=1
for quality in ${LII_AUDIT_QUALITIES:-MASTER GAME}; do
 if [[ "$quality" == MASTER ]]; then
  unset LII_GAME_DETAIL
  model=models/leonidas_ii/Aurelian_1889.blend
 elif [[ "$quality" == GAME ]]; then
  export LII_GAME_DETAIL=1
  model=exports/leonidas_ii/build/Aurelian_Game_Source.blend
 else
  echo "Unknown audit quality $quality" >&2;exit 2
 fi
 echo "MICRO SAVED-SOURCE BEGIN $quality"
 "$BLENDER_BIN" -b -t 2 --python-exit-code 1 -P blender/leonidas_ii/test_micro_contacts.py
 LII_FITTING_REPORT="docs/leonidas_ii/MICRO_GEOMETRY_${quality}.json" "$BLENDER_BIN" -b "$model" -t 2 --python-exit-code 1 -P blender/leonidas_ii/audit_fittings.py
 LII_ROOM_PART_REPORT="docs/leonidas_ii/ROOM_PART_GEOMETRY_${quality}.json" "$BLENDER_BIN" -b "$model" -t 2 --python-exit-code 1 -P blender/leonidas_ii/audit_room_parts.py
 LII_PLANT_PART_REPORT="docs/leonidas_ii/PLANT_PART_GEOMETRY_${quality}.json" "$BLENDER_BIN" -b "$model" -t 2 --python-exit-code 1 -P blender/leonidas_ii/audit_plant_parts.py
 LII_EXTERIOR_PART_REPORT="docs/leonidas_ii/EXTERIOR_PART_GEOMETRY_${quality}.json" "$BLENDER_BIN" -b "$model" -t 2 --python-exit-code 1 -P blender/leonidas_ii/audit_exterior_parts.py
 LII_DOOR_SWEEP_REPORT="docs/leonidas_ii/DOOR_SWEEP_GEOMETRY_${quality}.json" "$BLENDER_BIN" -b "$model" -t 2 --python-exit-code 1 -P blender/leonidas_ii/audit_door_sweeps.py
 LII_SHAFT_CLEARANCE_REPORT="docs/leonidas_ii/SHAFT_CLEARANCE_${quality}.json" "$BLENDER_BIN" -b "$model" -t 2 --python-exit-code 1 -P blender/leonidas_ii/audit_shaft_clearances.py
 echo "MICRO SAVED-SOURCE FINISHED $quality (screen only, not physical/visual acceptance)"
done
