# LEONIDAS-II — previous-generation inspection

Audit started 16 November 2026, **before reconstruction geometry was created**.

## 1. Repository provenance and scope

Repository: https://github.com/dreamer2664/victoria . The remote's default is **agent/boats**, not the liner. There are four independent branch histories, with no combined project root:

| Branch | inspected tip | ownership / contents |
|---|---|---|
| agent/ship | `75bf4ac5770b803919b36c8dbdb5374df82d88ac` | liner; root `blender/`, `shipdesign/`, `models/`, `drawings/`, `reference/`, `exports/`, `roblox/`, `interfaces/` |
| agent/boats | `6bd984e7d9a95459bc9c1032f58bd5210a9c1159` | three boats; `boats/`, `refs/rmg/`, boats' Roblox code and interfaces |
| agent/ports | `dbcc091fb20f4a3f53ab29b46a09055ca0e735f4` | two ports; root asset library, port Blender and Roblox code, textures and documents |
| agent/qa-audit | `f2237f8bea5e25d6153100b98558360b787012db` | `QUALITY_ASSURANCE_AUDIT.md` and diagnostic renders |

`agent/leonidas-ii` branches from the ship tip. **No boat or port asset is to be edited or silently merged.** Each branch's complete file inventory and the full commit graph were recorded. The complete ship commit list/change descriptions and generator/runtime inventories were examined; selected historical diffs, the hull/machinery/export/build helpers and all seven runtime scripts received detailed source review. Long combined reads of old interior/superstructure and boat/port sources were partly truncated; this is **not** a claim of line-by-line inspection of every revision or every other agent's script. The QA report is evidence to investigate, not a substitute for opening the models.

### Missing evidence, not invented evidence

The original conversation/specification given to Agent 03 is **not committed**. The earliest ship commit is already a machinery/validator/export delivery. References to `/home/user/research/raw`, `research/HISTORICAL_EVIDENCE.md` and `tools_blender/run.sh` do not resolve within this repository. Uncommitted downloads, unsuccessful image-service requests and private museum plans cannot be recovered from Git. The committed README, `shipdesign/spec.py`, `layout.py`, interface and dimension manifest are therefore the recoverable design brief. This report does not pretend otherwise.

## 2. Vessel established from documentation

**SS Aurelian**, fictional British express passenger/mail-and-cargo liner, Liverpool–Queenstown–New York, designed as an 1889 completion. Original envelope: **166.0 m LOA, 158.0 m LBP, 18.4 m moulded beam, 6.50 m design draught**. Original plant: a single screw, one inverted triple-expansion engine, nine Scotch return-tube boilers, two funnels and three masts. This is **not** a steam launch, yacht or paddle steamer. Fictional company, yard, designer, dates, tonnages and performance are project design choices, not discovered historical facts.

The specification contradicts itself: stale 7.0/7.1 m waterline comments; boat deck quoted as both 16.6 and 17.2 m; bridge only 1.4 m above occupied boat-deck spaces; 9 boilers described as single-ended/four-furnace while built with furnace faces on both ends; conflicting displacement/deadweight totals; inconsistent boiler and funnel positions in different dictionaries. Preserve the principal envelope, not these contradictions.

## 3. Inspection actually performed

* The committed ship render set was visually reviewed using labelled contact sheets (not every plate reopened at native resolution): port/starboard broadside; both bow and stern quarters; bow-on, stern-on, above and below; six final interiors, eleven check interiors; engine cutaway, engine detail, shaft alley, hull section and body-plan render.
* All eleven committed ship drawing PNGs and all twelve historical ship plates were opened. Full-size reference images were used where detail matters; labelled contact sheets were used to compare coverage and repeated defects.
* The `refs/rmg/` inventory and README were read and **all six actual photographs** opened, not just their filenames. This does not imply that linked, unavailable launch sheets were opened. SLR0772 shows diagonal construction and thwarts; SLR1818 shows lapstrake planking, close frames, slatted floor and lifting eyes; SLR0719 shows contrasting construction treatments. These concern boats, not liner scantlings.
* Boat renders/drawings, the port visual set and eighteen inherited 1891 construction/harbour engravings were viewed on the recorded contact sheets to understand interfaces and shared historical evidence. **141 raster images** were inventoried across the branch tips. This is a visual-evidence inventory, not a claim to have certified the ports' or boats' entire geometry.
* Blender **4.2.3 LTS** was installed and all five ship `.blend` files plus the three boat `.blend` files opened headlessly. Mesh hierarchy, real bounds, polygon/triangle counts, UV layers, images, materials and object transforms were exported to JSON. The liner assembly contains **44 mesh objects, 287,408 source triangles, zero UV layers and zero images**. Its interiors module contains 15 merged meshes / 185,744 triangles. These are measured source counts, not the different FBX triangulation figures in the older QA report.
* All existing ship Luau scripts were read, including control, assembly, telegraph, lighting/doors, engine animation and effects. Source-level contracts were compared with actual object names.
* The original standalone validator was rerun: **12 pass, 2 warnings, 0 failures**. This is not the README's advertised 13 or the older audit's 14; optional scene checks explain some differences. Its pass does not certify usable rooms or moving geometry.

Machine-readable inspection records and commit/file inventories accompany this report in `inspection/`.

## 4. Visual and geometric findings

### Hull / structure

**Worth retaining:** the overall narrow liner envelope, sheer concept, fine entrance, round bilge intent, single-screw counter arrangement and the pure-Python control-curve work as a design starting point. The concept has a recognisable late-Victorian silhouette.

**Rebuild:** source shell topology, stern aperture, keel junctions, plating detail, ports and structural interior. Existing shell has open boundaries and inconsistent face winding (also independently identified by prior QA). Underwater plates are largely unarticulated. White rectangles along the exterior are not convincing portholes. Scuppers and material seams do not compensate for absent dimensional construction. Structural drawings are useful concepts but not complete manufacturing plans.

### Superstructure / deck equipment

**Worth retaining:** two buff/black funnels; three-mast silhouette; open promenade as a functional idea; allocation of ship's boats and a metric origin/scale convention.

**Rebuild:** room-derived deckhouses, apertured walls, proper white external steelwork versus interior oak, glazing, trim, rails, support brackets, deck planks, funnels with actual mouths, rigging terminals, deck machinery and boarding openings. Existing broadside reads as stacked long rectangular brown boxes with floating white window slabs. There are conspicuous open black ends. Decks include zero-thickness surfaces.

The actual `Bridge` bounds are x=30.00..43.35 m while `Wheelhouse_Fittings` is x=13.90..18.47 m. Navigation lights are near x=12.5 m, not the bridge wings. Rebuild all from one placement definition rather than translating a merged group by eye.

### Interior: reject the finish, redesign the arrangement

The dining room has numerous rudimentary ladder-back chairs and continuous white table strips, but little usable furnishing detail or visual hierarchy. The library is predominantly an enormous flat table and nearly bare room, with a small patch of books at the far end. The music room is essentially benches and a rectangle. The galley is an octagonal central primitive and simple slabs. The bridge render is an empty room. The staircase evidence includes obstructed views, open black voids and no convincing connection to the boat deck. Cabins are poorly exposed, barely furnished and merged together.

Measured examples: `Music_Room` **450** triangles; `Galley` **636**; `Officers_Captain` **568**; `Lavatories` **288**; `Wheelhouse_Fittings` **292**. Low counts alone are not the fault; they demonstrate why descriptions of finished furniture and fittings are unsupported by the actual close-ups. Every public/service room and every cabin type requires new dimensional joinery, upholstery, fittings, storage, lights and finishes. There is no finished furniture worth importing unchanged.

The original room schedule is not a complete accommodation plan. It counts 42 **zones** as if they were rooms, repeats unnamed third-class areas, puts holds across boiler positions, leaves most doors implicit and does not reconcile its passenger capacity with actually built berths. Re-plan physical rooms and circulation; keep nominal design capacity separate from counted modelled accommodation.

### Machinery: replace, not decorate

Measured original shaft axis: z=**2.05** m; crank axis: z=**2.35** m. Propeller z=**−0.60..4.70** m; shaft x=**−83..−21** m. It extends through the rudder region instead of terminating at the hub. The LP rod is only **0.06 m** tall. Most crank webs, pins, crossheads and connecting rods are merged into static `Engine_Main`. A rotating bare cylinder cannot animate that assembly correctly. Boiler-room source bounds exceed the designed inner hull at their bottom. The historical text and built boiler arrangement disagree.

Rebuild a connected, numbered steam/water/exhaust plant, a real three-throw crankshaft, dimensionally solved crossheads/conrods, bearings, aligned shaft line, stern tube, a thick pitched propeller, steering stock/quadrant and an independently accessible machinery space. Intentional fitted joints must be distinguished from accidental penetrations.

### Materials and textures

There are **no source texture images or UVs** in the liner. Colours are almost entirely flat Principled shaders. Some useful conceptual material names can inform the new palette, but no texture pipeline is worth preserving. Rebuild UVs and original tileable base-colour/roughness/normal maps. Wood direction, scale, cast/rolled metal, glass thickness, cloth seams, carpet motifs and roughness must survive export; Blender procedural nodes alone are insufficient.

### Roblox

Useful ideas: one authoritative server state, the 0.28 m/stud scale, signed telegraph orders, slow shaft response, prompt-based mobile/console interaction and attribute publication. Preserve these **ideas**, not the faulty implementation.

Blockers confirmed by source review: `math.radians` is not Luau; controller moves only `PrimaryPart` while assembly anchors every part without welding; output bow is +X while controller advances −Z; heave is integrated into previous-frame height and can drift; RPM is published absolute (losing astern); assembler measures object centres rather than true extents; moving/interactive parts searched by name do not exist in merged exports. Collisions are enabled indiscriminately on visual details. Door/seat/light/helm/telegraph/particle contracts need to be generated from the actual new model.

## 5. Historical corrections to carry into reconstruction

1. **Electric lighting is appropriate in 1889.** The actual September 1889 *Ocean* account explicitly describes electric lights in steerage, staterooms, library/smoking room and dining saloon. The old categorical “oil lamps, not electric pendants” assertion is wrong. Include period incandescent fittings and a dynamo room; oil lamps only as emergency fittings.
2. **No wireless room in 1889.** Replace that label with chart/signal storage, speaking tubes, flags and navigational instruments. Later passenger-list descriptions of Marconi equipment must not leak into the 1889 design.
3. **Twin screws are not inherently post-1889.** *Teutonic* and *City of Paris* already had them. Retain a single screw because it is the recoverable Aurelian brief, not because of the previous mistaken date argument.
4. The Jacobsen three-funnel painting labelled simply “City of Paris” is not authority for this two-funnel single-screw design; vessel/date identification is insufficient. The small dry-dock photo does not expose the detailed underwater body claimed in the old board. Do not claim to trace either.
5. Not all prior QA aesthetic opinions are historical rules. Three pole masts without square yards are explicitly described for *Teutonic* in the 1889 text. A partial auxiliary rig is a design choice, not an obligation to turn Aurelian into a full-rigged barque.
6. RMG **NPC9465 (1880, 80-ft launch)** and **STD0019 (27 Nov 1895, launch)** are period-adjacent technical references only. Neither supplies Aurelian's liner dimensions or hull lines. Public catalogue metadata loaded; no plan image was served on those object pages during this audit. Do not claim to have viewed an unavailable sheet.

## 6. Disposition / release gates

**Preserve:** vessel identity, principal dimensions, scale, archival evidence, old generations as provenance, and analytical control-curve ideas where checked.

**Substantially re-engineer:** hull form/topology, deck schedule, room and passage planning, boat/port attachment contracts, export pipeline and control logic.

**Rebuild from new geometry:** interior, machinery, shell/ports, superstructure, joinery, furnishings, fittings, textures, interaction pivots and collision proxies.

No completion claim is permitted from a mesh count, generator exit code or attractive exterior alone. Required evidence: actual model renders, every major interior type, engine/stern close-ups, metric-to-Roblox axis tests, split mesh counts, name-contract checks, circulation/headroom checks and an explicit Roblox Studio acceptance sheet. Headless tests do **not** constitute a Studio multiplayer walk-through or a naval stability/strength certification.
