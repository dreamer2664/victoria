# SS Aurelian · LEONIDAS-II delivery report

**Status: reconstruction review candidate, not an accepted playable release.** The current build-12 source/export checks, including actual-shell structural regression and independent normal/precision gates, are complete. The current-source render and manual visual-review pass is in progress. Roblox Studio acceptance remains open; exact local-commit and remote-publication outcomes belong to the local receipt / final handoff. Do not infer completion from the exterior or the counts below.

## 1. What was preserved, rebuilt and added

The recoverable brief is a fictional **1889 British Atlantic express passenger/mail-and-cargo liner**, Liverpool–Queenstown–New York. Its **166.00 m LOA / 158.00 m LBP / 18.40 m moulded beam / 6.50 m design draught**, single screw, nine boilers, two funnels, three pole masts and shared 0.28 m/stud scale are retained. It was not replaced with a launch, yacht, paddle steamer or a literal Teutonic replica.

| Disposition | Work |
|---|---|
| Preserved | Identity/function/principal envelope; examined longitudinal hull-control intent; shared metric scale; historical research/provenance; useful concepts of authoritative server state, telegraph/helm/prompts and published attributes. |
| Substantially rebuilt | Section/shell topology and counter stern, keel/stern-frame aperture, plate laps/fasteners, ports/boarding openings, finite decks/cutouts, framing/floors/keelsons/beams/bulkheads; room-derived superstructure and circulation; interior finish/furnishing; plant, shaft and steering; export and runtime implementation. |
| New | 203-space physical inventory; meaningful furniture templates and room fixtures; original UV/PBR atlas/signs; matched native collisions and movers; calibrated regional GLBs; install/control/smoke-test modules; exact-source logic harness; actual-model evidence registry; analytical SVG/PDF sheets; source and acceptance registers. |
| Kept as provenance, not installed | Original models, generators, drawings, interfaces and all legacy controllers at base commit `75bf4ac5770b803919b36c8dbdb5374df82d88ac`. No other agent's boat/port/QA asset is overwritten. |

The audit **preceded** reconstruction. See [PREVIOUS_GENERATION_INSPECTION.md](PREVIOUS_GENERATION_INSPECTION.md) and its recorded branch/history/Blender/image inventories. The old assembly had 44 mesh objects / 287,408 triangles, no UV layers or image maps; its low-detail merged interiors and static machinery were not reused as finished assets.

## 2. Measured current build

From `exports/leonidas_ii/build_data.json`, `game_manifest.json` and `IMPORT_KIT_MANIFEST.json`:

| Item | Measured result |
|---|---:|
| Editable master mesh objects | 1,422 |
| Editable master triangles | 3,300,554 |
| Explicit physical-space inventory entries | 203 |
| GAME visual nodes, excluding calibration | 1,438 |
| GAME unique meshes / reused placements | 860 / 578 |
| GAME placed triangles / unique geometry triangles | 2,473,152 / 2,166,940 |
| Maximum triangles in one GAME visual node | 18,000 |
| Complementary regional GLBs | 18 |
| Master native collision proxies | 4,071 |
| Compartment doors | 196 |
| Named machinery/helm/rudder/gangway moving assemblies | 20 |
| Generated native seats | 219 modeled positions, including four crew-mess bench seats; plus helm VehicleSeat |
| Registered modeled light positions | 346 |
| Main stair flights / engine ladders | 13 / 4 |

Master SHA-256: `ac604ee3238339de176d5816e325dff61508a21c013d48d6e9dae020cf9880c4`.

The import archive is **35,690,308 bytes**, SHA-256 `6f662a149daf6d19f10980b8a41425894e582b3b7f1f82ccd7b5d84578e81fe3`. It contains standard regional GLBs, not a flattened single mesh or fabricated uploaded asset IDs. Solid XZ reduces duplicate embedded-map compression streams; it does not change the geometry. Source maps are 2048², embedded regional image mip levels 1024². These counts are an export budget disclosure, **not proof of acceptable Roblox FPS**.

### Built accommodation is less than the targets

* **628 passenger sleeping positions:** 228 first, 132 second, 268 third. The first-class count is **114 permanent beds plus 114 modeled convertible upholstered settee berths**, one of each per cabin—not 228 permanent bed frames. Settee conversion animation and live sleeping use have not been implemented/accepted.
* **117 crew berths**, including the modeled captain/officer accommodation.
* First-/second-class dining: **96 / 48 actual chairs**. The first-class 228-seat schedule value is a target, not built seating. No one-sitting capacity is implied.
* The room-schedule target remains **900 passengers / 196 crew**; the inherited claim was 1,080 / 196. **Neither is achieved.** No invisible passengers, crew, chairs or unbuilt boats are counted.

The inventory comprises 114 first-class cabins, 33 second-class cabins, six officer cabins, one captain's cabin, five third-class and five crew dormitories, seven machinery spaces and the public/service/working spaces. Repeated cabin types are individually bounded/furnished/accessed physical spaces, not 203 unique furniture designs.

## 3. Interior, structure and mechanical scope

Public rooms include first/second dining, library/writing rooms, smoking/music/drawing and second-class lounges, stair halls and bar. Cabin/crew/third-class accommodation has real bed/bunk frames, mattresses, pillows/blankets, wardrobes/washstands or purpose-appropriate storage, and dimensional doors/finishes. Service rooms include galley/ranges/pots/connected common flue, bakery, pantry/cold/provision storage, bathrooms/lavatories/washrooms, hospital, purser/mail/barber/chart/navigation spaces and cargo fittings. Furniture uses turned legs/pedestals, cushions/rolled arms, panels/hardware, individual book spines/pages and hollow bowl/tub forms; it is not inherited box furniture hidden by textures.

Seven deck datums above baseline: **2.35 / 5.20 / 8.80 / 11.80 / 14.40 / 17.20 / 20.00 m**. The machinery working floor is separately at **1.60 m**, with engine galleries at 4.60/6.80 m. The bridge is high enough to contain the occupied cabins below; bridge-wing plates no longer duplicate the central structural deck. Fore/aft service routes, both after-orlop escapes and machinery access/return landings are explicit.

The plant uses nine single-ended Scotch boilers with after-facing furnace doors and connected steam/feed/flue headers, a graduated HP/IP/LP triple-expansion engine, separate crank/rods/crossheads/eccentric-link/spindle movers, surface condenser, hotwell, open-crosshead feed pumps, separately ported circulating pump, supported dynamo engine/generator assemblies and inboard-facing switchboards, tailshaft/thrust bearings/stern tube, pitched screw and stock/quadrant/steam steering. The latest revisions correct the condenser/pipe/stair arrangement, working-light supports and boiler firing-door flange clearances. Galley/bakery ranges now face reachable working aisles; the bakery entrance clears its range and preparation bench. Two small crew table/bench mess alcoves occupy existing berth-free bays without reducing berths. Internal boiler/valve/auxiliary details are simplified; the schematic is not a thermodynamic or pressure-vessel certification.

Engine bores **1.40 / 2.25 / 3.50 m**, stroke 1.80 m, crank radius 0.90 m, conrod length 3.00 m, nominal ahead 72 rpm; shaft z=3.00 m, propeller x=−78.00 m / diameter 5.30 m / pitch 9.40 m; rudder stock x=−79.50 m. The 19.295 kn result is `RPM × pitch × .88`, a **kinematic gameplay target**, not proven power, resistance, coal consumption or sea speed. Numerical displacement/hull coefficients are not a stability, load-line, strength or safety assessment.

## 4. Implemented Roblox contracts — live acceptance still required

* Regional imports normalize independently using four genuine calibration points. The waterline pivot maps `(x,y,z) → (−y,z−6.5,−x)` in **metres**, then scales once by `1/.28`. Final design envelope: **592.857 × 65.714 × 23.214 studs**.
* One anchored waterline root, welded passive geometry and Motor6D moving parts; visual furniture/rigging does not become detailed collision soup. Matched native doors/gangway colliders follow the same transformations.
* Boarding/gangway stow/travel and mooring interlocks; signed nine-order ahead/astern telegraph; independent regulator and firing controls; helm seat plus prompt fallbacks; generator, optional authorised whistle and local smoke/wake/instrument display.
* Exact slider-crank and eccentric-link transforms; signed shaft/propeller and matching rudder/quadrant; no cumulative integrated heave offset.
* Door prompts have server distance/rate/liveness/line-of-sight checks. Closing uses a conservative hinge-sweep avatar guard. Stationary doors stop sending redundant motor changes. Nearby players can use controls; production crew-role authorisation remains the experience owner's responsibility.
* Native seating, prototype standing-passenger carry, bounds-aware local furniture detail hiding and nearest-light budget (default 12, clamp 4–24, within 58 studs). These do **not** prove rendering/network/streaming performance.

Full instructions and unchecked live sheet: [ROBLOX_INSTALL_AND_TEST.md](ROBLOX_INSTALL_AND_TEST.md). The `.rbxmx` is an installer/control package, **not a pre-uploaded finished Roblox place**. Upload/review textures using your own authorised account/group. Disable old controllers for this imported ship.

## 5. Evidence and verification

### Headless results

* Static geometry/interface/circulation suite: **20 PASS / 3 INFO / 1 UNVERIFIED**. All inventoried door approaches, multideck component links, 13 sampled stair flights, four engine ladders and nine machinery aisle anchors pass the documented simplified collider checks.
* Actual structural regression (auditor 1.2): **3 PASS / 0 FAIL**. Frames/floors/keelsons pass both the analytical envelope and the actual lower-shell ray tests; the stern shoe/post/rising keel contacts pass. The full-radius rotating disc clears the stern frame by a conservative 79.5 mm; the actual shell has a conservative **574 mm radial-separation bound** using 115 continuous axial intervals no wider than 10 mm, each with a 20 mm axial propeller guard. This is not stopped-pose sampling or a minimum Euclidean tip-distance/elastic/hydrodynamic certification. The actual-shell negative control correctly rejected the previous master with 778 frame and 406 floor/beam vertices outside the physical loft. See `STRUCTURE_GEOMETRY_AUDIT.json` and `inspection/STRUCTURE_REGRESSION_BASELINES.json`; this is not universal Boolean containment or a strength calculation.
* Main conrod geometry: 2,163 analytical poses, maximum pin-distance residual about `8.88e−16 m`.
* Official Khronos validation: **18 actual regional GLBs, 0 errors, 0 warnings, 290 informational messages**. Reports bind the results to the archive's exact GLB hashes.
* All **six Luau sources compile** with Luau 0.747. This is parsing/bytecode compilation, not Roblox type/engine/API certification.
* **30 exact-source runtime logic/transform tests pass** under a deliberately fake Roblox API, including interlocks, signed reversing, endpoint transforms, no made-fast height drift, prompt rejection and door-sweep logic. This does not simulate weld contacts, Humanoid physics, multiplayer, real line of sight, streaming or FPS.
* Archive checks verify all regional hashes, six exact current script sources inside the RBXMX, matching archive/manifests/install guide, original maps and own-change scope. See `DELIVERY_VALIDATION.json`.

The collider model assumes 0.20 m grid cells, 0.28 m avatar radius, 1.68 m height, open doors and discrete stair samples. Furniture proxy comparison allows up to 25 mm differences from lower tessellation (measured maximum 21.9 mm); other proxies/interfaces must match exactly. Finite positive bounding extents are not signed-volume proof. Closed glTF components and UV checks are not universal proof of outward normals, no accidental interpenetration or successful Studio ingestion.

### Independent exported component / normal / precision audit

The exact regional-file audit initially found **2,788 triangles with opposing averaged shading normals (12,647 individual opposing corners)** and **nine cap triangles made collinear by the 0.1 mm export compression grid**. These were corrected rather than waived because Khronos accepted the format. The exporter splits opposing shading corners before tangent construction, and retains exact original source-point float precision only where compression would collapse a cap triangle. It does not invent offsets or delete cap faces.

The **executed current build-12 re-audit** covers all **860 unique meshes / 2,166,940 unique triangles / 74,050 exact-coordinate connected components**. Results: **zero negative or near-zero net component volumes, zero opposing face/corner-normal flags, zero degenerate-area triangles, zero odd unpaired welded edges, zero inconsistent directed edge winding, and zero collapsed triangle edges**. The manifest records 13,484 corrected shading corners across placements and 57 source-precision retained vertices. Report identities bind this audit to the current manifests and exact regional files. See `COMPONENT_VOLUME_AUDIT.json` and `inspection/EXPORT_NORMAL_REVISION.json`.

Coincident contacts have more than two balanced edge uses; these are reported separately, not passed off as a two-manifold Boolean union or proof of no intersections. Signed net component volumes do not certify every local face, physical pressure boundary or ship strength. This audit does not replace Studio import review.

### Actual-model visual evidence — review in progress

The planned set is **51 major/technical views + 203 roof-off physical-space surveys**. Eye-level interiors and explicitly named technical cutaways are distinct. All come from the delivered Blender geometry using Cycles; OIDN processing and image hashes are registered. Major views use up to 12 adaptive samples and surveys up to six on the limited CPU host, with two diffuse/glossy bounces and a temporary 1K texture cache (the original delivered 2K maps are unchanged); soft fine detail, residual noise and denoising edge artefacts are disclosed. Raw PNGs and render tiles remain excluded scratch; the full-resolution processed JPGs are the retained evidence. No AI-generated concept, historical photograph or analytical SVG is passed off as an actual model or in-game screenshot.

The opened-file review list, reviewed exceptions and source hash are recorded incrementally in `VISUAL_REVIEW.json`; [EVIDENCE_INDEX.html](EVIDENCE_INDEX.html) is the embedded-thumbnail index, with full-resolution JPG paths on each card. `all_cameras.json` records cameras, true pixel dimensions, source/renderer identities and cutaway flags. Presence of a file alone is not visual acceptance.

## 6. Sources and cross-agent interfaces

Historical basis: period *Ocean Steamships* (1891) construction/engine evidence; September 1889 *Ocean* Teutonic interiors/electric-lighting account; museum comparative engine model; inherited liner photographs. **RMG 1880/1895 steam-launch sheets were not accessible as images and are not liner plans.** No exact historical Aurelian plan was found/traced. The vessel and revised machinery/arrangement are explicit project design choices. See [DESIGN_AND_SOURCES.md](DESIGN_AND_SOURCES.md) and [ATTRIBUTION.md](ATTRIBUTION.md).

Boat tip inspected: `6bd984e7d9a95459bc9c1032f58bd5210a9c1159`; port tip: `dbcc091fb20f4a3f53ab29b46a09055ca0e735f4`; QA tip: `f2237f8bea5e25d6153100b98558360b787012db`. This is a unilateral versioned handoff, not approval from Themistocles-II/Pericles-II or a joint Studio test.

Three ship-owned mount/cradle/davit interfaces: steam cutter SWL requirement **3,900 kg**, rowing cutter **2,100 kg**, whaler **1,700 kg**. Actual boat assets are not duplicated or modified. There is **not** a complete eleven-boat lifesaving inventory. Berth/depth envelopes fit nominal dimensions on paper, but the actual +4 m quay/gangway world fit, channel/turning/grounding and launch/hoist operations remain unverified.

## 7. Files and publishing

* Editable source: `models/leonidas_ii/Aurelian_1889.blend`, `blender/leonidas_ii/`, `shipdesign/leonidas_ii.py`.
* Import delivery: `exports/leonidas_ii/Aurelian_Roblox_Import_Kit.tar.xz`; standalone control sources/package in `roblox/leonidas_ii/`.
* Maps: `reference/leonidas_ii/materials/`; spatial data/manifests in `exports/leonidas_ii/`.
* Three editable analytical sheets plus vector PDF in `drawings/leonidas_ii/`; actual deck cutaways are separate model renders. Drawings are neither museum tracings nor certified construction sheets.
* Audit, inventories, source/attribution, static/format/runtime/delivery checks and installation sheet in `docs/leonidas_ii/`.

Branch **`agent/leonidas-ii`**, parent `75bf4ac5770b803919b36c8dbdb5374df82d88ac`. The exact local commit and publication outcome are recorded in the local `PUBLICATION.json` receipt / final handoff; this report cannot include its own commit's hash without a circular dependency.

**Publication status is recorded in the local receipt / final handoff, not inferred from this report.** The earlier anonymous dry-run lacked authentication. After renewed explicit authorization, a read-only authenticated repository write-permission check succeeded; that is not itself a push. The publisher requires the exact reviewed commit, strict evidence/review gates and a clean worktree before an ordinary fast-forward branch push. No force-push or other branch overwrite is authorized. The authorized credential is held transiently for the requested push, not saved in repository files, remote URLs or reports. Rotate the credential after use. The final push and remote exact-commit outcome must be read from the local publication receipt / final handoff. For a normal authenticated checkout, after verifying the branch/commit:

```bash
git switch agent/leonidas-ii
git log -1 --oneline
git push -u origin agent/leonidas-ii
```

If the remote has advanced, fetch and review; do not force-push. Only this agent's namespaced additions and the requested root entry points are in scope. The sandbox sparsely omits unchanged inherited binaries and caches redundant Git objects outside saved files to fit its size limit; their repository trees remain unchanged. `tools/restore_leonidas_checkout.py` can reconstruct the exact recorded local commit if that cache expires, without replacing working files or making any remote write.

## 8. Remaining acceptance work

1. **Finish/accept actual-image review** of every major area and all physical-space surveys; record issues, not only successful exits.
2. Import all regions in Studio, review PBR/UV/normal/glass fidelity and exact hierarchy, then run the supplied structural smoke test.
3. Walk every route/compartment and operate doors/gangways with the intended largest avatar. Pay attention to shallow headroom, gallery transitions and furniture clearances.
4. Test seated/standing/jumping passengers, boarding/disembarking and reversing machinery with two clients under latency. Carry is a prototype, not a certified solution.
5. Benchmark target-device client/server frame times, draw calls, memory, replication and streaming. The substantial whole-ship asset has **no proven performance target**.
6. Test real port/quay/world navigation collision and mooring/boat launch/hoist behavior; the controller is anchored-root kinematics, not hydrodynamic contact solving.
7. Resolve accommodation/dining/lifesaving shortfalls if the original capacity is mandatory, and obtain cross-agent approval. No stability/structural/pressure-vessel/safety certification is supplied.
8. Publish the reviewed local commit using secure GitHub write access. Until these open gates are accepted, describe this as a reviewable rebuild, **not a completed playable release**.
