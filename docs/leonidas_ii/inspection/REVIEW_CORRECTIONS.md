# Corrections found during actual-image / independent export review

These are reconstruction revisions, not claims of Roblox Studio acceptance. Superseded images are excluded scratch and do not count as current-source evidence.

## Exported shading and cap precision

The independent regional-GLB audit found 2,788 triangles whose averaged smooth normal opposed their face (12,647 individual opposing corners), despite balanced directed edge winding and positive net component volumes. Nine cross-section cap triangles also became collinear on the 0.1 mm compression grid. See `EXPORT_NORMAL_REVISION.json` for the before identities/counts.

`export_game.py` now splits offending shading corners before tangent reconstruction, and retains exact source-point float precision where compression would collapse a triangle. It does not invent offsets, delete cap faces, or change authored shape/UVs/winding/triangle totals. An executed export-only refresh returned zero findings in all independent gated categories and zero Khronos errors/warnings. Subsequent interior rebuilds repeat these checks against new exact regional hashes.

Coincident touching solids can yield >2 balanced uses of a welded edge. These are reported, not passed off as a two-manifold Boolean union or a universal no-intersection proof.

## Crew accommodation camera

A full-resolution eye-level crew image was opened and rejected: its camera was inside an outer bunk. `render.py` now chooses a plausible standing photographic vantage using actual fixture bounds and rotated native collision boxes. Narrow dormitory images look down the real central aisle. A low-resolution actual-model probe was opened and showed bunks and a continuous aisle rather than a mattress interior. This probe is not a replacement for final full-resolution inspection.

## Galley/bakery firing fronts

The galley camera probe exposed a substantive arrangement error: the stove fronts faced the close bulkhead, not the work aisle. Both ranges are now rotated to face the aisle. The bakery entrance is moved to its clear forward end, preserving the room envelope and adding a usable bread-preparation bench. The static suite now explicitly checks range orientation and connected firing positions, rather than relying only on room/door labels.

An intermediate rebuild correctly failed because the bakery doorway remained obstructed after the first rotation. It was not accepted or published.

## Small crew mess alcoves

The two narrow lower crew mess-and-berth rooms had no mess table. Each now has a two-seat table/bench alcove in the existing berth-free entrance bay, against the wall opposite the door and outside the longitudinal centre aisle. No berths are removed or invisibly added. Native seating increases by four bench seats; the existing chair count is unchanged.

The first table placement failed the actual furniture-pair overlap gate and was moved to the gap between adjacent berths. A second intermediate rebuild then caught a 0.51 mm master/GAME seat-datum difference caused by using tessellation-dependent bounding boxes. Placement now uses exact common berth centres; actual fixture-envelope/pair tests remain separate. Exact contract comparison is retained, not relaxed.

## Music-room evidence

The former generic lounge view framed only a fragment of the pianoforte. A dedicated, collision-checked view is now aimed at its keyboard side; the separate roof-off room survey must still be inspected.

## Machinery photographic visibility

Opening raw engineering images exposed a renderer-only evidence defect: boiler working-aisle shots omitted the tank top/overhead decks, and the shaft-alley filter omitted its tank-top floor. These images were rejected as intact-room evidence. The working-view filters now retain those actual structural meshes, plus the auxiliary bay bulkheads/framing. Deliberate isolated engine/gear/stern views remain explicitly labelled cutaways. No geometry was moved/hidden to disguise a model defect; the discarded images do not count as final evidence.

## Physical stern-frame continuity and actual-shell containment

The build-10 stern close-up was rejected: the flat shoe's forward end did not contact the rising keel, and internal structural fins protruded below the physical bilge. The shoe now connects the after post to a rising arm and forward keel; the fore post is split around the stern tube. A mesh-component contact graph checks the actual contacts within 2 mm. A separate triangle/slab audit checks the complete rotating propeller disc, rather than just the blades at one stopped angle.

The first correction (build 11) passed an ideal mathematical hull-envelope test, yet the opened image still showed fins. An actual-object identity-colour diagnostic identified the rolled frames: the ideal curve did not represent the coarse physical shell's bilge chords. This was a real geometry defect, not a reason to hide structure in the renderer.

The replacement builder samples the actual shell triangles using BVH side/bottom rays. Floors, beams and keelsons use sampled actual clearances; frame segments use 34 heights and a 65 mm inward profile offset, breaking where no physical shell hit exists. Auditor 1.1 adds lower-shell side-ray tests below z=6 m (the opening-free band), alongside the analytical-envelope, contact and screw-sweep tests. Running that auditor on the saved build-11 master correctly **failed** with **778 frame vertices and 406 floor/beam vertices outside the actual lower shell**, despite zero analytical-envelope violations. Both rejected-build negative controls are preserved in `STRUCTURE_REGRESSION_BASELINES.json`.

The executed build-12 master passes all three current structural gates: zero sampled violations; minimum actual lateral margins approximately **55.5 mm frames / 60.7 mm floors-and-beams / 158.2 mm keelsons**; connected stern shoe/post/rising keel; about **79.5 mm** full-disc clearance from the stern frame. Both the low-resolution probe and the opened final full-resolution stern JPG no longer show the fins.

Auditor **1.2** also checks the actual counter shell, not just the frame. It clips real shell and pitched-propeller triangles into **115 continuous axial intervals no wider than 10 mm**, expanding each propeller interval by 20 mm at both ends. A convex clipped propeller polygon's maximum radius is bounded by its vertices; the minimum projected shell radius is measured over the clipped polygon. Independent interval minima/maxima conservatively cover continuous rotation rather than a finite set of stopped blade poses. The executed master has a minimum **574 mm radial-separation bound** by this method. This is not a minimum Euclidean tip-distance, hydrodynamic or elastic-clearance certification. A separate read-only GAME probe agreed within export precision. No geometry change or export substitution was used for this additional check.

These vertex/ray/contact/envelope tests are **not** a universal Boolean-containment, hidden-intersection, scantling or strength proof. Full-resolution review is separately recorded in `VISUAL_REVIEW.json`.

## Auxiliary plant and purpose-specific service spaces

Close-range review also triggered modeled auxiliary improvements: supported dynamo engine/generator assemblies with exposed winding/commutator fittings and inboard-facing switchboards; open-crosshead feed pumps; separately ported circulation/hotwell fittings; and additional engine/boiler supports and connection detail. Generic service-room fitting placement was replaced by purpose-specific chart/navigation, mail sorting, drinks/ice storage, cargo, medical and barber arrangements. Bath/bridge cameras were corrected and the skeleton view gained explicitly diagnostic underbody fill. The build-11/12 composition probes were opened; they are not counted as full-resolution evidence or as Roblox mechanical/access acceptance.

## Complete current-source image-review follow-up

The final build-12 JPG set has now been opened: **51 planned major views individually + all 203 room surveys on 34 native-grid pages + two supplementary crew details individually**. All three analytical SVGs are separately reviewed. `VISUAL_REVIEW.json` records exact image/source/renderer identities, view-specific observations and limitations, with **zero unresolved image-revision blockers**. The master and GAME/import archive are unchanged by this follow-up.

* **Crew camera:** the final enclosed 1600×1000 view is visibly in the standing aisle, not inside a berth. Both berth levels and the ceiling/aisle are legible. It still does not prove live lower-berth/headroom clearance.
* **Cooking fronts:** final galley/bakery images expose their aisle-facing range fronts; static orientation/approach checks are also current. Operational, fire and avatar acceptance remain open.
* **Crew benches:** initial close overhead details were individually opened but still showed only a thin sliver of bench; they were rejected and replaced, not signed off. Final close oblique details for both rooms explicitly omit the joined wall/ceiling objects while retaining the actual floor, all furniture and adjacent bunks. These show the bench top, four splayed leg/floor contacts and separate table pedestals/base. They are diagnostic cutaways viewed from outside the omitted wall, not photographic eye positions in an intact room. Two modeled positions per bench do not establish actual avatar sitting/knee room or comfortable simultaneous use.
* **Music/public rooms:** final keyboard-side pianoforte and all seven other public compositions were opened at full resolution. Repeated room/furniture families, dense dining rows, cropped near edges/stair destinations and denoising softness are recorded, not hidden by a blanket quality claim.

`blender/leonidas_ii/render_crew_details.py` separately records its driver hash while preserving the common renderer's existing identity. The serial render pipeline reproduces these additional details after the normal set. Strict checks refuse missing/stale detail pixels, wrong driver hashes or missing manual detail reviews. A pre-completion negative control rejected five incomplete evidence/review/blocker gates; the final executed strict result is **47 PASS / 1 UNVERIFIED / 0 FAIL**. The unverified gate is Roblox Studio/live/FPS acceptance.

## Acceptance

Do not interpret completed image coverage or this correction log as universal geometry, hidden-contact or gameplay approval. Read the current `STATIC_VALIDATION.json`, `COMPONENT_VOLUME_AUDIT.json`, `DELIVERY_VALIDATION.json` and `VISUAL_REVIEW.json`. Failed intermediate builds and low-resolution probes do not count as delivered evidence.
