# Roblox — the two ship's boats of OPERATION VICTORIA

Driveable, scripted versions of both boats, built from the Blender exports at
the project scale of **1 stud = 0.28 m**.

| File | Where it goes | What it does |
|---|---|---|
| `src/BuildBoat.lua` | ModuleScript (run from the command bar) | assembles imported meshes into a driveable model: scales, rotates, sets mass, welds, makes the moving parts pivot |
| `src/BoatService.lua` | ServerScriptService | starts the right controller for each boat, routes control messages, builds seats and the docking point |
| `src/BoatClient.lua` | StarterPlayerScripts | keyboard input, HUD |
| `src/SteamCutter.lua` | ModuleScript | steam cutter: engine start/stop, throttle, reverse, screw, rudder, smoke |
| `src/RowingCutter.lua` | ModuleScript | rowing cutter: stroke cycle, ten animated oars, steering by bank |
| `src/Hydrodynamics.lua` | ModuleScript | buoyancy probes, thrust, anisotropic hull drag, yaw |
| `src/WaterSurface.lua` | ModuleScript | finds the water surface (Terrain water, a `WaterPlane` part, or a fallback level) and the wave field |
| `src/BoatRig.lua` | ModuleScript | Motor6D rigging so oars/rudder/screw turn about their real pivots |
| `src/Effects.lua` | ModuleScript | funnel smoke, steam jets, bow spray, prop wash |
| `src/Config.lua` | ModuleScript | all tunables, both boats |
| `src/Manifest_*.lua` | ModuleScript | generated from `boats/exports/*/manifest.json` — part names, roles, pivots and sizes in studs |

All twelve files compile clean under the Luau compiler and lint clean under
`luau-analyze --mode=nonstrict`.

## Install

1. **Import the meshes.** From `boats/exports/steam/` import the per-part GLB
   files (each part keeps its own pivot — this matters for the oars, rudder and
   screw) into a Folder. Repeat for `rowing/`.
   *Import them at scale 1 and let `BuildBoat` do the conversion.*
2. **Assemble.** With `BuildBoat` as a ModuleScript in `ReplicatedStorage`:

   ```lua
   local BuildBoat = require(game.ReplicatedStorage.BuildBoat)
   BuildBoat.assemble("steam_cutter_1888", game.Workspace.SteamImport,
       { position = Vector3.new(-14, 4, 0) })
   BuildBoat.assemble("rowing_cutter_25ft", game.Workspace.RowingImport,
       { position = Vector3.new(14, 4, 0) })
   ```

   This scales by 3.5714, rotates the bow to −Z, picks the hull as the
   PrimaryPart, sets its mass to the published loaded displacement, welds the
   detail to it and tags the model with `BoatId`.
3. **Add water.** Terrain water works as-is. If you use a flat water part,
   name it `WaterPlane`.
4. **Add the scripts.** `BoatService` → ServerScriptService; `BoatClient` →
   StarterPlayerScripts; everything else → a ModuleScript folder the service
   can `require`.

## Controls

Sit in the boat's helm seat, then:

| Key | Steam cutter | Rowing cutter |
|---|---|---|
| **W** | open the regulator (ahead) | pull — starts the stroke |
| **S** | reverse (Stephenson link) | — |
| **A / D** | helm to port / starboard | pull harder on that bank |
| **Shift** | full ahead | harder stroke |
| **E** | start / stop the engine | — |
| **R** | sound the whistle | — |

## How the behaviour works

**Steam cutter.** Starting is not instantaneous. `E` lights the fire and
raises steam over about six seconds (`engine_start_s`); only then does the
screw turn. Throttle is the regulator opening, and the screw's rpm follows it
with inertia. The hull answers the helm in proportion to the water flowing
past the rudder, so at rest the tiller does nothing — as in a real boat.
Coal smoke scales with throttle and steam pressure.

**Rowing cutter.** One full stroke is a real cycle: catch (blades turned
square, oars swung forward), drive (blades buried, boat accelerates), finish
(blades released), recover (blades feathered flat and swung forward). Thrust
is applied only during the drive, so the boat surges and carries her way
between strokes. There is no rudder in the control loop: steering comes from
pulling harder on one bank, which is how a coxswain actually steers a cutter.

**Both boats** float on buoyancy probes rather than being pinned to a height,
so they sit at their designed draught (0.53 m steam, 0.40 m rowing), heel to a
load and pitch into a seaway. Lateral resistance is anisotropic — a hull
resists sideways motion far more than forward motion — which is what stops
them sliding sideways through turns.

## Timing constants worth tuning first

In `Config.lua`:

| Constant | Default | What to change it for |
|---|---|---|
| `steam_cutter_1888.max_thrust_n` | 2600 | top speed; target 6–7 knots |
| `steam_cutter_1888.prop_max_rpm` | 420 | screw spin rate, purely visual |
| `steam_cutter_1888.engine_start_s` | 6.0 | how long steam takes to raise |
| `rowing_cutter_25ft.max_speed_studs` | 11 | top speed; target 5–6 knots |
| `rowing_cutter_25ft.stroke_rate` | 26 | strokes per minute at full effort |

The thrust figures are in Roblox force units and are first estimates; expect
to adjust them once against the hull masses `BuildBoat` sets.

## Integration with the ship

`interfaces/boats_spec.json` is the contract with the main ship agent:
davit sling positions, cradle contact points, stowage envelope, boarding
points, weight, origin and orientation. Both boats are published there and the
figures are generated from the same source as the models
(`boats/scripts/boatgen/specs.py`).

`BoatService` creates a `DockPoint` part at each boat's bow and the seats at
the published boarding position; if the ship's boat-handling arrangement needs
different attachment points, change them in `Config.BOATS[id].davit_points`
and re-run `publish_spec.py` so both sides agree.

## Status

The scripts compile and lint clean, but **they have not been run in Roblox
Studio** — Studio is not available in the environment these boats were built
in. `boats/docs/TESTING.md` §2 lists the ten acceptance tests per boat that
close that gap, with the expected result for each. The three known risks
(Motor6D pivot offsets on import, hull PrimaryPart selection, thrust tuning)
are listed there too.
