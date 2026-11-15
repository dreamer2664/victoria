# OPERATION VICTORIA — Agent 01: Port Construction

Two late-Victorian British maritime ports, modelled in Blender, documented against
period sources, and exported for Roblox.

| | **Port A — Aldermouth** | **Port B — Carrickmore** |
|---|---|---|
| Purpose | Passenger harbour | Industrial / shipbuilding harbour |
| Prototype | Liverpool: enclosed non-tidal dock system | Belfast: shipyard, graving docks, slips |
| Distinctive works | floating landing stage, terminal, customs, baggage hall, station, transit sheds, coal staithes, cattle pens | Princess Graving Dock (800 × 80 ft, three caissons), No. 1 dock, three building slips, moulding loft, engineering/boiler shops, Titan crane, yard rail |
| Berths | 4 (B1 212 m @ 11 m, B2 110 m @ 6.5 m, B3 132 m @ 9 m, B4 124 m @ 9 m) | 3 (fitting-out 210 m @ 10 m, service 320 m @ 9 m, No. 1 dock 120 m @ 8 m) |
| Geometry | 46 prototypes, 396 instances, 786 k instanced tris | 41 prototypes, 291 instances, 377 k instanced tris |
| Overlaps | 0 | 0 |

Everything is built to one scale: **1 Roblox stud = 0.28 m**. The Blender source is
modelled natively in metres; the conversion happens once, in `roblox/src/Config.luau`.

---

## 1. What is in here

```
blender/
  build_ports.py          driver: layout -> save -> render -> export  (CLI below)
  make_plans.py           draws docs/port_*.svg from the same layout data
  port_a.blend            the built Port A scene
  port_b.blend            the built Port B scene
  lib/
    core.py               MeshBuilder primitives, constants, 51 materials
    parts.py              windows, doors, quoins, cornices, columns, stairs, railings
    bldg.py               warehouses, transit sheds, terminals, stations, offices, shops
    maritime.py           quay walls, graving docks, caissons, slipways, landing stage, bollards
    machinery.py          cranes, winches, staithes, coal hoists, rail, wagons, cargo, plate stacks
    texgen.py             generates all 16 texture sets into textures/
    signs.py              bakes 23 painted signboards into textures/signs/
    portsite.py           land/water decomposition + LayoutAuditor
    proxy.py              berth clearance block-out -- NOT a ship asset
  ports/
    port_a.py             Port A composition + metadata
    port_b.py             Port B composition + metadata

assets/glb/<port>/        one GLB per prototype + port_<x>_full.glb
assets/fbx/<port>/        port_<x>_full.fbx
assets/modular/           reserved for the modular kit breakdown
docs/
  port_a_plan.svg         measured layout plan (north up, 100 m scale bar)
  port_b_plan.svg
  port_a_layout.md        dimension spec, berths, levels, interaction points, limitations
  port_b_layout.md
  port_a_meta.json        machine-readable metadata consumed by the Roblox layer
  port_b_meta.json
  QC_REPORT.md            what was inspected, from where, and what was found
  ROBLOX_SETUP.md         import + assembly instructions
renders/port_a/           01_aerial .. 08_terminal_court
renders/port_b/           01_aerial .. 07_roofscape
reference/
  reference_board.html    annotated period plates (self-contained, images embedded)
  plates/                 18 public-domain plates
roblox/src/               Luau: Config, layouts, PortService, ShipService, Mooring, server, client
tools/gen_layout_docs.py  regenerates the two layout specs from the meta JSON
HISTORICAL_EVIDENCE.md    every decision -> its source
ASSET_LICENSES.md         everything about provenance
```

---

## 2. Rebuilding from scratch

Blender 4.2 LTS, Cycles CPU (EEVEE does not work headless on this box).

```bash
# textures first, if texgen.py changed at all
python3 blender/lib/texgen.py textures

# build, save, render and export one port
blender -b --factory-startup -noaudio --python blender/build_ports.py -- --port a --stage all

# stages: layout | save | render | export | all
# options: --cams 01_aerial,03_street   --samples 40   --res 1280x720
```

A layout-only run takes about 4 s and prints the audit:

```
prototypes: 46   instances placed: 381   instanced tris: 770154
overlaps: 0
scene bbox (m): (-460, -560, -8) (300, 560, 36.9)
BERTH A-B1   26.0 x 212.0 m  depth 11.0 m  env 180x 20x  9 m  OK (>=4 m clearance)
```

Then, if the layout changed at all:

```bash
blender -b --factory-startup -noaudio --python blender/make_plans.py  # layout plans
python3 tools/gen_layout_docs.py                                     # written specs
python3 reference/make_reference_board.py                            # reference board
```

---

## 3. Importing into Roblox

Full instructions, including the stud conversion, collision setup and the assembly
step, are in **[`docs/ROBLOX_SETUP.md`](docs/ROBLOX_SETUP.md)**. The short version:

1. **Scale.** Do not rescale on import. Every exported GLB/FBX is in metres; scale the
   imported model by **3.5714** to get studs (1 / 0.28). Alternatively set
   `MeshPart.Size` from the metadata, which is authoritative.
2. **Whole port or kit.** `port_<x>_full.glb` is one object — use it to look at the
   port, not to ship it. For a playable place import the per-prototype GLBs and
   assemble them with the transforms in `docs/port_<x>_meta.json`; the module
   `roblox/src/PortLayoutA.luau` documents the pattern.
3. **Collision.** The exported meshes are render geometry. Build collision from the
   plan: a `Part` per building footprint (the rectangles in the layout docs), one for
   the quay surface, one invisible wall along each quay edge. Do not enable
   `CollisionFidelity.Precise` on the sheds — it is expensive and unnecessary.
4. **Interaction points.** `PortService.luau` builds every prompt from the generated
   layout modules. Positions are metres; `Config.toWorld()` converts.

---

## 4. Modular construction and connection points

Assets are built as prototypes in `_PROTOTYPES` and placed as linked duplicates, so a
change to a prototype updates every instance. The connection conventions:

| Asset class | Connection point | Convention |
|---|---|---|
| Quay modules (`A_quay24`, `B_quay24`) | 24 m module length, origin on the coping line | place at 24 m centres along an edge; `rz` picks which way the land faces |
| Buildings | origin at the SW footprint corner, footprint given in the layout docs | door faces the street side named in the metadata |
| Cranes | base plate centre at `QUAY_Z` | `rz` = working direction, +X = the crane's reach |
| Bollards | base at `QUAY_Z`, centre of the base plate | 16–20 m centres along a berth |
| Gangways | shore end fixed, ship end free | the interaction trigger sits at the shore end |
| Slipways | origin at the low (water) end | `rz = -90` turns the ways onto an east–west frontage |
| Graving docks | origin at the SW corner of the dock rectangle | `depth` is measured down from the coping |

Signage is baked into textures and applied to signboard parts, so it instances with the
building and costs no extra geometry.

---

## 5. Gameplay systems

`roblox/src/` is a working integration layer, not pseudocode:

- **`ShipService`** — a per-berth state machine
  `Idle → Approaching → Berthing → Moored → Working → CastingOff → Departed`, with
  illegal transitions rejected. Turnaround is timed from the research: ~29 h for a
  passenger berth, ~4.5 days for a coaling cargo berth.
- **`Mooring`** — headline / sternline / spring, `RopeConstraint` between a ship cleat
  and a real bollard, with the simulation refusing "Moored" until the required number
  of lines is fast.
- **`PortService`** — builds ProximityPrompt anchors from the generated layout, tagged
  for lookup and carrying the berth they serve.
- **Boarding gate** — you cannot board unless you have a ticket, have cleared customs,
  the ship is `Working`, and a gangway is shipped. Four independent conditions, all
  modelled steps in the port.
- **`PortClient`** — HUD showing berth states and notices.

---

## 6. Status and known gaps

Honest state of the work, as of this commit:

- Both ports build, audit clean (0 layout overlaps), save, render and export.
- **Port A berth B3 is 132 m against a 130 m envelope** and does not meet the 4 m end
  clearance rule. Recorded, not hidden — see `docs/port_a_layout.md` §7.
- Port A's south-east corner is open quay / reserved land rather than built up.
- No ship is modelled anywhere. `proxy.py` is a clearance block-out and is exported
  under the reserved name `_PROXY_liner`; **delete it before shipping**.
- The landing stage is static: these docks are non-tidal, so there is no tide to
  animate.
- See `docs/QC_REPORT.md` for the full inspection record, including what failed.

---

## 7. Sources

`HISTORICAL_EVIDENCE.md` carries the full register: 18 annotated period plates, the
Belfast dock history, the Liverpool dock-system archaeology, and a dated exclusion list
(no Thompson Dock, no Arrol gantry, nothing after 1889). `ASSET_LICENSES.md` records
that no third-party model or texture is redistributed — every mesh and texture in both
ports is generated by the code in this repository.
