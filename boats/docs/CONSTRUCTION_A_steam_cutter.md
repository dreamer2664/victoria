# BOAT A — 25 ft Steam Cutter

**What it is.** A 25 ft (7.620 m) ship's steam cutter of the "proposed" 1888
Admiralty type — the design recorded on the Dangerfield lithograph *Proposed
25 ft steam cutter* (National Maritime Museum, RMG NPC9572, 18 January 1888),
developed into a complete, operable vessel: hull, structure, boiler, engine,
shafting, propeller, rudder, funnel, pipework, fuel, seating and boat's gear.

Everything in this document describes **this model**. Where a detail is
reconstructed rather than documented it says so; the full evidence trail is in
`../HISTORICAL_EVIDENCE.md`.

---

## 1. Principal dimensions

| | metric | imperial |
|---|---|---|
| Length overall | 7.620 m | 25 ft 0 in |
| Beam, extreme | 2.134 m | 7 ft 0 in |
| Depth moulded amidships | 1.203 m | 3 ft 11⅜ in |
| Sheer height at stem head | 0.908 m | 2 ft 11¾ in |
| Sheer height at transom | 0.773 m | 2 ft 6⅜ in |
| Draught, light | 0.500 m | 1 ft 7⅝ in |
| Draught, loaded | 0.527 m | 1 ft 8¾ in |
| Freeboard, loaded | 0.671 m | 2 ft 2⅜ in |
| Displacement, light | 3212 kg | 3.16 tons |
| Displacement, loaded | 3532 kg | 3.48 tons |
| Hull depth (keel to sheer) amidships | 1.203 m | — |

Draught and displacement are solved, not guessed: `boatgen.hydro` integrates
the actual modelled hull form (Simpson's rule over 41 stations) against the
itemised weight schedule in `boatgen/specs.py`. The light and loaded waterlines
in the renders are the ones this calculation produces.

## 2. Hull and structure

* **Form.** Hollow, fine forward; a fairly full run aft; a raked stem and a
  raked transom stern. The sheer sweeps up 0.14 m from amidships to the stem
  head and 0.11 m to the transom, which is what stops a boat this short from
  looking like a box.
* **Planking — carvel outside.** Thirteen strakes of 20 mm planking, landed
  edge to edge (`build_carvel_planking`, `n_strakes=13`, `thickness=0.020`).
  The two lowest strakes are red-leaded below the waterline, the working
  topsides are black, and the two upper strakes are painted white — the
  white sheer strake that reads so clearly on every period photograph of
  these boats and on the restored examples.
* **Inner skin — double diagonal.** Two layers of 11 mm diagonal planking at
  0.024 m and 0.038 m inside the frame line, running in opposite directions,
  which is the double-diagonal construction recorded for the 1838 cutter
  (RMG SLR0772) and used in Admiralty boats of this size to get stiffness
  without great weight.
* **Frames.** Some 48 grown oak timbers at 152 mm centres, 28 mm sided ×
  40 mm deep, standing from the keel to the sheer (`build_frames`). They are
  visible inside the boat in the cutaway renders, exactly as they would be
  before the ceiling is fitted.
* **Keel, stem, sternpost.** A single straight-grained keel with a raked stem
  and a sternpost carrying the stern tube; all drawn as `build_keel`,
  `build_stem`, `build_sternpost`.
* **Keelson, gunwale, transom.** An internal keelson through the floors; a
  gunwale capping the frame heads from stem to transom; a raked transom
  built from separate transom planks.
* **Bearers and floors.** Two wrought-iron longitudinal engine bearers on
  cast floors, 0.42 m off the centreline, carrying the boiler and the engine
  bed — the machinery is not "sitting on the planking", it is bolted to a
  structure.

## 3. Deck, coaming and canopy

* A 0.115 m drop from the sheer to the deck edge, so the deck is a shallow
  tray and water runs to the sides rather than into the machinery space.
* A foredeck forward of the machinery space and a small after deck aft,
  with the machinery standing in an open well between them.
* A coaming 0.11 m high around the well, capped and painted.
* A **canvas canopy** carried on six brass hoops and four longitudinal
  strings. The canvas is modelled as cloth, not as a board: it **sags 26 mm
  between hoops**, carries a slight ripple across its width, is **seamed**
  with five raised strips down its length, and is **laced** to the coaming
  with rope ties through brass grommets at every other hoop, finishing in a
  **scalloped valance** and closed end curtains. The funnel passes through it
  — see §5. The canopy is deliberately *low* (0.30 m rise): a steam cutter's
  canopy is a weather hood, not a deckhouse, and a tall box would both look
  wrong and block the view from the helm.

## 4. Boiler

A vertical fire-tube boiler, riveted, coal-fired:

| | |
|---|---|
| Shell outside diameter | 0.720 m (2 ft 4⅜ in) |
| Height, base to crown | 0.860 m (2 ft 9⅞ in) |
| Working pressure | 100–120 psi |
| Heating surface | vertical fire tubes + firebox |
| Mounting | on the iron bearers, base at floor level |
| Fittings | stop valve, safety valve with lever and weight, pressure gauge, gauge glass with two cocks, three try cocks, feed check valve, blow-down cock |

The boiler is modelled as a *shell plus internals*, not a decorated cylinder:
behind the firebox doors there is a grate, above it a firebox, then the tube
plate and a nest of fire tubes leading to the smokebox and the funnel spigot
(`machinery.boiler_cutaway`). The cutaway render shows them.

Every visible fitting has a job: the gauge glass shows the water level, the
try cocks prove it, the safety valve lifts at pressure, the stop valve is what
the engineer opens to let steam to the engine. This is the "no modern engine
under a Victorian shell" requirement — the plant is a real, if small,
Victorian steam plant.

## 5. Engine and machinery

| | |
|---|---|
| Type | inverted vertical single-cylinder, direct-acting |
| Bore × stroke | 5½ in × 6 in (0.140 m × 0.152 m) |
| Rated | ~5 ihp at 350 rpm on 100–120 psi |
| Frame | four turned columns on a cast bedplate |
| Valve gear | slide valve in a chest, driven by an eccentric with a Stephenson reversing link |
| Transmission | forged crankshaft, crank webs, connecting rod, crosshead running in guide bars, piston rod and piston |
| Propeller | two-bladed, 0.34 m (13½ in) diameter, on a 0.048 m shaft through a stern tube |
| Rudder | plate rudder aft of the screw, with a stock through the counter and a tiller |

The engine is placed so the crank sits at z = −0.025 m relative to the load
waterline — low in the boat, where the weight belongs. The shaft runs aft at
about 9° from the crank to the stern tube and out to the screw at
(−3.42, 0, −0.45). The screw hangs below the counter with its disc top 0.04 m
clear of the local keel line, so it turns in clean water without cutting into
the planking — verified as a triangle-level interference test, not assumed.

**Why a single-cylinder engine?** The 1888 plan archive pairs this hull with
simple direct-acting plants; compound engines belong to the 32 ft cutters of
1891 (RMG NPC9568) and later. A single 5½ × 6 in cylinder is the right size
for a 25 ft hull, keeps the machinery compact enough to fit under a low
canopy, and is honestly buildable from the drawing set.

**Steam cycle, as modelled:** coal → firebox → fire tubes → smokebox → funnel;
water → feed tank → feed pump → check valve → boiler; steam → stop valve →
main steam pipe → valve chest → cylinder → exhaust. The pipes are modelled as
runs at real elevations: main steam on the port side at chest height, exhaust
to the funnel base, feed (copper) low down along the starboard side, blow-down
through the shell.

The main steam and exhaust runs are **lagged** — wrapped in canvas with brass
retaining bands at intervals, which is how a Victorian steam pipe is actually
finished, both to keep the heat in and so that a hand laid on it is not
burnt. It also stops the pipework reading as bare scaffolding inside the
boat.

## 6. Fuel and consumables

* Coal bunker abaft the boiler at x = +1.62 m, 0.48 m wide, holding about
  0.18 m³ (≈ 140 kg) of coal — roughly four hours at this plant's firing rate.
* Feed/water tank low down at x ≈ −1.95 m, below the after end of the
  machinery space, feeding the pump.
* Bucket, shovel and ash rake stowed against the bunker.

## 7. Seating and accommodation

* Helmsman's bench aft of the engine, with the tiller within reach.
* Two passenger benches in the after part of the well.
* Foredeck seating forward of the boiler.
* Side decks 0.16 m wide outboard of the coaming, so the crew can walk
  forward without stepping into the machinery well.

## 8. Boat's gear

Mooring and lifting fittings: two keelson eyes for the davit slings (at
x = +2.05 and −1.55, spread 3.6 m — see `interfaces/boats_spec.json`), a stem
ring, a stern eye. Navigation: a compass in a box on the foredeck, port and
starboard sidelights on brackets, a lifebuoy on the canopy, a boat hook, a
bucket, fenders. There is no mast, because a 25 ft steam cutter under way
does not set sail; the historical examples with masts are rowing boats.

## 9. What a Victorian engineer would notice

* The boiler is where the weight is needed and the fire is reachable from the
  helm seat.
* The engine is aft of the boiler, so the steam pipe is short and the
  exhaust run to the funnel is shorter still.
* The screw is behind the rudder post position but ahead of the rudder blade,
  so the rudder gets clean water and the boat steers at low revolutions.
* The bunker is abaft everything so that trimming the boat is a matter of
  moving coal forward.
* The canopy keeps the rain off the machinery without hiding it from a
  passenger or blocking the helmsman's view.

## 10. Rebuild

```
cd boats/scripts
LD_LIBRARY_PATH=/var/tmp/blender/lib blender -b --python build_steam_cutter.py -- --quick
```

`--quick` renders at reduced resolution; without it the full render set is
produced. The build is deterministic — every dimension comes from
`boatgen/specs.py` and `boatgen/hull.py`.
