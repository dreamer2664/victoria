# THEMISTOCLES-II — second-generation build notes

This document records how the second-generation boats were actually built: what
changed in the engine, what the geometry pipeline does, where the numbers come
from, and the outstanding verified/non-verified list. It is the engineering
pair to `HISTORICAL_EVIDENCE.md` (which records the period sources) and
`docs/THEM2_INSPECTION_REPORT.md` (what was wrong with the first generation).

## The rebuild in one paragraph

`boats/scripts/them2/` holds a fresh set of procedural libraries:

| module | contents |
|---|---|
| `geom2.py` | mesh builder: grids, sweeps, lathes, tubes, plates, cap-fans, rivet rows, icospheres; Sutherland–Hodgman half-plane volume clipping |
| `hull2.py` | `Hull2` parametric hull (sheer, keel-profile, half-breadth curves + per-station section super-ellipses), section sampling with true arc-length mapping, waterplane integration, draught solving |
| `structure2.py` | shell & skeleton: clinker strake stack, carvel, double-diagonal skin, keel/stem/sternpost/transom, bent frames, keelson, gunwale/inwale/rubbing strake, breast hook, risers, side benches |
| `parts2.py` | oars (from documented scantlings, loomed/leathered/blank-stop rowed), swivel rowlocks, plate rudders w/ pintles and tiller, foot gratings, stretchers, fenders, painter coils, anchors & grapnels, boat hooks, water breaker, bucket, baler, sidelights, binnacle compass, ensigns, harpoon (sheathed), centreboard + case, line tub |
| `machinery2.py` | vertical multitubular boiler (open fire door + coal heap + hold-down stays + brass cleading bands), boiler mountings (gauge glass, pressure gauge, Ramsbottom safety valve, whistle, feed check), compound inverted cylinder engine with Stephenson-link eccentrics, shaft line w/ couplings + stern tube, helical 2-blade propeller, funnel w/ guy stays and spark arrestor, lagged pipes, coal bunker w/ heap, fire irons, copper feed tank, hand force pump, engine bearers, helm station (wheel on pedestal), steering chain run, teak fore cabin with cambered roof + panelled door, canopy tracks, dagger-board (canopy) stowage |
| `boatlib2.py` | placement logic: thwarts w/ hanging knees + risers, rowlock placement rows, oar stowage in the boat, stowed lug rig (masts + yards with furled sails lashed with gaskets), boat's gear outfit per the HMS Bombay model inventory, lifting eyes |
| `specs2.py` | the single source of truth: hull definitions, weight budgets, hydrostatic reconciliation |
| `mats2.py` / `studio2.py` / `bl2.py` | procedural PBR materials (wood ring-grain, tarnished metals, canvas weave, rope twist, glass, coal, lagging), studio environment (cyclorama, three-point), Blender plumbing (mesh→object with per-face palette, GLB/FBX export, camera fitting) |

The three *build scripts* (`build2_rowing_cutter.py`, `build2_whaler.py`,
`build2_steam_cutter.py`) assemble complete boats from these libraries and save
`.blend` files.  `render2.py` renders the published sets with view-framed
cameras; `export2.py` writes per-part GLB + FBX and the manifest JSON.

## Hydrostatics — what was wrong and what now passes

First-generation boats were balanced by hand-tuned `.blend` placements.  The
second generation solves the waterline:

- The displaced-volume integral of the parametric hull (41 × 41 section clip
  by Sutherland–Hodgman) was verified coarse-vs-fine at several draughts.
- `specs2.reconcile` translates the design vertically so that the solved
  LOADED waterline sits at Z = 0, then writes the solved light draught into
  the metadata.  All published draughts, freeboards and lcb figures come out of
  this solver, so the interface document cannot disagree with the model.
- **Section fullness found insufficient.**  The first generation's hull form
  (midship section coefficient drawn at 0.32 on a very flat floor) displaces
  1.93 m³ only at 0.744 m of draught: the 10-oared cutter with ten rowers
  cannot float at the documented 0.397 m.  Fuller (rounder) mid sections are
  documented for Service cutters; the second generation uses them, and the
  published draught is the solved ~0.66 m loaded.  Both numbers are preserved
  in `docs/THEM2_INSPECTION_REPORT.md` §8, including the discrepancy analysis.

## Render sets

`renders/them2/` holds the published sets: per boat, nine exterior angles
(broadside, bow quarter, stern quarter, bow-on, stern-on, overhead, underside,
hero, high profile), interior top/down-angle, skeletal construction study
(planking hidden), on-water in-situ hero, and for the steamer a machinery-room
study.  All views computed from the model bounds — no hand-placed cameras.

## Roblox delivery

- Moving parts are individual objects with origins at the animation pivot:
  every oar (rowlock), the rudder (pintle line), the screw (shaft hub).
- `roblox/tools/gen_manifest2.py` regenerates `roblox/src/Manifest_*.lua` from
  the export metadata (`moving_pivots`, per-part envelopes, hydro block) so the
  Lua never hard-codes a number the geometry can contradict.
- `Config.lua` values updated to the solved hydro; rowing/steering/steam
  controllers from the QA'd first-generation control stack are reused unchanged
  in behaviour terms (they bind parts by name `Oar_*/Rudder/Propeller`, which
  this generation preserves).
- Per-part triangle limit 19 000 observed on every export (largest part: hull
  planking, mesh-decimated to the limit; everything else well under it).

## Status of claims

- Renders produced from the committed build scripts end-to-end. ✓
- Hydrostatics produced by the same code that models the hull. ✓
- Exports produced from the committed exporter against the published blends. ✓
- **Studio play-test status: NOT VERIFIED.**  The Roblox Lua was developed and
  symptom-tested against the manifests and boat shapes (unit-style checks in
  pure Lua in `docs/TESTING.md`), but the boats have not been sailed in an
  actual Roblox Studio session on this branch, so this readme makes no
  "play-tested" claim.
