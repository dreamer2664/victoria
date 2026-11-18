# Operation Victoria — LEONIDAS-II

## SS *Aurelian* · 1889

A **new reconstruction of the project's fictional Atlantic express passenger/mail-and-cargo liner**, preserving its 166 m principal envelope and single-screw identity. This is not a reconstruction of an actual ship called Aurelian, nor a launch enlarged into a liner.

**Release status: review candidate, not a Studio-certified playable release.** Geometry, furnishings, machinery, materials, import pipeline and runtime have been rebuilt. Actual-model evidence, measured counts, open issues and the unverified live tests are distinguished in the delivery documentation. A successful generator or exterior render alone is not acceptance.

### Immediate progress report

**Interim snapshot: 225/254 planned images reviewed — all 203 room surveys plus 22/51 major views.** The remaining 29 major views and Studio/live acceptance are still open. Read the [detailed progress report with renders](docs/leonidas_ii/PROGRESS_REPORT.md), or open its [self-contained illustrated HTML version](docs/leonidas_ii/PROGRESS_REPORT.html). This is a progress publication, not a declaration that the complete brief has passed.

### Start here

| Purpose | Deliverable |
|---|---|
| Inspection and preservation/rebuild decisions | [Previous-generation inspection](docs/leonidas_ii/PREVIOUS_GENERATION_INSPECTION.md) |
| Historical evidence, design choices, source limitations | [Design and sources](docs/leonidas_ii/DESIGN_AND_SOURCES.md) · [Attribution](docs/leonidas_ii/ATTRIBUTION.md) |
| Current delivery, evidence review and limitations | [Delivery report](docs/leonidas_ii/DELIVERY_REPORT.md) |
| Editable original model | [`models/leonidas_ii/Aurelian_1889.blend`](models/leonidas_ii/Aurelian_1889.blend) — semantic collections, original packed maps |
| Standard regional Roblox geometry and controls | [`exports/leonidas_ii/Aurelian_Roblox_Import_Kit.tar.xz`](exports/leonidas_ii/Aurelian_Roblox_Import_Kit.tar.xz) — **extract before importing** |
| Installation, controls, required live test sheet | [Roblox install and test](docs/leonidas_ii/ROBLOX_INSTALL_AND_TEST.md) |
| Dimension/attachment contract | [`interfaces/leonidas_ii_ship.json`](interfaces/leonidas_ii_ship.json) · [`DIMENSION_MANIFEST.json`](DIMENSION_MANIFEST.json) |
| Arrangement, datums and machinery flow | [`drawings/leonidas_ii/`](drawings/leonidas_ii/) — editable SVG and vector PDF; analytical, not historical tracings |
| Actual geometry images | [Embedded evidence index](docs/leonidas_ii/EVIDENCE_INDEX.html) · [`renders/leonidas_ii/`](renders/leonidas_ii/) — full-resolution exterior, interiors, engineering, deck cutaways, room surveys and camera register |
| Source maps | [`reference/leonidas_ii/materials/`](reference/leonidas_ii/materials/) — six original 2048² maps |
| All new Roblox source | [`roblox/leonidas_ii/`](roblox/leonidas_ii/) — installer, runtime, generated data, client, server and Studio smoke test |

### Dimensions and accommodation

* **166.00 m LOA / 158.00 m LBP / 18.40 m moulded beam / 6.50 m design draught.** At 0.28 m/stud: 592.857 × 65.714 × 23.214 studs. Shell plating adds a small amount to outer beam.
* Source: metres, +X bow / +Y port / +Z up, baseline origin. Game export: **metres**, −Z bow / −X port / +Y up, waterline origin; `(x,y,z) → (−y,z−6.5,−x)`. Scale **once** using the genuine 10 m calibration markers.
* Seven deck datums, 203 separately inventoried physical spaces, 13 main stair flights and four engine-room ladders. A physical-space count is not a count of unique room designs or a safety certificate.
* **Built:** 628 passenger sleeping positions (228 first / 132 second / 268 third) plus 117 crew berths. First class includes **114 permanent beds + 114 modeled convertible settee berths**, not 228 permanent beds; settee conversion/live sleeping use is not implemented/accepted. The 900/196 planning targets and inherited 1,080/196 claim are **not achieved**. First-/second-class dining contain **96 / 48 actual chairs**, not the first-class 228-seat planning target. No invisible accommodation or seating is counted.
* Nine single-ended Scotch boilers and one triple-expansion plant: 1.40 / 2.25 / 3.50 m bores, 1.80 m stroke, signed 72 rpm nominal; 5.30 m pitched bronze screw. Approximately 19.3 kn is a kinematic gameplay target, **not** a resistance, indicated-power or sea-trial result.

### Rebuild and check

Requires Blender **4.2 LTS** (4.2.3 used) and external Python with NumPy, Pillow, SciPy and Matplotlib; see [`blender/leonidas_ii/requirements.txt`](blender/leonidas_ii/requirements.txt). CairoSVG is optional for PDF conversion. Blender supplies its own Python/NumPy. Set `BLENDER_BIN` to your executable. The portable Linux build may require its `lib/` directory on `LD_LIBRARY_PATH`.

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
python3 tools/make_leonidas_review.py
# Open/review every image and record exact hashes before this strict gate:
python3 tools/check_leonidas_delivery.py --require-evidence --require-reviewed
```

`tools/build_leonidas_ii.sh` orders the master build, actual-shell/stern structural audit, lower-tessellation GAME build, packed map preparation, closed-component GLB export, regional kit, exact exported component/normal audit and static validation. `build/` directories are regenerable scratch, not delivery dependencies. **Do not run `tools/leonidas_revision_fixes.py`: it records a one-off, non-idempotent migration already applied to the source.**

The independent component audit restores missing regional GLB scratch files directly from the hash-verified delivered archive; it does not need to rebuild or change the editable master to re-check a delivery.

The import kit uses solid XZ compression to avoid redundant embedded images. Extract with `tar -xJf Aurelian_Roblox_Import_Kit.tar.xz`, 7-Zip, or a compatible archive utility. Its contents are normal glTF 2.0 GLBs and an `.rbxmx` control package; no Draco decoder, invented Roblox asset IDs or external texture CDN is required. Textures may need your authorised Studio uploads.

### Integration and acceptance boundary

Implemented contracts include boarding/gangway and mooring interlocks, signed ahead/astern orders, separate firing/regulator controls, helm, articulated crank/rods/shaft/propeller, rudder/quadrant, doors, seating and locally budgeted lighting/effects. **They have not been accepted in Roblox Studio.** There is no measured client FPS, multiplayer passenger-carry validation, continuous Humanoid collision test or hydrodynamic navigation-collision solver. Follow the unchecked live test sheet before using this in a published experience.

Boat/port work was inspected at the recorded branch tips; only ship-owned host interfaces are supplied. Three compatible craft sockets do not establish the inherited eleven-boat lifesaving inventory. No other agent's asset is changed and no joint world-fit approval is claimed.

### Provenance and branch

Branch **`agent/leonidas-ii`**, based on `75bf4ac5770b803919b36c8dbdb5374df82d88ac` from `agent/ship`. New work is namespaced in the repository's existing directory structure; there is no `projects/` tree. Root README and the dimension entry point now point to LEONIDAS-II. Original generators, models, renders, interfaces and runtime sources remain in Git as provenance, **not** the intended install path. The [inherited README](docs/leonidas_ii/inspection/INHERITED_README.md) and [inherited dimension manifest](docs/leonidas_ii/inspection/INHERITED_DIMENSION_MANIFEST.json) preserve their original claims verbatim.

The sandbox uses a sparse checkout for unchanged inherited binary files and keeps redundant Git history/reference clones in excluded cache to fit its saved-file budget. This does not alter those assets in the branch. A normal clone can use `git sparse-checkout disable`. Only if this sandbox's cache expires, run `python3 tools/restore_leonidas_checkout.py`; its local publication receipt can reconstruct the exact recorded commit from retained files. It never pushes or uses stored credentials.
