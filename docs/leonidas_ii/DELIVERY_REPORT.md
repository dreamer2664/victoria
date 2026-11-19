# SS Aurelian · corrected model and exhaustively reviewed render handoff

**Current status: corrected editable MASTER and corresponding GAME/import kit rebuilt; all 272 current final renders individually inspected with limitations; requested title-only offline HTML built and tested. Strict delivered-package/evidence gates: 63 PASS / 0 FAIL / 1 UNVERIFIED.** This is not a Roblox Studio-certified playable release, universal hidden-contact certification or the user's aesthetic sign-off. Publication is recorded independently: the local receipt contains the exact prepared commit and the outcome of push plus read-only remote-tip verification.

## 1. What was corrected

The user identified floating plates and many small defects after the earlier refinement. We reopened the actual images, traced candidates into finite primitives and saved meshes, repaired the generators, then expanded the independent checks rather than trusting the old PASS reports.

* Tableware, individual cup/saucer/runner heights, stacked pantry crockery, tray contents, paper/ink, chessmen and other small surface-mounted accessories now use their real supporting surfaces.
* Furniture support includes bed slats, table/chair joints and outer soles, a three-foot piano stool with raised hub, piano soundboard/tail-leg/hinge/prop/pedal supports and actual curved caster bearings. Hospital-screen rings, the trolley, service fittings, locker hardware and bracketed accessories were also repaired.
* Finished floor layers are flush, preserve true stair/plant wells and do not hide millimetre bearing errors. Stair-hall column feet and capitals have separate saved-surface probes. Saved/generated polygon comparison retains a 0.1 mm grid and explicitly reproduces float32/local-origin storage rather than enlarging the tolerance.
* Door tests now include their own jambs **and actual furniture**, in both signed directions. The wider check exposed 97 wardrobe-crown obstructions; the cabinets and finite hinge/strap geometry were corrected, not exempted. The final screen samples 196 doors at 9,212 poses in each quality.
* Plant/exterior primitive graphs are matched to the saved geometry. Shaft carriers, bored flanges/shoes, thrust collars and coupling positions were repaired and separately sampled for moving clearance.
* **The subsequent native-pixel review found two more defects that valid closed components had missed:** crossed carom-table rails made false black corner pockets, and full-width stair riser ends produced black coplanar side slits. The rails are now one closed, shared-vertex mitred annulus; risers are housed inside the skirts and under the nosings. Convex exposed-plane tests cover the actual authored rail/stairs, with restored-old-geometry negative controls. Both quality settings now pass 344 regressions.
* Diagnostic cameras were also rejected during pixel inspection: one was inside a washstand, two looked between the real hinges and one cropped a trolley wheel. A subsequent native-frame opening caught a further open-pose problem: the swung leaf blocked the closed-pose eye. The rejected original pixels/driver/register/review are archived. A fresh opposite-side view now passes three actual-mesh knuckle sightlines and was individually reopened, showing all three knuckles and the swung strap. All four shared-driver replacements were freshly rendered/denoised/reopened. The widened target bunk includes its feet/posts in the checked native frame; the trolley retains all four tyres in frame, while its far caster neck remains visually occluded. These are evidence-camera corrections, not assumed model defects; old pixels are never assigned a new camera/source identity.

* **The exhaustive deck-plan pass found three more evidence failures:** the normal ceiling filter still left weather roofs hiding the hospital, two cabin ranges, chart room and entire wheelhouse. Those originals were rejected and archived. Fresh actual-source roof-off replacements now omit the explicit separate roof objects while retaining all **18 promenade / 25 boat-deck / 1 bridge** furnished rooms; each replacement has a separately hashed visibility driver. This changes evidence visibility only, not the delivered MASTER/common renderer or any ship geometry.

Earlier room-specific layouts, period materials, supported lighting, rigging chainplates and five exterior ladder assemblies are retained. Principal hull, machinery, capacity, scale and boat-interface contracts have not changed. No generated concept imagery substitutes for model geometry.

## 2. Exact current assets

Editable MASTER SHA-256:

`05fcdf10d429f83bd5e671b27e026d5c577e90a6e44f20c26750e9e3e069a526`

| Item | Measured result |
|---|---:|
| MASTER mesh objects / triangles | 1,437 / 4,341,224 |
| Inventoried physical spaces | 203 |
| GAME visual nodes, excluding calibration | 1,461 |
| Unique GAME meshes / reused placements | 1,160 / 301 |
| GAME placed / unique triangles | 3,199,238 / 3,101,586 |
| Maximum triangles per visual node | 18,000 |
| Calibration nodes | 4 |
| Complementary regional GLBs | 24 |
| Collision proxies / doors / moving assemblies | 4,040 / 196 / 20 |
| Seat records / modeled light positions | 201 plus helm VehicleSeat / 485 |
| Main stair flights / engine ladders | 13 / 4 |
| Compacted editable source | 23,514,427 bytes |
| Regenerable full GAME GLB | 318,706,340 bytes |
| Delivered compressed import kit | 26,721,984 bytes |

Import archive SHA-256: `0e43cb09d8d4bcbc3f400765f3c1ecc3c33bd7ec60e710b63483bc0ef31aa29f`.

The MASTER was losslessly recompressed: all **231,304,620 decompressed bytes** were hash-compared before replacement; no mesh, map or data was removed. The kit contains normal glTF 2.0 regional GLBs and the exact six-source RBXMX control package. Its solid XZ compression reuses embedded-image redundancy, not a Draco/decimated replacement. Original 2048² maps remain editable; regional maps use the documented 1024² mip level.

## 3. Executed checks on this exact generation

| Scope | Executed result | Limit |
|---|---|---|
| Finite fittings and actual saved-floor contacts, MASTER and GAME | 83 recipes each; zero detached clusters, floating/support flags | Finite surface/graph/ray screen at 0.6 mm, not every hidden joint or load rating |
| Complete room-part correspondence/contact, both qualities | 195 rooms / 41,425 parts each; zero detached/saved-mismatch flags; 12 column feet/capitals pass | Non-plant room meshes, not continuous avatar access |
| Plant-part correspondence/contact, both qualities | 45 static assemblies / 5,295 parts and 18 moving assemblies; zero scoped flags | Rigid-part graphs, not pressure/strength/thermodynamics |
| Exterior/deck/access correspondence/contact, both qualities | 80 static assemblies / 33,247 parts and 3 moving assemblies; zero scoped flags | Not universal rigging clearance or operability |
| Broad signed door sweeps, both qualities | 196 doors / 9,212 sampled poses / zero intersections each | 2° discrete poses; own jambs and room furniture included, not continuous or adjacent-space/avatar certification |
| Shaft/bearing clearance, both qualities | 2 pairs / 48 poses / zero intersections or saved mismatch; 4/4 negative controls | Sampled finite meshes, not continuous dynamics |
| Positive/negative generator regressions | **344 PASS / 0 FAIL in each quality** | Includes actual-template alterations and exposed-plane controls; not assembled-ship visual approval |
| Independent actual saved stair joinery, both qualities | 13 stairs / 26 exposed sides each; zero saved mismatch or positive-area coplanar overlap; restored old riser negative detected | Actual saved polygons at the existing 0.1 mm correspondence grid; not all-surface/hidden-joint or strength/walking proof |
| Source/detail and structural checks | 7 detail gates and 3 structural gates pass | Scoped actual contacts/rays/analytical envelopes; not seaworthiness |
| Frozen actual export provenance | Verified | MASTER/GAME/build-data/exporter/generator/12 canonical audit identities frozen before the real exporter, checked unchanged afterward; receipt included in kit |
| Independent exact exported component audit | 1,160 unique meshes / 3,101,586 triangles / 110,629 components; all eight blocking categories zero | No negative/near-zero volume, normal disagreement, degenerate area, odd unpaired edges, inconsistent winding or collapsed edges; not a union/no-intersection proof |
| Full source/current-export static checks | 20 PASS / 3 INFO / 1 UNVERIFIED | Simplified collision grids, open-door routes and sampled stair envelopes, not Humanoid physics |
| Official Khronos format validation | 24 regional GLBs; 0 errors / 0 warnings / 294 infos | Actual archived GLB hashes, not Studio upload or appearance |
| Luau compilation and exact-source mock runtime | 6/6 compile; 30 logic/transform tests pass | Fake Roblox API, not engine/network/physics/LOS/FPS acceptance |
| Micro-delivery byte/provenance checks | 42 PASS / 0 FAIL | All 12 original canonical audit files/results and current generator keys, retained source bytes, unchanged frozen actual-export receipt and matching kit; absent excluded GAME scratch is explicitly receipt-bound, not freshly read |
| Validator mode/tamper regressions | 52 PASS / 0 FAIL | Isolated copied-metadata and explicitly synthetic saved-byte fixtures; tests missing/changed inputs, audit/result/identity tampering and mandatory strict-mode failures. Not a geometry or actual-archive validation. Original assets remain unchanged. |
| **Strict delivered-package/evidence preflight** | **63 PASS / 0 FAIL / 1 UNVERIFIED** | Actual archive/source/driver identity, unchanged frozen audit/export bindings, explicit roof-off upper plans, all 272 actual individual observations, exact embedded native-dimension encodings and offline desktop/mobile/restricted-iframe UI pass. No Blender geometry audit is rerun here; the remaining live acceptance boundary is Studio/Humanoid/network/FPS. |

Reports are the canonical `*_MASTER.json` / `*_GAME.json` families, regression records in `inspection/`, [EXPORT_INPUT_IDENTITY.json](EXPORT_INPUT_IDENTITY.json), [MICRO_DELIVERY_VALIDATION.json](MICRO_DELIVERY_VALIDATION.json), [DELIVERY_BINDING_TESTS.json](DELIVERY_BINDING_TESTS.json), [COMPONENT_VOLUME_AUDIT.json](COMPONENT_VOLUME_AUDIT.json), [GLTF_VALIDATION.json](GLTF_VALIDATION.json), [STATIC_VALIDATION.json](STATIC_VALIDATION.json), [RUNTIME_LOGIC_TESTS.json](RUNTIME_LOGIC_TESTS.json) and [DELIVERY_VALIDATION.json](DELIVERY_VALIDATION.json).

**Revalidation scope after snapshot resume:** excluded `build/` scratch, including the original saved GAME `.blend`/data pair, is not retained. The original fresh-input checker therefore reported two missing-input failures; the exact validator/failure reports are [preserved](inspection/DELIVERY_REVALIDATION_SCRATCH_V6.json). No canonical geometry audit, model, image, frozen actual-export receipt or import archive was rewritten to remove those failures. Delivery checking now explicitly uses `--delivered-package`: actual delivered archive contents/receipt and retained MASTER/data/exporter bytes must match, all twelve original audit hashes and their full generator/source/result gates remain mandatory, and missing GAME scratch is plainly recorded as frozen-identity-only. This is not a fresh GAME geometry audit or saved-file read. The standalone micro checker still defaults to `--require-saved-sources` and fails on missing or changed saved GAME inputs; the actual ordered build enforces that strict mode after packaging. Use the same flag on the full delivery checker when fresh saved-source bytes are required.

## 4. Completed individual visual handoff and limits

The current complete target is **272 actual-model final renders**: 51 major views, 203 roof-off room surveys, 2 crew-mess cutaways, 7 exterior/wheelhouse details and 9 micro-contact details. Enclosed photographs, wall/roof-removed diagnostics and analytical drawings remain explicitly distinguished by short view titles and separate metadata.

**Every one of the 272 current final JPGs has now been individually inspected after this rebuild.** Observations cover all 203 room surveys, 51 major views, 2 crew-mess cutaways, 7 exterior/wheelhouse details and 9 micro-contact details. All seven rejected/stale-driver replacements were freshly rendered, denoised and individually reopened: three roof-off upper-deck plans plus the bunk, closed/open hinge and trolley. There are **272 current filename/native-body identity associations and zero unresolved visual blockers** in the declared visible-image scope; no rejected/stale record is counted as accepted. The black carom corners and stair-end slits are absent in the relevant current public-room pixels. Tiny, dark, cropped, roof-removed and occluded contacts remain explicitly limited, not declared proved. [FINAL_RENDER_REVIEW.json](FINAL_RENDER_REVIEW.json) records exact file/source/renderer identities and actual visible observations. No earlier V5 approval is transferred merely because some objects did not change. [VISUAL_REVIEW.json](VISUAL_REVIEW.json) is the compatible major/survey/supplementary subset; image generation alone cannot fill it.

The requested [final HTML gallery](EVIDENCE_INDEX.html) is **self-contained and offline, shows every final render, and contains only short view titles—no captions**. Native-dimension WebP display copies are conventionally encoded from the exact unlabelled final JPGs; original JPGs and camera/source metadata remain separate. The temporary 58px filename/hash strips used to disambiguate inspection are never gallery content. Its builder refuses stale/unregistered/missing pixels, changed driver hashes or incomplete exact-image/native-body review coverage.

All **272 embedded encodings** were independently reproduced from the originals. With networking offline, Chromium tests passed at **1440×1000 and 390×844**: responsive layout/no horizontal overflow, native image decoding, modal/next/previous, keyboard wraparound, Escape/focus return and 44px controls. A separate **390×844 opaque-origin iframe with only `sandbox="allow-scripts"`** also passed image decoding, layout, modal/next/close and focus checks, without same-origin, modal or network privileges. Desktop, mobile and restricted-iframe screenshots were additionally opened for layout inspection. [RENDER_GALLERY.json](RENDER_GALLERY.json) and [RENDER_GALLERY_VALIDATION.json](RENDER_GALLERY_VALIDATION.json) bind the exact HTML, builder/tester and final-review identities. These are UI/byte tests, not automatic model approval.

Current renderer SHA-256: `854dd554b781839204ffeefa9401434282449a3803c0331381a79c0b7d81b781`. Cycles uses the actual model with registered practical-light positions plus photographic fill, bounded CPU samples and a temporary 1K texture cache. Conventional tiled OIDN/JPEG processing is recorded. This is visible-image review, not hidden-joint, historical-photo, gameplay or user aesthetic certification.

Three regenerated analytical SVGs have separately been inspected through exact native rasterisations. All three delivered one-page PDFs have now also been individually opened through direct PDFium page rasterisations; their file/page/raster identities and observations are separate entries in the manual registers, not part of the 272 model JPGs. They show arrangement, datums/calibration and connected plant flow; dense arrangement labels require vector zoom and these drawings do not prove physical contacts, safety or thermodynamics.

## 5. Preserved contracts and unverified live work

* Fictional 1889 British Atlantic passenger/mail/cargo liner: **166 m LOA / 158 m LBP / 18.4 m moulded beam / 6.5 m draft**; nine boilers, two funnels, three pole masts, one screw. Not a literal reconstruction of an actual Aurelian/Teutonic.
* Scale **0.28 m/stud**. Native source +X bow / +Y port / +Z baseline becomes GLB metres `(-y, z−6.5, -x)`, Y-up, waterline origin. Scale once using the four genuine 10 m markers.
* **628 passenger sleeping positions:** 228 first / 132 second / 268 third, plus 117 crew berths. First class is **114 permanent beds + 114 modeled convertible settee positions**; live conversion/sleeping is unimplemented. Dining has 96 / 48 actual chairs. Earlier 900/196 planning targets are not achieved.
* Engine bores 1.4 / 2.25 / 3.5 m, 1.8 m stroke. Signed 72 rpm and about 19.3 kn are gameplay kinematics, not proven power, resistance, coal use or sea speed. No stability, pressure-vessel, scantling, load or seaworthiness certification.
* Three host craft sockets are unchanged; boat/port assets are untouched. A unilateral interface handoff is not a complete lifesaving inventory or joint quay/channel/gangway/launch/hoist world-fit acceptance.
* Installer/runtime controls include calibration, anchoring/movers, signed orders, interlocks, doors, helm, seats, prototype standing carry and local detail/light budgets. **Studio import, continuous Humanoid access, replication/carry/security, real prompt LOS, streaming and measured client FPS remain UNVERIFIED.** Use [ROBLOX_INSTALL_AND_TEST.md](ROBLOX_INSTALL_AND_TEST.md) before a published experience.

## 6. Files, history and publication

* Editable source: `models/leonidas_ii/Aurelian_1889.blend`; generators: `blender/leonidas_ii/`.
* Matching import kit: `exports/leonidas_ii/Aurelian_Roblox_Import_Kit.tar.xz` — extract before importing. Six Luau sources and insertable `.rbxmx`: `roblox/leonidas_ii/`.
* Main visual handoff: [all-render title-only HTML gallery](EVIDENCE_INDEX.html); exact individual observations/limitations: [FINAL_RENDER_REVIEW.json](FINAL_RENDER_REVIEW.json). Three SVG and three delivered PDF pages were separately reviewed, outside the 272 model JPGs.
* Lossless histories: [history guide](HISTORY.md). The old 25-view review/critical inventory and their exact claims remain archived, never relabelled as this source.
* Rebuild serially: `bash tools/build_leonidas_ii.sh`, followed by the official/runtime checks, render batches, individual review, gallery builder and strict delivery gate described in the README. **Do not rerun the one-off revision or nine micro-migration patchers; preserve subsequent direct source repairs.** Excluded `build/` scratch must be regenerated for fresh GAME saved-source audits.

Branch **`agent/leonidas-ii`**; the earlier published checkpoint **`6a9ee980fc9876b691dbb1f7535b61f619b181ed`** is historical. The corrected handoff passes the strict delivered-package/visual-file gates described above. Publication is a separate normal fast-forward operation, followed by read-only comparison of the remote branch tip with the exact local commit. The ignored local `PUBLICATION.json` receipt records that commit/tree and verification outcome independently of this non-self-referential report; the exact old publication receipt remains preserved in history. No force-push, unrelated asset change or Studio/live acceptance is implied by publication.
