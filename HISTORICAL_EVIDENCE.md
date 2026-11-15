# HISTORICAL EVIDENCE — SS *Aurelian* (1889)

**A note on what this ship is.** *Aurelian* is an **original, fictional** vessel. She is not
a reconstruction of *Teutonic*, *Majestic*, *City of Paris* or *Umbria*, and no dimension
has been copied from any of them. What has been copied is **period practice**: the
proportions, structural arrangement, machinery and interior conventions that British
express liners of 1884–1890 shared, taken from contemporary photographs, published
plans, the technical press and a builder's textbook.

Every dimension in `DIMENSION_MANIFEST.json` is tagged either **computed** (derived from
the hull form) or **design choice** (an engineering decision inside the historical band,
justified below). Where a number is a judgement call rather than a documented practice,
this document says so.

---

## 1. Sources actually examined

Primary material is listed in `reference/reference_index.json` and reproduced, annotated,
on **`reference/reference_board.png`**. In summary:

| Source | What it is | What it decided |
|---|---|---|
| *Ocean Steamships* (New York, 1891), construction chapter pp. 97–106 + 105 plates (Project Gutenberg #54136) | A builder's textbook of exactly this period | The **build sequence**: keel, floors and frames, shell strakes, stringers, bulkheads, deck beams, decks, machinery |
| *Ocean: Magazine of Travel*, September 1889 — *Teutonic* article, 5 photographs | Contemporary published photographs and deck description | Promenade deck as a **superstructure deck on brackets**; interior arrangement; stair/saloon/smoking-room detail |
| Wikimedia Commons PD photographs — *Teutonic*, *Germanic*, *Majestic*, *City of Paris*, *Paris* in dry dock | Broadside, dock and interior photographs | Sheer and freeboard, funnel/mast arrangement, hull form under water, interior panelling |
| MaritimeQuest, *RMS Umbria* (1884) builder's data | Tabulated dimensions and machinery of a near sister | Cross-check on **displacement (13,300 t)** and IHP for a ship of this size |
| Harland & Wolff plan archive (National Museums NI) | ~500,000 drawings, late 1880s onwards | **Cited as an archival holding only** — access is by written application and could not be obtained in this project. No H&W drawing was used. |

**Honest limitation.** I could not obtain a genuine 1880s *lines plan* of any of these
ships during this project: the USM Maine archive returned 403, the Royal Museums
Greenwich image service was unavailable, and Commons carries no 1880s lines plan of these
vessels. The hull form here is therefore **generated from period design coefficients and
section shapes**, not traced from a plan. See §3.

---

## 2. The shipping line

*Albion & Western Steam Navigation Co., Liverpool* is invented. The naming, the
Liverpool–Queenstown–New York fortnightly service, the "SS" prefix and the yard at
Birkenhead are all consistent with Liverpool companies of the period (Cunard, Guion,
National Line). The builder, *Birkenhead Iron Works & Shipbuilding Co.*, is likewise a
period-plausible name for a Merseyside yard.

---

## 3. Hull form

**What the period did.** British express liners of the late 1880s were moderate
block-coefficient hulls driven hard: *Umbria* (1884) ran at about Cb 0.69 and 19 knots on
14,500 IHP; *Teutonic* (1889) was finer and faster. A design for 19.3 knots on 14,000 IHP
therefore needs:

| Coefficient | This ship | Period band | Basis |
|---|---|---|---|
| Block, Cb | **0.694** | 0.66 – 0.73 | computed from the modelled form |
| Midship, Cm | **0.918** | 0.90 – 0.94 | U-shaped sections with a double bottom |
| Prismatic, Cp | **0.755** | 0.72 – 0.78 | computed |
| Waterplane, Cw | **0.750** | 0.72 – 0.78 | computed |

Sheer: 11.80 m amidships, **13.05 m forward**, 12.35 m aft. The forward rise is the
period's characteristic "sheer to the bridge" — visible in every broadside photograph on
the reference board. Freeboard at the main deck is 2.30 m, at the upper deck 5.30 m.

**Inference, clearly marked.** The *section shape* (rise of floor, bilge radius, flare)
is derived from the dry-dock photograph of *Paris* and from standard practice in the 1891
textbook, not from a traced body plan. The hydrostatic numbers are internally consistent
(displacement 13,482 t against a specified 13,600 t, 0.9%), but a real shipyard would have
run a full stability calculation, which this project has **not** done.

---

## 4. Structure

Period practice, from the 1891 construction chapter and Lloyd's rules of 1887:

- **Keel**: 25 mm plate, 1.22 m wide, with a bar keel below.
- **Frames at 0.9144 m (3 ft) centres** — the standard British spacing. 173 frames over
  the 158 m length between perpendiculars.
- **Shell 19 mm** in strakes **1.83 m (6 ft) wide**, riveted at 89 mm pitch with 22 mm
  rivets. The model builds the strakes and seams as geometry, because the plates and
  rivet lines are the visible grain of a riveted hull.
- **Stringers** at the deck edges and at the turn of the bilge.
- **14 transverse watertight bulkheads** (11 main + collision bulkheads forward and aft).
  This is at the upper end of the 10–12 typical of the class; the validator flags it as a
  warning rather than an error, and it is retained because the machinery spacing wants it.
- **Double bottom 1.30 m** deep, tank top at the tank-top deck.

**What is simplified.** The model carries the shell strakes, seams, stringers, deck beams
and bulkheads as geometry, but **not** the individual rivets as geometry (1.2 million of
them at 89 mm pitch would be unbuildable in Roblox). Riveting is represented by the seam
displacement and by material, and the rivet pitch is recorded in the manifest.

---

## 5. Machinery

**Why triple-expansion, and why this arrangement.** By 1889 the vertical inverted
direct-acting triple-expansion engine was the standard for an express liner; *Teutonic*
and *City of Paris* both had one. It is the correct choice for 14,000 IHP at 62 rpm, and
it is what the period photographs and the 1891 textbook show.

| Item | This ship | Period comparison |
|---|---|---|
| Cylinders (HP/IP/LP) | **0.965 / 1.575 / 2.565 m** | *Teutonic*: 1.09 / 1.73 / 2.79 m for 17,500 IHP |
| Stroke | **1.295 m** | *Teutonic*: 1.52 m |
| Expansion ratio | 1 : 1.63 : 2.66 | typical 1 : 1.6 : 2.7 |
| Revolutions | **62 rpm** | period practice, 55–65 rpm |
| Boilers | **9 cylindrical single-ended return-tube**, 4.2 m dia × 3.35 m, 11 bar | *Umbria*: 9 boilers; *Teutonic*: 12 |
| Condensers | 2, surface | standard |
| Propeller | **5.30 m dia, 6.90 m pitch, 4 blades**, manganese bronze | period practice, pitch/dia ≈ 1.3 |
| Shaft | 0.46 m | period rule for this power |
| Rudder | 17 m² | 1/60–1/70 of immersed lateral area |

The propeller law used in the Roblox controller is `speed = pitch × rpm × 60 × (1 − slip)`,
with slip 12% at service revolutions. At 62 rpm this gives **19.3 knots**, matching the
specification — so the animation, the speed and the physics agree with each other rather
than each being invented separately.

**Separately modelled moving parts** (required by the brief): three piston rods, three
crossheads, three connecting rods on a slider-crank solution, a crankshaft with three
throws at 120°, the propeller shaft, the propeller, and the eccentrics and weigh shaft of
the valve gear. These are separate objects in `models/module_machinery.blend` and separate
parts in the Roblox export, so they can be driven independently.

---

## 6. Funnels and masts — the design decision worth recording

The first arrangement put the funnels at x = +24 and −3 m. A ray-cast of an interior
camera proved that **the forward funnel passed straight through the library**. That is not
a modelling slip; it is a planning error, and it is exactly the class of mistake the
period avoided by running each uptake up a **dedicated casing** between rooms.

The arrangement was therefore re-planned:

- Funnels at **x = +30.0 and +4.5**, each rising through its own casing with the boiler
  room uptakes inside it. This mirrors *Teutonic*, whose library sat **between** the two
  funnels.
- Masts stepped **on bulkheads or in trunked vestibules** — foremast on the forecastle,
  mainmast in the gap between the after funnel casing and the music room, mizzen on the
  after bulkhead of the second-class smoke room.
- `shipdesign/validate.py` now checks both of these every build and fails the build if
  either regresses.

Boat stowage: 11 boats on Trotman davits, stowed at 17.9–18.7 m on the boat deck, with
the 25-ft steam cutter to starboard at x = 38 and the 25-ft rowing cutter to port at
x = −34. The davit geometry and the Agent-02 allocation are in `interfaces/boats_spec.json`.

---

## 7. Interiors

The interiors follow the *Ocean Magazine* photographs on the reference board directly:

- **Panelling.** Every first-class public room is panelled: a dado to 0.92 m, a moulding,
  raised panels above it, and a cornice under the deck beam. Bare plaster walls are what
  make a period room look modern, so the panelling is generated room by room from the
  room polygon.
- **Deckheads.** Transverse beams at 2.45 m centres, 0.16–0.20 m deep, with the plaster or
  panelled ceiling between them — as in every photograph.
- **Carpets** in the public rooms (green in the library, red in the dining saloon and the
  smoke room), **linoleum** in the galleys and crew spaces.
- **Lighting.** Hurricane and oil lamps in 1889, not electric pendant lights: warm,
  ~2400 K, one per cabin and clusters in the public rooms. The Roblox lighting script
  uses exactly that colour and brightness.
- **Furniture** is period: long communal tables down the dining saloon (as in the
  photograph), revolving chairs in the smoke room, leather settees round the walls, a
  ground-glass centre table in the library lighting the saloon below.
- **Staterooms** are 2.4 m wide × 3.1 m long with a single berth abreast, a washstand and
  a wardrobe — the proportion visible in the *Teutonic* stateroom photograph, not a modern
  hotel room.

**What is simplified.** Furniture is built from primitives and reads correctly at room
scale but is not carved or upholstered in detail. There are no table settings, no
crockery, no personnel, and no soft furnishings beyond the carpets.

---

## 8. What this model does **not** have

Stated plainly, because the brief asks for limitations to be reported honestly:

1. **No stability or strength calculation.** Displacement and coefficients are computed;
   GM, righting levers and longitudinal strength are not. A real 1889 design would have
   gone through both.
2. **No traced lines plan.** As noted in §1, no genuine 1880s lines plan was available.
   The hull is generated from period coefficients and section shapes.
3. **Individual rivets are not geometry** on the hull (pitch and diameter are recorded and
   the seams are modelled).
4. **Not every one of the 42 rooms is fully furnished.** The principal public rooms,
   staterooms, third-class spaces, galley and bridge are furnished; service spaces,
   store rooms and the shaft alley are modelled as spaces with their fittings.
5. **The engine is a plausible arrangement, not a specific engine.** Cylinder sizes are
   scaled from a real comparison engine of the same power, but no single 1889 engine was
   copied.
6. **Rigging is representational.** Stays, shrouds and the boat falls are modelled as
   cables at correct angles and sizes; the running rigging of the lug sails is not.
7. **No crew, passengers or boats under way during sea trials.** The Roblox layer provides
   the systems for play; it does not include a completed game loop.

---

## 9. Validation

`python3 -m shipdesign.validate` runs 13 drawing-office checks every build. Current state:
**13 passed, 2 warnings, 0 failures.**

Passing: deck schedule monotonic · all 42 room footprints valid and scalar-coordinate ·
every enclosed room has ≥ 2.0 m headroom · no two rooms on a deck overlap · both funnel
uptakes clear of every room · no mast through a furnished room · every room edge has a
full-height wall face (148 checked against the built mesh) · staircases connect every deck
from lower deck to bridge · boat outfit fits its davits · hull displacement within 0.9% of
specification · Cb inside the 1884–89 band · LCB 1.53% forward of amidships · bulkhead
count.

Warnings: 14 bulkheads is at the upper end of the 10–12 band (see §4); 26 third-class and
crew spaces open directly off a corridor or mess rather than through a recorded door,
which is correct for those spaces but not represented as door geometry.
