# Operation Victoria — LEONIDAS-II

## SS *Aurelian* · 1889

A **new reconstruction of the project's fictional Atlantic express passenger/mail-and-cargo liner**, preserving its 166 m principal envelope and single-screw identity. This is not a reconstruction of an actual ship called Aurelian, nor a launch enlarged into a liner.

**Asset handoff: corrected model and individually reviewed evidence; not a Studio-certified playable release.** Geometry, furnishings, machinery, materials, import pipeline and runtime have been rebuilt. All **272 current final renders** have been individually inspected with exact source/file/native-pixel identity and explicit limitations. Actual-model evidence, measured counts and the remaining unverified live tests are distinguished in the delivery documentation; this is not the user's aesthetic sign-off.

### Current work: micro-detail correction and exhaustive visual recheck

**The user found floating tableware and further small defects after the earlier refinement.** The generator—not just the pictures—has been repaired again. Current matched MASTER/GAME sources clear all six canonical saved-source screen families: finite fittings/floor contacts, complete room parts, plant, exterior/decks/access, own-frame/furniture door sweeps and sampled shaft-bearing clearance. Both quality settings pass **344 positive/negative regressions**. The broader door screen caught 97 wardrobe-crown obstructions; later native-pixel review caught coplanar carom-rail corners and stair-riser ends that closed-component checks missed. All were repaired, not exempted. The final rebuild has a verified frozen-input receipt over the actual GAME export and **42/42 micro-delivery checks**. Geometry checks still do not complete the visual review.

**Final visual review: 272/272 current renders individually inspected.** The [self-contained offline HTML gallery](docs/leonidas_ii/EVIDENCE_INDEX.html) shows every final render with **short titles only, no captions**. All embedded native-dimension images were independently reproduced; offline desktop/mobile and restricted viewer-iframe controls were tested. Strict **delivered-package/evidence** preflight: **63 PASS / 0 FAIL / 1 UNVERIFIED**, including 52 isolated validator-mode/tamper regressions. This revalidates delivered bytes and the original frozen geometry/export records; it does **not** rerun Blender audits or claim a fresh read of excluded GAME rebuild scratch. [Exact observations and limitations](docs/leonidas_ii/FINAL_RENDER_REVIEW.json) include low-angle/underside views and actual reopenings of seven rejected/stale-camera replacements. Geometry screens never substitute for that review, hidden-joint/continuous-motion proof, Studio/live/FPS acceptance or the user's aesthetic approval.

**Publication:** the corrected handoff targets [`agent/leonidas-ii`](https://github.com/dreamer2664/victoria/tree/agent/leonidas-ii) as a normal fast-forward update. The independent local `PUBLICATION.json` receipt records the exact commit/tree and the outcome of authenticated push plus read-only remote-tip verification; a prepared commit alone is never described as a completed push. Publication is separate from Studio/live acceptance. The earlier published checkpoint below is historical, not acceptance of the corrected delivery.

The earlier published **256-image / 47 PASS / 1 UNVERIFIED** checkpoint at `6a9ee98`, the 25-view refinement subset and previous candidate diagnostics are history, not acceptance of this changed source. Original pre-correction room pixels, superseded reports/galleries, rejected V5 stair/carom pixels and V6 rejected hinge/upper-plan evidence are retained losslessly; see the [history guide and exact-hash indexes](docs/leonidas_ii/HISTORY.md). The current **272-view gallery** was rebuilt only after every fresh final was individually reviewed. The upper-plan replacements explicitly omit separate weather roofs while retaining every original furnished room; old roof-obstructed pixels were not relabelled.

### Earlier requested progress report

The **225-image interim snapshot** (all 203 surveys plus 22/51 major views) was pushed and remote-verified at `6938aeb31d708d3f11e77cd9d5408cb172ecaec2`. Its [detailed progress report with renders](docs/leonidas_ii/PROGRESS_REPORT.md), [self-contained HTML version](docs/leonidas_ii/PROGRESS_REPORT.html) and [snapshot register](docs/leonidas_ii/PROGRESS_SNAPSHOT.json) are preserved unchanged as the historical checkpoint. The 29 major views recorded as remaining there were subsequently reviewed for build 12. The changed master needs fresh evidence; use the current checkpoint above for its state.

### Start here

| Purpose | Deliverable |
|---|---|
| Inspection and preservation/rebuild decisions | [Previous-generation inspection](docs/leonidas_ii/PREVIOUS_GENERATION_INSPECTION.md) |
| Historical evidence, design choices, source limitations | [Design and sources](docs/leonidas_ii/DESIGN_AND_SOURCES.md) · [Attribution](docs/leonidas_ii/ATTRIBUTION.md) |
| Current delivery, evidence review and limitations | [Delivery report](docs/leonidas_ii/DELIVERY_REPORT.md) |
| Every final render, short titles only | [Open the self-contained HTML gallery](docs/leonidas_ii/EVIDENCE_INDEX.html) — 272 images, offline, no captions; click to enlarge |
| Exhaustive current-source visual review | [Exact final-render observations](docs/leonidas_ii/FINAL_RENDER_REVIEW.json) · [Gallery byte/UI validation](docs/leonidas_ii/RENDER_GALLERY_VALIDATION.json) |
| Editable original model | [`models/leonidas_ii/Aurelian_1889.blend`](models/leonidas_ii/Aurelian_1889.blend) — semantic collections, original packed maps |
| Standard regional Roblox geometry and controls | [`exports/leonidas_ii/Aurelian_Roblox_Import_Kit.tar.xz`](exports/leonidas_ii/Aurelian_Roblox_Import_Kit.tar.xz) — **extract before importing** |
| Installation, controls, required live test sheet | [Roblox install and test](docs/leonidas_ii/ROBLOX_INSTALL_AND_TEST.md) |
| Dimension/attachment contract | [`interfaces/leonidas_ii_ship.json`](interfaces/leonidas_ii_ship.json) · [`DIMENSION_MANIFEST.json`](DIMENSION_MANIFEST.json) |
| Arrangement, datums and machinery flow | [`drawings/leonidas_ii/`](drawings/leonidas_ii/) — editable SVG and vector PDF; analytical, not historical tracings |
| Actual geometry images and source identities | [`renders/leonidas_ii/`](renders/leonidas_ii/) — all 272 final JPGs and source/camera registers; every current final individually reviewed. No old image is relabelled with the corrected master/driver hash. |
| Source maps | [`reference/leonidas_ii/materials/`](reference/leonidas_ii/materials/) — six original 2048² maps |
| All new Roblox source | [`roblox/leonidas_ii/`](roblox/leonidas_ii/) — installer, runtime, generated data, client, server and Studio smoke test |

### Dimensions and accommodation

* **166.00 m LOA / 158.00 m LBP / 18.40 m moulded beam / 6.50 m design draught.** At 0.28 m/stud: 592.857 × 65.714 × 23.214 studs. Shell plating adds a small amount to outer beam.
* Source: metres, +X bow / +Y port / +Z up, baseline origin. Game export: **metres**, −Z bow / −X port / +Y up, waterline origin; `(x,y,z) → (−y,z−6.5,−x)`. Scale **once** using the genuine 10 m calibration markers.
* Seven deck datums, 203 separately inventoried physical spaces, 13 main stair flights and four engine-room ladders. A physical-space count is not a count of unique room designs or a safety certificate.
* **Built:** 628 passenger sleeping positions (228 first / 132 second / 268 third) plus 117 crew berths. First class includes **114 permanent beds + 114 modeled convertible settee berths**, not 228 permanent beds; settee conversion/live sleeping use is not implemented/accepted. The 900/196 planning targets and inherited 1,080/196 claim are **not achieved**. First-/second-class dining contain **96 / 48 actual chairs**, not the first-class 228-seat planning target. No invisible accommodation or seating is counted.
* Nine single-ended Scotch boilers and one triple-expansion plant: 1.40 / 2.25 / 3.50 m bores, 1.80 m stroke, signed 72 rpm nominal; 5.30 m pitched bronze screw. Approximately 19.3 kn is a kinematic gameplay target, **not** a resistance, indicated-power or sea-trial result.

### Rebuild and check

Requires Blender **4.2 LTS** (4.2.3 used) and external Python with NumPy, Pillow, SciPy, Matplotlib and zstandard (lossless native source-stream compaction); see [`blender/leonidas_ii/requirements.txt`](blender/leonidas_ii/requirements.txt). CairoSVG is optional for PDF conversion. Blender supplies its own Python/NumPy. Set `BLENDER_BIN` to your executable. The portable Linux build may require its `lib/` directory on `LD_LIBRARY_PATH`.

```bash
bash tools/build_leonidas_ii.sh
# Actual Cycles evidence, one Blender process at a time:
bash tools/render_leonidas_evidence.sh
# Editable analytical drawings (PDF additionally requires CairoSVG):
python3 tools/draw_leonidas_ii.py --pdf
# Optional checks, with their documented dependencies:
python3 tools/audit_leonidas_volumes.py
node --expose-gc tools/validate_leonidas_gltf.cjs
python3 tools/test_leonidas_runtime.py
# Revalidate the delivered frozen export/audits, not missing rebuild scratch:
python3 tools/check_leonidas_micro_delivery.py --delivered-package
python3 tools/test_leonidas_delivery_bindings.py
python3 tools/make_leonidas_review.py --sheets-only
# Internal filename/native-pixel inspection copies; this approves NOTHING:
python3 tools/prepare_leonidas_review_images.py
# Actually open/review EVERY final image and record exact observations first:
python3 tools/make_leonidas_render_gallery.py
python3 tools/test_leonidas_render_gallery.py
python3 tools/check_leonidas_delivery.py --require-evidence --require-reviewed
```

The gallery test additionally requires Python Playwright and its Chromium headless shell (`python3 -m playwright install chromium --only-shell`, plus platform libraries via `python3 -m playwright install-deps chromium`). It independently reproduces every native-dimension embedded encoding and checks offline desktop/mobile controls plus an opaque-origin iframe with only `sandbox="allow-scripts"`; this is UI/byte verification, never automatic model or visual approval. The delivered HTML itself needs no Python, browser extension, server or external resources.

**Delivered-package vs fresh saved-source verification:** this saved snapshot intentionally omits `build/` scratch, including the original GAME `.blend`/build-data pair. The full delivery checker explicitly revalidates the actual archive, retained MASTER and unchanged frozen actual-export/audit bindings, reports those absent scratch inputs, and still evaluates every canonical audit/result gate. It does not regenerate provenance or describe frozen identities as a fresh GAME file read. The standalone micro checker defaults to `--require-saved-sources` and **fails if those actual saved files are absent or changed**; after an actual ordered build, use that mode (or append `--require-saved-sources` to the full delivery command). The ordered build enforces it automatically. The exact earlier missing-scratch failure and validator are [archived](docs/leonidas_ii/inspection/DELIVERY_REVALIDATION_SCRATCH_V6.json); 52 isolated binding regressions test this distinction without editing original assets.

The default serial render batch includes the two additional crew-mess close-ups after the planned set. `blender/leonidas_ii/render_crew_details.py` reuses the unchanged common renderer, separately hashes its own camera/visibility driver, and explicitly omits room walls/roof for these diagnostics; it does not change ship geometry. Run only `LII_GROUPS=crew_details bash tools/render_leonidas_evidence.sh` to reproduce those details after the full-resolution public views are available.

`tools/build_leonidas_ii.sh` orders the master build, lossless source compaction, actual-shell/stern structural and fixture/rigging audits, lower-tessellation GAME build, packed map preparation, all six both-quality canonical micro audit families, separate actual saved-stair side/correspondence screens, a frozen-input receipt across the actual GLB exporter run, regional kit, exact exported component/normal audit and static validation. `build/` directories are regenerable scratch, not delivery dependencies; regenerate excluded GAME scratch before fresh saved-source audit checks. **Do not rerun `tools/leonidas_revision_fixes.py` or any of the nine `tools/leonidas_micro_corrections/fix_micro_parts*.py` scripts: these non-idempotent migrations have already been applied. Preserve subsequent direct source edits.**

The independent component audit restores missing regional GLB scratch files directly from the hash-verified delivered archive; it does not need to rebuild or change the editable master to re-check a delivery.

The import kit uses solid XZ compression to avoid redundant embedded images. Extract with `tar -xJf Aurelian_Roblox_Import_Kit.tar.xz`, 7-Zip, or a compatible archive utility. Its contents are normal glTF 2.0 GLBs and an `.rbxmx` control package; no Draco decoder, invented Roblox asset IDs or external texture CDN is required. Textures may need your authorised Studio uploads.

### Integration and acceptance boundary

Implemented contracts include boarding/gangway and mooring interlocks, signed ahead/astern orders, separate firing/regulator controls, helm, articulated crank/rods/shaft/propeller, rudder/quadrant, doors, seating and locally budgeted lighting/effects. **They have not been accepted in Roblox Studio.** There is no measured client FPS, multiplayer passenger-carry validation, continuous Humanoid collision test or hydrodynamic navigation-collision solver. Follow the unchecked live test sheet before using this in a published experience.

Boat/port work was inspected at the recorded branch tips; only ship-owned host interfaces are supplied. Three compatible craft sockets do not establish the inherited eleven-boat lifesaving inventory. No other agent's asset is changed and no joint world-fit approval is claimed.

### Provenance and branch

Branch **`agent/leonidas-ii`**, based on `75bf4ac5770b803919b36c8dbdb5374df82d88ac` from `agent/ship`. New work is namespaced in the repository's existing directory structure; there is no `projects/` tree. Root README and the dimension entry point now point to LEONIDAS-II. Original generators, models, renders, interfaces and runtime sources remain in Git as provenance, **not** the intended install path. The [inherited README](docs/leonidas_ii/inspection/INHERITED_README.md) and the inherited dimension manifest inside the [indexed history archive](docs/leonidas_ii/inspection/MICRO_INTERMEDIATE_HISTORY_INDEX.json) preserve their original claims verbatim.

The sandbox sparsely omits unchanged inherited binaries and six superseded inspection JSONs independently verified against both their lossless archive and published Git blobs. Redundant Git metadata lives in excluded cache to fit the saved-file budget; no omitted asset is deleted from the branch. A normal clone can use `git sparse-checkout disable`. Only if this sandbox's cache expires, run `python3 tools/restore_leonidas_checkout.py`: it fetches the exact recorded published commit read-only, or reconstructs an unpublished exact tree/commit from retained files and its recorded parent. Recovery uses index-only operations, never checkout/reset/clean over working files; unknown missing deliverables fail closed. It never pushes or stores credentials.
