# SS Aurelian — LEONIDAS-II design basis

## Identity, evidence and limits

Aurelian remains the project's **fictional 1889 Atlantic express passenger/mail-and-cargo liner**, not an historical ship and not a steam launch. Retained principal envelope: **166.00 m LOA / 158.00 m LBP / 18.40 m moulded beam / 6.50 m design draught**, 0.28 m per Roblox stud. The model is a researched interpretation. No authentic Aurelian shipyard drawing exists and no genuine liner lines plan was traced. Comparators are not silently passed off as Aurelian's plans.

Inspection records: [previous generation](PREVIOUS_GENERATION_INSPECTION.md), `inspection/`. Inspection of old source/models/images preceded construction of new geometry. Source code and analytical arrangement are editable inputs, not evidence that the corresponding mesh already passed visual checks.

## Source register (accessed 16 November 2026)

| ID | Source and stable URL | Actual evidence used / limits |
|---|---|---|
| P01 | Chadwick et al., **Ocean Steamships**, Charles Scribner's Sons, 1891. Complete period book via [Waterloo Gutenberg mirror](https://mirror.csclub.uwaterloo.ca/gutenberg/5/4/1/3/54136/54136-h/54136-h.htm). Original [Gutenberg 54136](https://www.gutenberg.org/ebooks/54136) was returning maintenance. | Construction and speed/machinery chapters; structural and engine engravings **actually opened**. Sequence keel → floors/frames/reverse frames → beams/stringers → shell/rivets. Book published two years after the chosen date; distinguish contemporary practice from exact 1889 installation. American public-domain text/illustrations; do not copy modern website design. |
| P02 | *Ocean: A Magazine of Travel*, Vol. III No. 2, September 1889, Teutonic account, reproduced by [GGArchives](https://www.ggarchives.com/OT/Ships/Teutonic.html) and [issue contents/illustrations](https://www.ggarchives.com/OT/Publications/OceanMagazineOfTravel-1889-09.html). | Oak stairs/newels, writing desks/revolving chairs, embossed leather smoking-room seating, patterned rubber floor, ivory/gold dining finish, electric incandescent lights. Page includes much later material: **Marconi descriptions are excluded**. Modern summary dimensions are not mixed with period article as if one specification. |
| M01 | Smithsonian NMAH, **Model, Vertical Marine Steam Engines**, object MC.310578 / nmah_846155: https://www.si.edu/object/model-vertical-marine-steam-engines:nmah_846155 | Actual photo opened. Compounding, graduated cylinder bores, guides, crossheads, connecting rods and common crankshaft. Model's date not established as 1889; comparative mechanical evidence only. Metadata marked CC0; external museum media attribution retained, no exclusivity claimed. |
| M02 | Royal Museums Greenwich, [ship plans collection guide](https://www.rmg.co.uk/collections/our-collections-ship-plans-collection) | Distinction among lines, framing, deck and inboard plans; profile convention. General research guide, not a liner plan. |
| M03 | RMG **NPC9465**, [unnamed 80-ft launch, 1880, 1:24](https://www.rmg.co.uk/collections/objects/rmgc-object-1182149) | Catalogue text accessed. **No actual sheet image was provided on the accessible page.** Cannot claim line tracing/visual inspection. Launch arrangements must not determine liner size/type. |
| M04 | RMG **STD0019**, [unnamed steam launch, 27 November 1895, 1:12](https://www.rmg.co.uk/collections/objects/rmgc-object-532343) | Catalogue text accessed. **Actual sheet unavailable** on accessible page. Later than 1889, period-adjacent technical comparator only. |
| M05 | RMG SLR0772, SLR1818, SLR0719, photographs preserved on `agent/boats` under `refs/rmg/` | All six real photographs opened. Boat planking, thwarts, framing and lifting eyes only. Not used as liner scantling authority. Original agent's model/image licensing notes still apply. No other agent's assets modified. |
| R01 | Twelve inherited comparator plates, `reference/plates/`, provenance in inherited `reference_index.json` / `HISTORICAL_EVIDENCE.md` | All visually examined. Teutonic/Majestic/Germanic/Paris exteriors and Teutonic interiors supply period vocabulary. The Jacobsen painting's vessel/date identification is uncertain; not used for underwater form, machinery or exact deck arrangement. Small Paris dry-dock image is not a lines plan. |

### New locally retained historical images

`reference/leonidas_ii/` (all eight opened at original image size during audit):

* `i_040_a.jpg`, `i_040_b.jpg`: transverse structural comparisons. Plate with frame/reverse-frame/floor system, not a complete set of offsets.
* `i_041.jpg`: **Aller / Trave / Saale** triple-expansion installation, not Teutonic. Shows columns, guide frames, open working levels, raised cylinders, ladders and crank-bearing arrangement.
* `i_087.jpg`, `i_099.jpg`, `i_103.jpg`: hull construction/framing, floors/keelsons, transverse deck beams and pillars. Use for structural relationships; do not infer unseen shell thickness from the photographs.
* `i_102.jpg`: marine-engine engraving, a comparator rather than a literal Aurelian plant. Valve linkages/operating controls and tie rods. Earlier work-in-progress captions reversed `i_087` and `i_102`; corrected against the opened images.
* `smithsonian_vertical_engines.jpg`: M01 museum photograph. Compounding and moving-part relationships. This local research copy is excluded from the Git publication because the accessible page distinguishes CC0 metadata from media usage restrictions; use the linked museum record and see ATTRIBUTION.md.

Book image URLs are the P01 HTML directory plus `images/<filename>`. Smithsonian image endpoint: https://ids.si.edu/ids/deliveryService?id=NMAH-AHB2016q019120&max_w=1200 . No AI-generated image is used as historical evidence or as a substitute for an actual model render. New material maps are original procedurally authored textures, not borrowed photographs.

## New arrangement / structure

* All coordinates in `shipdesign/leonidas_ii.py`; +X bow, +Y port, +Z baseline. Working waterline z=6.5. Preserve the examined longitudinal curve intent; rebuild the section topology and a fuller counter overhang. The original shell mesh is not reused.
* New deck heights: orlop 2.35, lower 5.20, main 8.80, saloon 11.80, promenade 14.40, boat 17.20, bridge **20.00 m**. The old bridge/boat separation of 1.4 m was uninhabitable.
* Physical compartment IDs, boundary walls, door centres, furnishings, ceiling height, deck cutouts and stairs come from one room record. No separate manually translated bridge or window group.
* Two accommodation passages around the central first-class cabins; grand stair and independent fore/aft service escapes. Service/casing areas are not labelled as passenger rooms. The current geometry counts **628 passenger berths (228 first / 132 second / 268 third) and 117 crew berths**. These are fixture counts, not a certified passenger complement. The planning schedule still totals 900 passenger / 196 crew targets, while the inherited claim was 1,080 / 196. Neither target has been achieved; reducing bunk rows for real circulation and mess alcoves is a deliberate capacity shortfall, not an extra 272 invisible passengers.
* Structure uses a mesh shell of finite thickness, real opening reveals, bar/plate keel, riveted strakes, angle frames/reverse framing, floors, keelsons, deck beams/knees and bulkhead compartments. These are representative game geometry, not class-approved scantlings. Fine fasteners are concentrated where inspectable; surface maps carry sub-millimetre detail elsewhere.
* Room surfaces: raised oak/mahogany panels with skirting/dado/cornice; ivory/gold dining and music rooms; patterned rubber in the smoking room; wool carpet and cloth; individual book spines/pages, writing desks and upholstered seats; washbasins with an actual bowl, taps, tub and plumbing; proper ranges/ovens/flues and pantry shelving. Repeated cabin types still receive individually accessible physical rooms and usable fixtures.

## Machinery correction (explicit design choices)

The old .965/1.575/2.565 m cylinders, 1.295 m stroke and 62 rpm were not a plausible 14,000 IHP plant. Its pitch/RPM calculation produced about 12.2 knots, not the advertised 19.3.

The revised **single** inverted triple-expansion design uses **1.40 / 2.25 / 3.50 m bores, 1.80 m stroke, 3.00 m connecting rods, 0.90 m crank radius, 72 rpm nominal**. These are Aurelian design choices informed by P01's contemporary engine-size range, **not copied dimensions of Teutonic** (which had two engines). Working boiler pressure remains 11 bar; no pressure-vessel certification is implied. Engine height requires a genuine main-deck machinery casing; cabin generation excludes it.

Nine **single-ended** return-tube Scotch boilers, 4.2 m diameter / 3.35 m barrel, three rows at x=3.0/15.5/28.0, three athwartships at y=−4.4/0/+4.4. Furnace doors are on the **after end only**. There are connected smoke hoods and collector uptakes to the two funnels. Steam main, HP→IP receiver, IP→LP receiver, LP exhaust→condenser, feed pump→boiler feed main, sea intake→circulating pump→condenser→overboard have named endpoints.

Shaft centre **z=3.00 m**, propeller plane **x=−78.00 m**, rudder stock **x=−79.50 m**. A new stern-frame aperture separates shaft, 5.30 m four-blade pitched bronze propeller, rudder and counter. Shaft and crank share the same axis. Propeller nominal pitch **9.40 m**, advance ratio .88 at 72 rpm gives **19.295 knots** kinematically. This is a gameplay target, not a resistance/sea-trial result. Rotating crank webs/pins, exact slider-crank crosshead positions, pivoted conrods and reciprocating rods remain separate in export.

## Boat / port integration handoff (not bilateral approval)

Inspected boat tip `6bd984e`, port tip `dbcc091`. No direct agent messaging or joint Studio session occurred. This is a **versioned unilateral compatibility handoff**, not a claim that Themistocles-II / Pericles-II approved it.

* Shared scale .28 m/stud; liner export deliberately maps metric authoring point `(x,y,z)` to Roblox metric `(-y,z−6.5,−x)`; bow becomes −Z, port becomes −X, load WL becomes Y=0. Convert once to studs after import. Port has its own +X-along-quay mapping; do not apply the liner transform to port meshes.
* Ship davit SWL: steam cutter **3,900 kg**, rowing cutter **2,100 kg**, whaler **1,700 kg**, per latest boat contract. Replaces insufficient inherited 2,000 kg generic rating. These are required nominal ratings, not engineered/certified lifting gear.
* Mount records include sling stations and exact latest boat cradle contact levels. Mounts are **empty host sockets**, not duplicate crude boats. Actual boat assets remain owned by the boats branch. Steam origin x=37.2, y=−6.0; rowing x=−34,y=+6; whaler x=−20,y=+6. Authoring support positions are adjusted to contact the cradle at boat deck z=17.2. Boat README/hydro use loaded WL z=0, but orientation prose says light WL; flag contradiction to owner and use hydro contract, not both.
* Principal berth envelopes A-1 / B-1 accommodate 166×18.4×6.5 m on paper (180×20×9 envelope). This does **not** establish channel turning or actual water-depth mesh validity. The passenger quay at +4.0 m relative WL and Aurelian boarding at +2.3 m need a sloping gangway. Runtime creates a stowable ship-owned gangway; no port geometry is altered.
* Original claimed eleven carried boats are not silently certified with only three shared craft sockets. Boat capacity / complete lifesaving inventory remains an acceptance limitation unless separately modelled and tested.

## Delivery / acceptance

Build editable source, independent geometry modules, maps, spatially split standard GLB exports, source-of-truth JSON and native Studio setup/runtime scripts. The regional GLBs are distributed in a solid-compressed `.tar.xz` import kit; no new FBX compatibility claim is made. Test actual triangulated meshes, UV coverage, finite transforms, openings and room-envelope fits. Visually inspect every major compartment type and all deck arrangements; record image names and shortcomings. A console exit code cannot replace images. Roblox Studio is not installed in this workspace; multiplayer transport, Studio import, avatar collisions and performance must be marked **unverified** until tested there.
