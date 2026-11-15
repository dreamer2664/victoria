# Operation Victoria — Agent 03: The Ocean Liner

**SS *Aurelian* (1889)** — an original, historically credible British express liner of the
late 1880s, modelled at real-world metres in Blender, exported in modules for Roblox, and
documented with drawings, renders and a reference board.

![Exterior](renders/exterior/three_quarter_bow.png)

---

## What this is

* **Not** a reconstruction of *Teutonic*, *Majestic*, *City of Paris* or *Umbria*, and no
  dimension is copied from any of them. Every plate of geometry is original.
* **Is** a vessel designed on the principles those ships shared: a steel riveted hull of
  Cb ≈ 0.69 and 19-knot speed, a vertical inverted triple-expansion engine on nine
  single-ended boilers, two funnels and three pole masts, a superstructure deck carried on
  brackets with the promenade round it, and panelled first-class public rooms with
  hurricane lamps.

| | |
|---|---|
| Line | Albion & Western Steam Navigation Co., Liverpool |
| Builder | Birkenhead Iron Works & Shipbuilding Co., yard no. 147 |
| Laid down / launched / completed | Nov 1887 / 14 Mar 1889 / 20 Jun 1889 |
| Service | Liverpool – Queenstown – New York, fortnightly |
| LOA / LBP / beam / draft | 166.0 / 158.0 / 18.4 / 6.50 m |
| Displacement / gross / lightship | 13,600 t / 8,480 GRT / 9,950 t |
| Passengers / crew | 228 first, 132 second, 720 third = 1,080 / 196 |
| Machinery | 1 set vertical inverted triple-expansion, 0.965/1.575/2.565 × 1.295 m, 14,000 IHP at 62 rpm |
| Boilers | 9 cylindrical single-ended return-tube, 4.20 m × 3.35 m, 11 bar |
| Speed | 19.3 kn service, 20.2 kn maximum |
| Propeller | single screw, 5.30 m dia × 6.90 m pitch, 4 blades |
| Scale | 1 stud = 0.28 m → **592.9 studs** long, **65.7 studs** abeam |

Full numbers: [`interfaces/ship_spec.json`](interfaces/ship_spec.json),
[`DIMENSION_MANIFEST.json`](DIMENSION_MANIFEST.json).

---

## Repository layout

```
shipdesign/            the design itself — pure Python, no Blender, no numpy geometry
  spec.py              principal dimensions, machinery, funnels, masts, boats, palette
  hull.py              hull form: sections, shell loft, hydrostatics  (bpy-free)
  layout.py            deck schedule, 42 rooms, 32 doors, 9 stairs, 14 bulkheads
  drawings.py          lines plan, body plan, general arrangement, 7 deck plans
  validate.py          13 drawing-office consistency checks (exit 1 on failure)
  publish_spec.py      writes interfaces/ship_spec.json + DIMENSION_MANIFEST.json
blender/
  lib_build.py         shared modelling helpers
  build_hull.py        shell, strakes, rivets, keel/stem/sternpost, rudder, anchors
  build_superstructure.py  deckhouses, promenade, boat deck, bridge, funnels, masts,
                           rigging, boats + davits, deck machinery, nav lights
  build_interiors.py   all 42 rooms, furniture, stair, dome, panelling, carpets
  build_machinery.py   boilers, triple-expansion engine, propeller, shafting, steering
  assemble.py          links modules into models/ship_assembly.blend
  render.py            exterior renders          render_interiors.py  interior renders
  render_machinery.py  engine-room cutaway
  export_roblox.py     7 logical FBX + GLB modules at 1 stud = 0.28 m
  diag_cam.py          ray-cast camera diagnostic
models/                module_hull / _superstructure / _interiors / _machinery / assembly
exports/               fbx/, glb/, roblox_modules.json
roblox/                5 runtime scripts (see below)
drawings/              9 sheets, PNG + SVG
renders/               exterior/, interiors/, machinery/
reference/             reference_board.png/.pdf, plates/, reference_index.json
interfaces/            boats_spec.json (in), ship_spec.json (out)
HISTORICAL_EVIDENCE.md every decision traced to a source or marked as inference
```

---

## Building it

Requires Python 3.11+, numpy, matplotlib, and Blender 4.2 (a portable copy is used here via
`tools_blender/run.sh`).

```bash
# 1. design + drawings + specs (no Blender needed)
python3 -W ignore -m shipdesign.drawings
python3 -W ignore -m shipdesign.publish_spec
python3 -m shipdesign.validate                     # must report 0 failures

# 2. geometry
BLENDER=/path/to/blender
$BLENDER -b -P blender/build_hull.py
$BLENDER -b -P blender/build_superstructure.py
$BLENDER -b -P blender/build_interiors.py
$BLENDER -b -P blender/build_machinery.py
$BLENDER -b -P blender/assemble.py -- \
        hull,superstructure,interiors,machinery models/ship_assembly.blend

# 3. renders
$BLENDER -b models/ship_assembly.blend -P blender/render.py -- renders/exterior
$BLENDER -b models/ship_assembly.blend -P blender/render_interiors.py -- renders/interiors
$BLENDER -b models/ship_assembly.blend -P blender/render_machinery.py -- renders/machinery

# 4. Roblox export
$BLENDER -b models/ship_assembly.blend -P blender/export_roblox.py -- exports
```

Every module builds into its **own** `.blend`, so the hull, superstructure, interiors and
machinery stay separately editable. `assemble.py` links them into one scene without
flattening them.

---

## Roblox integration

`exports/roblox_modules.json` lists seven **logical modules** — Hull, Superstructure,
DeckEquipment, Interiors_Public, Interiors_Cabins, Interiors_Structure, Machinery — each
with its own FBX and GLB, a shared origin and the scale factor applied. Import them into
the same Studio model named `Aurelian`; do **not** merge them into one mesh.

| Script | Place in | Does |
|---|---|---|
| `AurelianShipController.server.lua` | inside the `Aurelian` model | Master state: telegraph order → shaft RPM → propeller law → speed; rudder → turn rate; pitch/roll/heave; publishes attributes |
| `Aurelian_Telegraph.server.lua` | inside the wheelhouse | Working 10-position EOT with needles, helm wheel, whistle |
| `Aurelian_EngineAnim.server.lua` | inside Machinery | Slider-crank piston motion, crankshaft, propeller and shaft rotation, furnace flicker, engine hum |
| `Aurelian_DoorsAndLighting.server.lua` | ServerScriptService | Proximity doors, watertight doors, boarding plates that release the moorings interlock, interior lamp setup and night watch |
| `Aurelian_SmokeAndWake.client.lua` | StarterPlayerScripts | Coal smoke intensity from RPM, steam puffs, wake and bow wave, distance culling |

All control flows through **attributes on the ship model**, so any script can read the
state (`SpeedKn`, `ShaftRPM`, `Telegraph`, `Heading`, `RudderAngle`, `MooringsClear`,
`LightsOut`) without wiring up RemoteEvents.

Interaction is by `ProximityPrompt` throughout, so it works on touch and console as well as
on a keyboard.

---

## The scale rule

`1 stud = 0.28 m`. The exporter applies `global_scale = 1/0.28` and exports FBX with
`axis_forward=-Z, axis_up=Y`, and GLB with `export_yup=True`. An object 1 m long in Blender
arrives at 3.5714 studs. The ship is 592.9 studs overall.

---

## Quality gate

`shipdesign/validate.py` runs 13 checks every build and **fails the build** on any of
them. Current state on the assembled scene:

```
13 passed, 2 warnings, 0 failures
```

It caught three real design errors during this project, which is why it exists:

1. A funnel running straight through the library (found by ray-casting a camera).
2. Walls that stopped 2.75 m above the floor while the real ceiling — the deck above —
   was at 3.30 m, leaving a black band round the top of every small room.
3. Room polygons containing numpy arrays instead of floats, which had silently produced a
   6.57 m room as 0.57 m wide.

See [`HISTORICAL_EVIDENCE.md`](HISTORICAL_EVIDENCE.md) §8 for an honest list of what this
model does **not** have.

---

## Interfaces

* **In** — `interfaces/boats_spec.json` (contract published for Agent 02: two 25-ft
  cutters, their dimensions and the davit positions reserved for them).
* **Out** — `interfaces/ship_spec.json` (everything another agent needs to place this
  vessel in a scene: dimensions, decks, hydrostatics, layout, scale, Roblox attributes).

---

## Branch

`agent/ship`. Other agents' work is untouched; nothing outside this agent's scope has been
modified.
