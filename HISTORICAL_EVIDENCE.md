# HISTORICAL EVIDENCE

Everything in the two ports is either (a) taken from a source that is quoted or cited
below, or (b) an explicit, recorded inference from type-plans and period photographs.
Nothing is included because it "looks Victorian".

The model's horizon is **1889**. Anything built after 1889 is excluded, even where it
is the most famous feature of the port being emulated.

---

## 1. The hard date line

| Excluded | Date | Why it matters | Consequence in the model |
|---|---|---|---|
| Thompson Graving Dock, Belfast | 1902–1911 | The dock everyone associates with Belfast; not 1889 | Not built. The 1885–89 Princess (Alexandra) dock is used instead. |
| Arrol Gantry, Belfast | 1905–1908 | The iconic portal gantry over the slips | Not built. Ships are handled by sheer legs, a Titan crane and slip cranes. |
| Olympic-class slipways, Belfast | 1908–1911 | Rebuilt and lengthened | The three slips are modelled to 1885–89 proportions (34 m wide, 96 m long ways). |
| Southampton No. 5 dry dock | 1896 | Post-dates the horizon | Not modelled. |
| LSWR purchase of Southampton docks | 1892 | Post-dates the horizon | Not modelled. |

This is the single most important discipline in the project: the two most
recognisable "Belfast shipyard" objects in the world are both too late, so Port B
had to be built from the 1880s yard instead.

---

## 2. Sources consulted

### 2.1 *Ocean Steamships: A Popular Account of their Construction, Development, Management and Appliances* (New York, 1891)

Project Gutenberg eBook #54136. Read in full text and, critically, **in its plates**:
105 period photographs and engravings, 18 of which are reproduced and annotated on
`reference/reference_board.html`. This is the single best source in the project
because it is (i) contemporaneous, (ii) photographic rather than illustrative, and
(iii) covers both the passenger side and the building side of the industry.

Design-relevant content extracted:

- **The shipyard frontage.** The Belfast yard is described as having "the
  launching-slips, where as many as fifteen vessels have been in course of
  construction at the same time", with a fitting-out dock cut at right angles to the
  river, and "a net-work of rails which connect the works with all the principal
  lines". → Port B's three slips, the fitting-out quay, and the yard rail system.
- **The moulding loft.** "where all the iron-work for the hulls of fifteen ships has
  been handled at one time". → A long top-lit loft floor with a floor-level
  interaction point.
- **Boundary and access.** "the high brick walls which keep out idlers". → Port B's
  3.6 m soot-brick estate wall with a stone coping, and a single controlled time
  office gate.
- **Materials handling.** "great stacks of timber, iron, and steel". → Port B's
  timber yard, plate stacks and the sawmill.
- **Coaling.** Coaling from barges on the offside of a berth took about 4.5 days with
  8 barges of 250–300 t. → Port A's coal staithes and barge berths on the *offside* of
  the main passenger berth, not on the passenger quay.
- **Package traffic.** 10,000–100,000 packages per call, worked by 6 gangs of 25 men.
  → The scale of Port A's cargo sheds and the number of quay-side winches.
- **Turnaround.** A North German Lloyd liner of the period turned round in ~29 hours.
  → Berth lengths and the through-route of the terminal are sized so that a
  disembarkation and an embarkation can overlap.
- **Cattle pens.** Pens of 2 ft 6 in by 8 ft, slatted. → Modelled to that size.
- **Strake and rivet practice.** Strakes lettered from the keel; countersunk rivets.
  → Reference for the drawing office / loft dressing, not modelled as geometry.

### 2.2 Belfast dock history (Visit Belfast, "Quays, Docks and Slipways")

- **Alexandra Dock**, cut 1885, opened 1889: "just over 800 feet long and 80 feet
  wide", **the largest dry dock in the world at the time**, and "designed to be
  separated into 3 sections, using caissons to have a combination of dry and flooded
  dock space". Its caissons were built by another local shipbuilder and given yard
  numbers 53 and 54.
  → **Port B's Princess Graving Dock: 243.8 × 24.4 m, three working sections, two
  intermediate caisson stops plus an entrance caisson.**
- **Hamilton Dock**, 1864–67, and **Clarendon Docks** No. 1 (1800) / No. 2 (1826).
  → **Port B's No. 1 Graving Dock** (the older, smaller dock the great dock was built
  to supplement): 120 × 18 m, single section, flooded with its caisson seated.
- **Queen's Quay**, Belfast & County Down Railway station, 1848.
  → Justifies the railway running right onto the quay at both ports rather than
  stopping at a goods yard inland.

### 2.3 Maritime Archaeology Trust — Liverpool dock system

- Liverpool had **43 docks** in a **7.5-mile interconnected non-tidal system**, so
  that a ship could pass from the river into any dock without waiting on the tide.
- The **Mersey Docks & Harbour Board** operated **104 miles of freight railway**
  within the estate.
- Glasgow, by contrast, had tidal basins.

→ **Port A's geography is non-tidal**: an enclosed dock system entered through a lock,
with the water level held at a constant height. This is why Port A's quays, sills and
beds are all at fixed levels (`water 0.00`, `coping +4.00`, `lock sill −10.50`,
`dock bed −8.00`) rather than following a tide. It also justifies the extent of rail:
the 104-mile figure is why the quay has track running along it continuously.

### 2.4 National Museums NI — Harland & Wolff archive

- c. 75,000 images, from the 1890s onward, much of it by the photographer Robert
  Welch; includes plan types (general arrangement, lines, framing, inboard works).

→ Reference for the **drawing-office dressing** of the moulding loft and for the
conventions used on the layout plans in `docs/`.

### 2.5 Royal Museums Greenwich — ship plan conventions

- Plans are drawn **bow to the right**, at **¼ in : 1 ft**, and are organised as
  lines plan / deck plan / framing plan / inboard works plan.

→ The plan sheets in `docs/port_a_layout.md` and `docs/port_b_layout.md` follow the
same convention (north up, bow right, one dimension standard throughout).

### 2.6 Southampton City Council / SOU 1586

- LSWR purchased the docks in **1892**; No. 5 dry dock opened **1896**.

→ Examined and **rejected** as a source, purely on date. Recorded here so that the
exclusion is auditable rather than accidental.

---

## 3. Decision register

Each row: the decision, the evidence, and whether it is **documented** (a source says
so) or **inferred** (a reasoned extrapolation, recorded so it can be challenged).

### Port A — passenger harbour ("Port of March Hampton", Liverpool type)

| # | Decision | Evidence | Status |
|---|---|---|---|
| A1 | Enclosed non-tidal dock system entered by a lock | MAT: 43 docks, 7.5-mile non-tidal interconnected system | documented |
| A2 | Floating landing stage on chains serving two berths | Plate `i_191`, "Landing Stages at Liverpool" | documented |
| A3 | Enclosed, roofed embarkation gangways with a ticket check at the shore end | Plate `i_132`, "The Gang-plank — just before sailing" | documented |
| A4 | Separate customs & immigration hall on a one-way route from ship to street | Plate `i_142`, revenue officer boarding; clearance is a distinct step | documented |
| A5 | Baggage hall separate from the passenger hall | Plates `i_139`, `i_145` | documented |
| A6 | Cattle pens 2 ft 6 in × 8 ft, slatted, on the north quay | O.S. cattle-pen dimensions | documented |
| A7 | Coal staithes and barge berths on the **offside** of the main berth | O.S. coaling practice: barges both sides, ~4.5 days, 8 × 250–300 t | documented |
| A8 | Rail laid along the quay continuously, serving the sheds | MAT: 104 miles of MD&HB freight railway | documented |
| A9 | Transit sheds with open sides to the quay and doors to the street | Plate `i_227`; standard Liverpool shed type | documented |
| A10 | Berth B1 26 × 212 m at 11 m depth | Sized to the specified 180 × 20 × 9 m envelope + 4 m clearance rule | inferred |
| A11 | Booking-hall interior: panelled dado, cased beams, clerestory, brass | Plate `i_115`, Inman saloon | inferred |
| A12 | Harbour board offices separated from shipping-company offices | Period port administration; MD&HB vs line agents | inferred |

### Port B — industrial harbour ("Port of Carrickmore", Belfast type)

| # | Decision | Evidence | Status |
|---|---|---|---|
| B1 | The Princess Graving Dock, 243.8 × 24.4 m (800 × 80 ft) | Alexandra Dock 1885–89, largest dry dock in the world | documented |
| B2 | Three working sections divided by caissons | Alexandra designed to be split into 3 by caissons | documented |
| B3 | A separate older, smaller dock (No. 1, 120 × 18 m) | Hamilton Dock 1864–67; Clarendon 1800/1826 | documented |
| B4 | Three building slips on the river frontage, 34 m wide | O.S.: the frontage "lined with launching-slips" | documented |
| B5 | Moulding loft behind the slips, long and top-lit | O.S.: the loft handled ironwork for 15 hulls at once | documented |
| B6 | High soot-brick boundary wall with one controlled gate | O.S.: "the high brick walls which keep out idlers" | documented |
| B7 | Timber yard + sawmill + plate stacks | O.S.: "great stacks of timber, iron, and steel" | documented |
| B8 | Yard rail network connecting shops to the main line | O.S.: "a net-work of rails which connect the works with all the principal lines" | documented |
| B9 | Slips dressed with keel blocks, raking shores and staging | Plates `i_094`, `i_099`, `i_102`, `i_103` | documented |
| B10 | Titian/Titan-style crane + sheer legs at the fitting-out quay | Plate `i_099` erecting cranes over the frames | documented |
| B11 | Fitting-out quay in deep water at right angles to the slips | O.S.: a fitting-out dock cut "at right angles to the river" | documented |
| B12 | Slips rake at 2.6° over 96 m of ways | Launch-slip geometry derived from plate `i_109` and slip practice | inferred |
| B13 | Engineering and boiler shops with an overhead travelling crane | Plate `i_087`, an engine of this scale needs a craned bay | inferred |
| B14 | Dock depth increased from Alexandra's 26 ft sill to 11 m | Required by the specified 9 m draft; see §4 | **adaptation** |

---

## 4. Recorded adaptations

These are places where the historical form and the specified ship do not fit, and the
resolution chosen. Each is a deliberate deviation, not an error.

1. **Graving dock depth.** Alexandra Dock had about 26 ft (7.9 m) of water on the sill.
   The specified ship draws 9 m, and needs 1.7 m of keel blocks under her keel. Port
   B's Princess Dock is therefore 11.0 m from coping to floor. The *plan* dimensions
   (800 × 80 ft, three caisson sections) are exactly as built; only the depth is
   increased, and it is recorded in `docs/port_b_meta.json` under `"adaptation"`.

2. **Berth lengths.** The specified 180 m envelope with a 4 m clearance rule requires
   a 188 m clear berth. Liverpool's berths of the period were shorter and were worked
   by a ship moored to the stage with her ends overhanging. Port A's berth B1 is
   therefore 212 m. The *form* (a quay with the floating stage alongside) is
   unchanged; the length is stretched.

3. **Slip length.** A 96 m way will not take a 180 m hull. This is historically
   correct — ships far larger than the ways were launched from them, and the ways
   serve vessels building under normal 1880s lengths. The specified envelope is
   handled at Port B's **fitting-out quay** (210 m), not on the slips.

4. **Dock width vs. caissons.** Fitting two intermediate caisson stops plus an
   entrance caisson into 244 m gives 81 m sections. That is what Alexandra gave; no
   adaptation was needed, but it does mean no section will hold the full 180 m
   envelope, which is correct — a docked ship occupies the whole dock with the
   caissons open.

---

## 5. What was rejected, and why

- **Pirate/fantasy harbour imagery.** Rejected at brief level: the ports are
  commercial estates with offices, gates, rail and paperwork, not coves.
- **Generic "old port" props** (rope coils, anchors as decoration, treasure). Not
  modelled. Everything on the quay has a job: a bollard, a capstan, a winch, a
  crane, a wagon, a stack of a specific cargo.
- **Modern dock furniture** (container-style stacking, floodlight masts, bollards with
  reflective bands, safety-yellow anything). Excluded; checked material by material.
- **Downloaded ship models.** The brief forbids them, and they would have dictated the
  berth dimensions. The only ship-form geometry in the project is
  `blender/lib/proxy.py`, which is a **clearance block-out** — a 180 × 20 × 9 m box
  with a bow — used solely so that berth clearances can be tested numerically. It is
  exported under the reserved name `_PROXY_liner` and must be deleted before shipping.
- **Post-1889 photographs.** The reference board contains only plates published in or
  before 1891; none is used to justify a form that did not exist by 1889.
