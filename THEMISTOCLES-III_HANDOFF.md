# THEMISTOCLES-III — Comprehensive Engineering, Render-Audit, and Delivery Handoff

**Prepared for:** the successor agent, **THEMISTOCLES-III**  
**Workspace root:** `/home/user/victoria`  
**Handoff state date:** 16 November 2026, Europe/Rome  
**Immediate mission:** finish the user-mandated, genuinely sequential visual correction and audit pass; then publish an honestly audited `boats/renders/GEN-1/` folder in a committed and **pushed** change on the designated branch.

---

## 0. Read this before changing anything

This document is intentionally exhaustive. The project is not in a completed-delivery state. The user explicitly rejected the idea of merely producing a big render batch and calling it done. Their active instruction is:

> “Re-check every single render you have of every boat, analyze it very thoroughly, and really ask yourself ‘Is there anything wrong?’, then ‘What can I improve?’. And only after you’ve satisfied both questions (not by covering up, but by actually fixing / improving), you can move onto the next render. Then I want a folder of renders pushed, not in your workspace, actually pushed. Call them GEN-1; next generation will be GEN-2 and so on. Really work hard!”

Treat this as an engineering/quality-assurance requirement, not prose. It implies all of the following:

1. **One final render at a time.** Render it, view that exact image, identify any defect, find the physical or technical root cause, fix it, rebuild/re-render, re-view it, and only then accept it and advance.
2. **No framing trick or hidden-object “fix” in beauty views.** A camera may improve presentation, but it must not conceal incorrect construction. If geometry, material, assembly, lighting, or the environment is wrong, fix that cause.
3. **The `GEN-1` folder is release-only.** It may contain only images that passed the individual review; diagnostics go elsewhere temporarily and must not be delivered. The historic `boats/renders/them2/` batch is rejected reference material, never a source to copy into `GEN-1`.
4. **A local folder is not delivery.** The final `GEN-1` directory and its README/ledger must be added, committed, and pushed to the remote branch. At this handoff, that has **not** happened.
5. **Do not silently overwrite history.** The next release after this one must be `GEN-2`, then `GEN-3`, etc. Do not relabel old files to pretend they are a new generation.

The geometry is substantially better than the older output, but the final set remains incomplete. Do not tell the user it is complete until the push exists and can be verified.

---

# Part I — Exact current status

## 1. Delivery status: NOT DONE

### What is complete and preserved in the working files

- Major geometry/material/assembly improvements described below have been made in the local workspace and rebuilt into the three `.blend` files.
- The corrected hull shell topology was audited after the key repair:
  - rowing cutter `Planking_Clinker`: **0 nonmanifold / 0 boundary edges**;
  - whaler `Planking_Clinker`: **0 nonmanifold / 0 boundary edges**;
  - steam cutter `Planking_DoubleDiagonal`: **0 nonmanifold / 0 boundary edges**.
- A local smoke render/review established that the earlier rowing/whaler black cockpit-slot defect is no longer present, and that the steam top framing improved after a camera-margin adjustment.
- The current workspace contains a draft `boats/renders/GEN-1/README.md` describing the release intent and corrections.

### What is incomplete / must not be claimed as accepted

- **No final release is committed or pushed.**
- The active `.git` directory is currently absent in this sandbox. A check from `/home/user/victoria` returned `fatal: not a git repository (or any of the parent directories): .git`. Therefore no current `git status`, `git log`, or current branch identity can be trusted until the repository is safely reconstructed.
- The full 45-image GEN-1 batch did not finish. The one-shot background process vanished before completing and there is no usable process log tail. Its status was `not_found`; do not assume it is still rendering.
- As of the handoff, `boats/renders/GEN-1/` contains only **nine provisional rowing PNGs** plus the draft README:
  - `rowing_bow_on.png`
  - `rowing_bow_quarter.png`
  - `rowing_broadside.png`
  - `rowing_hero.png`
  - `rowing_profile_high.png`
  - `rowing_stern_on.png`
  - `rowing_stern_quarter.png`
  - `rowing_top.png`
  - `rowing_underside.png`
- Those nine were created by a launch intended to generate the final set, but they have **not been individually inspected as the exact release candidates**. They are not accepted just because related QA renders looked plausible. The correct process is to inspect them one-by-one or discard/re-render them through the true sequential procedure.
- There are no final whaler or steam PNGs in `GEN-1` at this moment.
- The final end-to-end export/re-export, manifest/spec refresh, and `verify2.py` run must be redone after final changes before the commit. Earlier verification passes do not cover uncommitted newer source edits.

### Important consequence

The correct immediate stance is: **GEN-1 is a work-in-progress release directory, not a deliverable.** It is safer to delete/recreate its provisional PNGs (while retaining/recreating the README and ledger) and conduct a strict per-image pass than to inherit unreviewed images.

---

## 2. Git and credential recovery — treat carefully

Earlier in this effort, a baseline was successfully pushed to branch `agent/themistocles-ii`:

- parent full reconstruction/fidelity delivery: `36aa526`;
- later rejected 45-image batch: `544d94f5b7e635e690592c96059eae9d43c6926f` on `origin/agent/themistocles-ii`.

`544d94f…` is *not* a GEN-1 delivery. It only records an earlier 45-render batch that failed the later visual audit. It is an investigation reference, not something to bless or reuse.

Because `.git` disappeared in this current environment, do **not** start with `git reset --hard` against the live working tree: it contains valuable uncommitted source and rebuilt Blend changes. First make a safety archive **outside the repository metadata operation**, for example:

```bash
cd /home/user
# Preserve all current source, blends, docs, and generated GEN content.
tar --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
  -czf victoria-pre-git-recovery-$(date +%Y%m%d-%H%M%S).tgz victoria
```

Then reconstruct the repository only using the legitimate previously configured project remote / authorized project information. Do not invent a GitHub URL or branch. The generic safe sequence is:

```bash
cd /home/user/victoria
git init
git remote add origin <the-existing-authorized-project-remote>
git fetch origin agent/themistocles-ii
git checkout -B agent/themistocles-ii origin/agent/themistocles-ii
```

That checkout will overwrite files if performed in place. Prefer either:

- clone/fetch into a second directory, then copy the saved local changes from the archive into the clean clone; or
- record a complete file list/checksum archive first, carefully restore only relevant modified paths afterward.

After the repository is restored, inspect diffs rather than trusting the list in this document:

```bash
git status --short
git diff -- boats/scripts/them2/structure2.py
git diff -- boats/scripts/them2/boatlib2.py
git diff -- boats/scripts/render2.py
git diff -- boats/scripts/build2_rowing_cutter.py \
             boats/scripts/build2_whaler.py \
             boats/scripts/build2_steam_cutter.py
```

A user-provided GitHub personal access token existed earlier in the conversation. **Do not put it in this file, source, shell history, README, or commit.** Use it only if genuinely needed for the final authorized push, and tell the user to rotate/revoke it afterwards because it was supplied in chat. No user secrets belong in the repository.

---

## 3. Current important paths

### Models, source, and scripts

| Path | Purpose / current relevance |
|---|---|
| `boats/blend/boat_b2_rowing_cutter.blend` | Local rebuilt 25 ft pulling cutter, 43 parts. Contains post-thwart and post-keelson correction. |
| `boats/blend/boat_c2_whaler.blend` | Local rebuilt 27 ft whaler, 43 parts. Contains post-thwart and post-keelson correction. |
| `boats/blend/boat_a2_steam_cutter.blend` | Local rebuilt 25 ft steam cutter, 50 parts. Contains shell closure, anchor/grapnel, and keelson corrections. |
| `boats/scripts/them2/structure2.py` | Core structural geometry. Changed for double-skin closure/material behavior and the keelson explicit frame. Highest-priority shared file. |
| `boats/scripts/them2/boatlib2.py` | Changed for thwart basis/orientation and bottom-board layout. |
| `boats/scripts/build2_rowing_cutter.py` | Requests timber interior material for clinker inside. |
| `boats/scripts/build2_whaler.py` | Same interior clinker-material correction. |
| `boats/scripts/build2_steam_cutter.py` | Anchor/grapnel stowage moved to after sheets; do not revert. |
| `boats/scripts/them2/studio2.py` | Studio floor/background changed; black cove wedge was removed but environment must still be visually judged per image. |
| `boats/scripts/them2/mats2.py` | Improved wood/metal/palette and water material. |
| `boats/scripts/them2/bl2.py` | Render rig changes: studio world changes and non-studio water lighting changes. |
| `boats/scripts/render2.py` | View selectors/camera presets/hide/only controls. Current top margin was raised to 1.28; machinery margin/scale changed to 1.10/0.50. |
| `boats/scripts/export2.py` | Roblox export driver. |
| `boats/scripts/verify2.py` | Overall build/export verification. Must pass again before delivery. |
| `boats/scripts/gen_manifest2.py` | Generates manifest; it requires an explicit metadata JSON positional argument. |
| `boats/renders/them2/` | Historic rejected 45-image reference batch; never deliver as GEN-1. |
| `boats/renders/GEN-1/` | Incomplete provisional release directory: README + nine unaccepted rowing PNGs only. |
| `THEMISTOCLES-III_HANDOFF.md` | This handoff. Keep it at workspace root and include it in the final commit if appropriate. |

### Deliberately removed diagnostic outputs

Temporary directories such as `_review`, `_qa`, `_qa2`, `_qa_steam`, and `_finalspot` were cleared to avoid confusing diagnostic output with a release. A number of one-off diagnostic scripts were also removed after use: `diagnose_shell.py`, `mesh_audit.py`, `object_bounds.py`, `penetration_audit.py`, and `print_hull.py`. Their findings are retained in this document. Recreate diagnostics only if needed; do not assume the files still exist.

---

# Part II — What was done, why, and what was proven

## 4. Baseline technical contract that must remain true

The pre-existing project models three historically motivated boats:

1. **25 ft pulling/rowing cutter**;
2. **27 ft whaler**;
3. **circa-1888 steam cutter**.

Non-negotiable technical agreements inherited from the user/project:

- every Roblox part must remain at or below **19,000 triangles**;
- moving parts remain separate and use correct pivots;
- `Z = 0` is the solved **loaded waterline**;
- model/export checks in `verify2.py` must pass;
- documentation must remain honest: these models **have not been play-tested in Roblox Studio**;
- never make high-fidelity render changes that knowingly break Roblox/export requirements;
- user granted scope to improve materials, realism, construction, and visible detail without a ceiling, but quality must be actual rather than decorative noise.

Previously established numeric data (unchanged by this render correction pass):

| Craft | Light draught / displacement | Loaded draught / displacement |
|---|---:|---:|
| Rowing cutter | 0.313 m / 1,112 kg | 0.663 m / 1,992 kg |
| Whaler | 0.297 m / 1,007.5 kg | 0.511 m / 1,487.5 kg |
| Steam cutter | 0.529 m / 3,212 kg | 0.769 m / 3,532 kg |

Earlier export totals, before the last uncommitted rebuild pass, were:

| Craft | Total triangles | Status |
|---|---:|---|
| Rowing cutter | 96,576 | per-part gate passed |
| Whaler | 94,292 | per-part gate passed |
| Steam cutter | 101,056 | per-part gate passed |

Do not cite those as final post-correction totals. Re-export and re-run the validation to get final truthful values.

---

## 5. The rejected render batch and the audit philosophy it triggered

A former quick Cycles batch produced **45 valid PNGs at 960 × 600**, fifteen per boat, typically at 16 denoised samples. It was committed in `544d94f…` and pushed previously. It looked superficially complete but was rejected under closer review. The user’s correction shifted the task from “render a batch” to “do individual root-cause visual QA.”

Significant previously observed defects:

- rowing/whaler interiors showed long dark longitudinal slots, initially suspected to be missing shell or sole geometry;
- interiors could read as exterior antifouling instead of timber;
- floor-board seams read as giant voids/uncovered central gaps;
- some dry studio views had a harsh floor/world horizon or broken cove response;
- water renders had a detached white ellipse/reflection and too-mirrorlike water;
- steam double-diagonal shell topology had 624 open/nonmanifold edge issues;
- steam top composition clipped hull ends;
- steam underside had a large dark stern/centreline wedge that made the model look broken;
- machinery close-up originally risked reading as a detached parts study rather than machinery integrated into a boat.

Each fix below exists because it was traced from a visual symptom to construction/source code rather than simply hidden.

---

## 6. Rowing cutter and whaler — cockpit/thwart root-cause correction

### Symptom

Dry interior/top views of the rowing cutter and whaler showed repeated long black slots. The black areas looked like enormous holes or missing interior shell construction.

### Diagnosis

The hull topology was initially verified watertight, so it was not sensible to paper over the symptom by adding a dark/bright material or changing the camera. Focused isolation renders were made with `render2.py --hide` and `--only`, including variants where structure, floor, and thwarts were separately shown. They demonstrated the offending geometry came from `Thwarts`.

`boatlib2.thwart_layout()` handed an outline whose logical dimensions are:

- athwartship length;
- fore-and-aft width;
- vertical thickness.

But the underlying plate builder used default XY coordinates. The construction basis was therefore wrong: the long side was effectively fore-and-aft, and boards overlapped along the length of the boat. This physically made the black “slot” artifact.

### Fix

`boats/scripts/them2/boatlib2.py` was altered to map thwart plate geometry through an explicit local basis:

- logical athwartship axis → world `Y`;
- logical fore-and-aft axis → world `X`;
- logical thickness axis → world `Z`.

The two narrow edge mouldings were correspondingly oriented in the correct fore-aft sense. Rebuilds after this change reported 43 parts for rowing and 43 parts for whaler.

### Evidence

Post-fix QA top/interior views clearly showed distinct athwartship thwarts instead of one set of overlapping lengthwise boards. This is a geometry correction, not a camera workaround.

### What THEMISTOCLES-III must still do

For the exact final `GEN-1` images, check all rowing and whaler views for:

- every thwart spanning realistically from side to side;
- no duplicate/overlapping centred boards;
- no unexpected black z-fighting/shadows between thwarts;
- smooth and plausible spacing at bow/stern where thwarts taper or omit;
- knees/risers joining realistically rather than floating or cutting through planking;
- visual consistency between top, interior, bow-on, stern-on, broadside, construction, and water views.

If one view finds a remaining actual construction flaw, return to source/rebuild all affected boats before accepting any later final images.

---

## 7. Bottom boards / sole — real construction improvement

### Original problem

The rowing/whaler central sole previously had panels and joints that visually merged into overly large dark voids. A central gap around the keelson made the interiors look hollow or unfinished.

### Changes

`boatlib2.py` was changed to give the interior a more credible arrangement:

- five narrow fore-and-aft floorboards per side;
- staggered three-panel lift-out sections;
- narrow, dispersed butt joints rather than aligned full-width gaps;
- raised, capped central keelson.

This arrangement is intentionally removable floor construction, not one homogeneous slab, and it visibly breaks up unrealistic uninterrupted gaps.

### Audit instructions

Check it under changing camera/lighting angles, not just top view. In the interior, bow-quarter, stern-quarter, and water hero views, ask:

1. Are butt joints narrow and plausible rather than black slots?
2. Are boards visibly supported by floors/frames in a believable way?
3. Does the raised central member read as a keelson cap rather than a random spine?
4. Are there any world-visible holes to daylight that cannot be justified by actual limber construction?
5. Are shadows stable or is there z-fighting?

---

## 8. Interior shell material correction

### Problem

Although rowing/whaler clinker hulls were topologically sound, their inside surfaces could read as the pink antifouling/exterior material. This weakened the boats’ interior realism and confused the construction.

### Fix

`structure2.py` gained support for independent interior material in `clinker_strakes()`. Both the rowing and whaler builders now request timber interior material (`mat_inner=21`). The exterior’s deliberate white upper sheer strake remains (normally `mat_top=22`) and is not a shader accident.

### Review expectation

Do **not** “fix” the intended white upper sheer strake. Instead, verify the exposed inner planking visibly reads as warm/weathered timber under the final lighting, while outer bottom/topside treatments remain consistent externally.

---

## 9. Steam double-diagonal shell: topology closure repair

### Original problem

A diagnostic topology audit showed `Planking_DoubleDiagonal` with **624 boundary/nonmanifold edges**. That was an actual shell-closure fault, not merely a render blemish.

### Fix

`structure2.py`’s double-skin/double-diagonal logic was altered to close shell perimeters and hoods. Post-rebuild mesh audits reported:

- steam `Planking_DoubleDiagonal`: **0 nonmanifold / 0 boundary edges**.

The two rowing/whaler clinker shell audits likewise reported 0/0.

### Review expectation

A closed mesh can still render poorly. In final steam images, examine:

- any unexpected black slits at stems, transom, or turn of bilge;
- unwanted overlaps/layers peeking through exterior surface;
- wet/dry material edges that make the shell seem inside-out;
- whether construction view still communicates double-diagonal structure honestly;
- whether the interior works visually without showing antifouling or self-intersections.

If topology needs another change, rerun the mesh audit after rebuilding. Do not settle for “it has no holes in the audit” if the render has physically implausible artefacts.

---

## 10. Steam cutter anchor/grapnel penetration correction

### Original problem

The steam anchor and grapnel had been positioned from/near the keel datum and genuinely pierced the hull. This caused visible undesirable underside geometry and was a physical placement bug.

### Fix

`build2_steam_cutter.py` was changed so anchor and grapnel are stowed on the after sheets around `Z = 0.22`, rather than originating through the shell at keel level. The steam cutter was rebuilt (50 parts).

### Important caution

Moving anchor/grapnel did **not** by itself remove the big underside wedge. Do not revisit it as the explanation for the major wedge; it fixed a different genuine bug. The final normal beauty/interior images should show stowage sitting credibly on the after sheets. In underside technical imagery, it is reasonable to use a narrowly scoped structural visibility selection so unrelated *interior* stowage cannot block a technical hull inspection—provided the README clearly says so and it is not mislabeled as a normal full-assembly beauty render.

---

## 11. The shared keelson sweep bug — critical root-cause correction

### Symptom

Steam underside rendered a severe dark/black wedge near the stern/centreline. Anchor/grapnel repositioning did not eliminate it. Hull-only isolation was clean; hiding just rudder did not eliminate it. Object bounds revealed the steam `Keelson` extended to `Z = -0.89` while the exterior double-diagonal shell bottom was around `Z = -0.77`.

The analogous members were also too low in the other boats:

- rowing keelson low bound roughly `-0.77` versus clinker shell around `-0.52`;
- steam keelson low bound `-0.89` versus shell `-0.77`;
- whaler was likewise suspect.

### Why it happened

The generic sweep used by `structure2.keelson()` transported a local second axis downward for a +X path. The “inner keelson” was swept using an implicit frame and had its depth axis pointing down through the exterior hull, rather than up inside the bilge.

### Fix

`structure2.py` now supplies a right-handed explicit frame for the sweep:

- athwartship axis: `(0, 1, 0)`;
- upward axis: `(0, 0, 1)`.

A code comment explains this exact historical failure. The relevant intent is: the longitudinal path is +X; explicit athwartship/up local directions prevent the generic transported frame from turning the inner structure downward.

### Post-fix measured bounds

After rebuilding all three boats:

| Craft | Keelson Z bounds | Exterior shell reference |
|---|---:|---:|
| Rowing | -0.63 to -0.43 | `Planking_Clinker` low about -0.52 |
| Whaler | -0.48 to -0.33 | loaded keel vicinity about -0.511; inspect visually |
| Steam | -0.73 to -0.49 | `Planking_DoubleDiagonal` low -0.77 |

The steam keelson is now within the hull envelope. Its lower edge is above the shell’s low point; it no longer physically projects below the whole hull. A prior sampled section check also confirmed shell keel and inner offset geometry follows the expected relationship.

### Nuance: the dark underside region

A later isolated render without keelson still appeared to show the dark wedge. Further hides showed it was not uniquely caused by keelson, anchor/grapnel, or engine; it partly corresponds to legitimate stern/centreline structural/interior presentation and complicated overlapping visible items in a normal full-boat underside camera. The correct resolution for a *technical underside release image* is not to pretend it is a clean exterior if unrelated interior furniture is being seen through/around the opening. The latest GEN-1 render plan uses `--only` to show these intended exterior components:

```text
Planking_DoubleDiagonal
Keel_Stem_Sternpost
Transom
Rudder
Propeller
Shaft_Line
Shaft_Bracket
Lifting_Eyes
Fenders
```

That is not a cover-up of the keelson bug: the keelson was independently geometrically fixed. It is a clearly scoped technical exterior view. Keep the label/readme wording honest and separately inspect normal interiors/beauty views to prove the complete boat is sound.

### Required final review

- inspect a full normal steam underside diagnostic privately, even if it is not released;
- inspect the released technical underside and ensure all selected gear appears credible, centred, non-floating, and not accidentally clipped;
- inspect the full interior and machinery view to ensure the interior keelson and stern area are correct;
- never claim that the outer `Keel_Stem_Sternpost`, which intentionally reaches farther down (historically around `Z=-1.00`), is an error. It is exterior keel hardware, unlike the corrected *inner* keelson.

---

## 12. Lighting, studio floor, water, and camera changes

### Studio environment

`studio2.py` was modified to remove an earlier black cove/floor wedge. `bl2.py` was also changed to lighten the studio world/background. The first hard world/floor discontinuity did not disappear merely by changing the world color, and later elevated dry camera directions were a partial improvement rather than a proof of success.

**Do not automatically accept studio views.** For each one, judge whether it has:

- a hard unnatural horizon line;
- visible floor edge / clipping boundary;
- a black wedge or suddenly dark reflected plane;
- background banding or perspective cues that distract from the boat;
- shadows that make intended open interiors illegible;
- enough elevation to present the hull but not make it look like a drone product shot.

If there is a real studio geometry/material issue, fix `studio2.py` or the render rig. Do not crop around it.

### Water environment

`mats2.py` was changed so water is more opaque and rougher; `bl2.py` changes ensure non-studio afloat views disable studio lights. This removed the old detached white reflection ellipse and mirror-boat response in revised rowing/steam QA heroes. Whaler afloat final review still needs the same scrutiny.

In every afloat image, verify:

- no detached white disk/ellipse;
- no duplicate mirrored boat/reflection that reads as a second hull;
- waterline is credible at the solved loaded state (`Z=0` convention);
- hull does not look levitating or sunk;
- enough small wave/roughness to read as water without turning into foam/noise;
- no studio light or floor leak survives;
- visible shadow/reflection supports scale but does not eclipse hull form.

### Camera presets

The current `render2.py` changes include:

- dry broadside/bow/stern elevation in the safer revised range (earlier set at `0.30`);
- top margin increased ultimately to **1.28** (earlier 1.12 still clipped the steam ends);
- interior margin previously increased to **1.14**;
- machinery view margin/scale currently **1.10 / 0.50** (compared to 1.04 / 0.42) so the machinery close-up is contextual and does not look like disconnected objects.

A spot check after the 1.28 top change showed the full steam hull with credible end clearance, though one end comes close to the frame. Keep an aesthetic eye on it. A true top view should afford enough air around both bow/stern and be visually balanced, not merely avoid literal clipping.

---

# Part III — Build, render, export, and verify playbook

## 13. Environment recovery

Blender and Git may disappear between sandbox states. If Blender is unavailable, install it using:

```bash
cd /home/user/victoria
bash boats/scripts/setup_blender.sh
```

Expected command pattern uses:

```bash
LD_LIBRARY_PATH=/var/tmp/blender/lib /var/tmp/blender/blender
```

Do not presume `/var/tmp/blender` exists after a restart; run setup if needed. Avoid launching default-quality Cycles renders for all boats in parallel. Prior attempts resulted in steam being OOM-killed (`exit 137`) and incomplete rowing/whaler work. Render sequentially.

If a Blender job hangs or an abandoned process remains, inspect process list and terminate carefully:

```bash
pgrep -af blender
pkill -9 -f 'blender -b'   # only after confirming it is a stale job
```

`stop_process` may not kill Blender grandchildren reliably.

---

## 14. Rebuild sequence

Before visual final rendering after source changes, rebuild all affected boats. The shared `structure2.py` keelson change affects all three, so build all three.

```bash
cd /home/user/victoria/boats/scripts

LD_LIBRARY_PATH=/var/tmp/blender/lib /var/tmp/blender/blender -b \
  --python build2_rowing_cutter.py

LD_LIBRARY_PATH=/var/tmp/blender/lib /var/tmp/blender/blender -b \
  --python build2_whaler.py

LD_LIBRARY_PATH=/var/tmp/blender/lib /var/tmp/blender/blender -b \
  --python build2_steam_cutter.py
```

Expected successful build messages historically were:

```text
BUILT ROWING CUTTER: 43 parts
BUILT WHALER: 43 parts
BUILT STEAM CUTTER: 50 parts
```

Then run `python3 -m py_compile` on changed Python modules before spending time rendering:

```bash
python3 -m py_compile \
  boats/scripts/them2/structure2.py \
  boats/scripts/them2/boatlib2.py \
  boats/scripts/them2/studio2.py \
  boats/scripts/them2/bl2.py \
  boats/scripts/them2/mats2.py \
  boats/scripts/render2.py \
  boats/scripts/build2_rowing_cutter.py \
  boats/scripts/build2_whaler.py \
  boats/scripts/build2_steam_cutter.py
```

Do not interpret `--res` in `render2.py` as an active resolution controller: the script accepts it but does not use `args.res`. `--quick` is what changes samples/resolution behavior. Fix this script if controlled intermediate resolution is important, and then document the exact effect.

---

## 15. Rendering one release candidate at a time

Use `render2.py`; it supports `--hide` and `--only`, which are preferable to ad-hoc scene scripts for targeted diagnostics. A generic one-view pattern:

```bash
cd /home/user/victoria/boats/scripts
OUT=../renders/GEN-1
mkdir -p "$OUT"

LD_LIBRARY_PATH=/var/tmp/blender/lib /var/tmp/blender/blender -b \
  ../blend/boat_b2_rowing_cutter.blend \
  --python render2.py -- \
  --out "$OUT" --prefix rowing \
  --views broadside --sea 0 --studio 1 --quick
```

Then use the image viewer on the exact output before proceeding. If it fails, return to source and rebuild—not just to `render2.py` unless camera/light itself is actually the cause.

Recommended order is deliberately functional rather than batch-oriented:

1. rowing dry broadside;
2. rowing dry bow quarter;
3. rowing dry stern quarter;
4. rowing bow-on;
5. rowing stern-on;
6. rowing top;
7. rowing full/private underside diagnostic, then scoped release underside;
8. rowing interior;
9. rowing construction;
10. rowing studio hero/profile;
11–14. rowing afloat views;
15. repeat the same disciplined pattern for whaler;
16. repeat for steam, with a private full underside and integrated machinery view.

This is slower than the aborted 45-image farm. It meets the actual user instruction.

---

## 16. Intended GEN-1 manifest (45 final images)

Once individually accepted, the release should contain **exactly 45 PNGs**, 960 × 600 (unless you deliberately revise and document output specs). This proposed naming is based on the existing renderer prefixes:

### Rowing cutter — 15

```text
rowing_broadside.png
rowing_bow_quarter.png
rowing_stern_quarter.png
rowing_bow_on.png
rowing_stern_on.png
rowing_top.png
rowing_underside.png
rowing_hero.png
rowing_profile_high.png
rowing_interior.png
rowing_construction_construction.png
rowing_water_hero.png
rowing_water_bow_quarter.png
rowing_water_stern_quarter.png
rowing_water_profile_high.png
```

### Whaler — 15

```text
whaler_broadside.png
whaler_bow_quarter.png
whaler_stern_quarter.png
whaler_bow_on.png
whaler_stern_on.png
whaler_top.png
whaler_underside.png
whaler_hero.png
whaler_profile_high.png
whaler_interior.png
whaler_construction_construction.png
whaler_water_hero.png
whaler_water_bow_quarter.png
whaler_water_stern_quarter.png
whaler_water_profile_high.png
```

### Steam cutter — 15

```text
steam_broadside.png
steam_bow_quarter.png
steam_stern_quarter.png
steam_bow_on.png
steam_stern_on.png
steam_top.png
steam_underside.png
steam_hero.png
steam_profile_high.png
steam_interior.png
steam_construction_construction.png
steam_water_hero.png
steam_water_bow_quarter.png
steam_water_stern_quarter.png
steam_machinery_machinery.png
```

The `steam_underside` final image should be the scoped technical exterior selection described earlier. Keep the full normal underside as a private audit render to prove the entire assembly is not being hidden from scrutiny.

Do not emit a contact sheet as one of the 45 release PNGs. A contact sheet can be an audit artifact outside `GEN-1`, if useful.

---

## 17. Per-image review ledger template

The release README should be expanded or accompanied by `boats/renders/GEN-1/AUDIT_LEDGER.md`. This is not bureaucracy: it proves that every exact file had the mandated sequence. Suggested columns:

| # | Exact final filename | Physical/visual intent | “Anything wrong?” result | Root-cause fix if needed | “What can improve?” result | Accepted? |
|---:|---|---|---|---|---|---|
| 01 | `rowing_broadside.png` | exterior silhouette, sheer, cove/background | Pending | — | Pending | No |
| 02 | `rowing_bow_quarter.png` | bow construction, clinker rhythm, stem | Pending | — | Pending | No |
| 03 | `rowing_stern_quarter.png` | stern/transom/rudder/stowage | Pending | — | Pending | No |
| 04 | `rowing_bow_on.png` | symmetry/stem/background | Pending | — | Pending | No |
| 05 | `rowing_stern_on.png` | symmetry/transom/rudder/background | Pending | — | Pending | No |
| 06 | `rowing_top.png` | thwarts, sole, oars/stowage layout | Pending | — | Pending | No |
| 07 | `rowing_underside.png` | clinker/keel exterior and appendages | Pending | — | Pending | No |
| 08 | `rowing_hero.png` | studio beauty/legibility | Pending | — | Pending | No |
| 09 | `rowing_profile_high.png` | upper hull/interior read | Pending | — | Pending | No |
| 10 | `rowing_interior.png` | thwarts, sole, timber material | Pending | — | Pending | No |
| 11 | `rowing_construction_construction.png` | internal structure correctness | Pending | — | Pending | No |
| 12 | `rowing_water_hero.png` | loaded waterline/reflection | Pending | — | Pending | No |
| 13 | `rowing_water_bow_quarter.png` | bow afloat | Pending | — | Pending | No |
| 14 | `rowing_water_stern_quarter.png` | stern afloat | Pending | — | Pending | No |
| 15 | `rowing_water_profile_high.png` | side profile afloat | Pending | — | Pending | No |
| 16 | `whaler_broadside.png` | exterior silhouette, sheer, cove/background | Pending | — | Pending | No |
| 17 | `whaler_bow_quarter.png` | bow construction/stem | Pending | — | Pending | No |
| 18 | `whaler_stern_quarter.png` | stern/transom/rudder | Pending | — | Pending | No |
| 19 | `whaler_bow_on.png` | symmetry/background | Pending | — | Pending | No |
| 20 | `whaler_stern_on.png` | symmetry/background | Pending | — | Pending | No |
| 21 | `whaler_top.png` | separate thwarts/sole layout | Pending | — | Pending | No |
| 22 | `whaler_underside.png` | hull/keel exterior | Pending | — | Pending | No |
| 23 | `whaler_hero.png` | studio beauty/legibility | Pending | — | Pending | No |
| 24 | `whaler_profile_high.png` | upper hull/interior read | Pending | — | Pending | No |
| 25 | `whaler_interior.png` | timber inside, floor, thwarts | Pending | — | Pending | No |
| 26 | `whaler_construction_construction.png` | structure/frames | Pending | — | Pending | No |
| 27 | `whaler_water_hero.png` | no detached reflection ellipse | Pending | — | Pending | No |
| 28 | `whaler_water_bow_quarter.png` | bow afloat | Pending | — | Pending | No |
| 29 | `whaler_water_stern_quarter.png` | stern afloat | Pending | — | Pending | No |
| 30 | `whaler_water_profile_high.png` | profile afloat | Pending | — | Pending | No |
| 31 | `steam_broadside.png` | hull/boiler/funnel integration | Pending | — | Pending | No |
| 32 | `steam_bow_quarter.png` | bow shell and fore cabin | Pending | — | Pending | No |
| 33 | `steam_stern_quarter.png` | transom/shaft/rudder area | Pending | — | Pending | No |
| 34 | `steam_bow_on.png` | symmetry/bow treatment | Pending | — | Pending | No |
| 35 | `steam_stern_on.png` | stern/rudder symmetry | Pending | — | Pending | No |
| 36 | `steam_top.png` | full hull clearance, machinery layout | Pending | — | Pending | No |
| 37 | `steam_underside.png` | scoped exterior technical view | Pending | — | Pending | No |
| 38 | `steam_hero.png` | studio beauty/legibility | Pending | — | Pending | No |
| 39 | `steam_profile_high.png` | overall assembly/internals | Pending | — | Pending | No |
| 40 | `steam_interior.png` | shell/frames/keelson/machinery | Pending | — | Pending | No |
| 41 | `steam_construction_construction.png` | hull structural story | Pending | — | Pending | No |
| 42 | `steam_water_hero.png` | loaded hull/no studio reflection | Pending | — | Pending | No |
| 43 | `steam_water_bow_quarter.png` | bow afloat | Pending | — | Pending | No |
| 44 | `steam_water_stern_quarter.png` | stern afloat/gear | Pending | — | Pending | No |
| 45 | `steam_machinery_machinery.png` | machinery contextualized in intact boat | Pending | — | Pending | No |

A “No defect found” result is acceptable only if it includes a short concrete observation, e.g. “all six thwarts independently bridge the risers; no z-fight or longitudinal overlap; no horizon discontinuity at top 20% of frame.” Never populate this ledger with vague “looks good.”

---

## 18. Final render integrity test

After final visual acceptance and before committing, validate exact file count, dimensions, and basic PNG readability:

```bash
cd /home/user/victoria/boats/scripts
python3 - <<'PY'
from pathlib import Path
from PIL import Image
imgs = sorted(Path('../renders/GEN-1').glob('*.png'))
assert len(imgs) == 45, f'Expected 45 final PNGs, found {len(imgs)}'
for p in imgs:
    with Image.open(p) as im:
        assert im.size == (960, 600), f'{p}: {im.size}'
        im.verify()
print(f'GEN-1 integrity PASS: {len(imgs)} PNGs at 960x600')
PY
```

If the user asks for another resolution, revise the contract honestly and change this check/README. Do not use `--res` believing it controls the renderer until the source has been fixed.

---

## 19. Re-export and verification before push

The correct export invocation template, from `boats/scripts`, is:

```bash
LD_LIBRARY_PATH=/var/tmp/blender/lib /var/tmp/blender/blender -b \
  ../blend/boat_b2_rowing_cutter.blend --python export2.py -- \
  --out ../exports/rowing2 --meta ../blend/boat_b2_meta.json \
  --cls rowing_cutter_25ft --limit 19000
```

Equivalent final commands must be used for:

- `boat_c2_whaler.blend`, `../exports/whaler2`, metadata `boat_c2_meta.json`, class `whaler_27ft`;
- `boat_a2_steam_cutter.blend`, `../exports/steam2`, metadata `boat_a2_meta.json`, class `steam_cutter_1888`.

Then regenerate manifests/specs using their documented input forms. Reminder: `gen_manifest2.py` needs an export metadata JSON passed as `sys.argv[1]`; it does **not** batch-run correctly with no argument.

Run final `verify2.py` after those exports. Preserve the exact terminal result in a final changelog/commit message or delivery note. The earlier result was `ALL THEM2 CHECKS PASS`, but it should be re-earned after final source work.

---

# Part IV — Known tools, API caveats, and failed approaches

## 20. Things that have already failed — do not blindly repeat them

1. **Parallel full Cycles rendering:** Bad. A prior attempt ran all three at once; steam was OOM-killed with exit 137 and rowing/whaler were stopped early. Render sequentially.
2. **Treating the 45-image farm as acceptance:** Bad. Even if one batch completes, user requires actual render-by-render review and root-cause repair.
3. **Using a camera to hide the black cockpit slots:** Bad. The cause was wrong thwart geometry and it was fixed structurally.
4. **Changing world color alone to eliminate studio horizon:** Insufficient. The scene geometry/environment must be checked in every view.
5. **Repositioning anchor/grapnel as solution to steam underside wedge:** It fixed a real shell penetration but did not explain every dark underside feature. The shared keelson root cause was discovered separately.
6. **Hiding only rudder in steam underside:** Insufficient. The wedge remained.
7. **Assuming closed topology guarantees visual correctness:** False. Closed hulls still require readability/composition/material QA.
8. **First parallel rowing/whaler QA2 invocation:** Initial rowing output was blank/nonzero; rerunning rowing alone worked. Treat blank/partial render processes as invalid.
9. **Assuming `--res` is active:** It is currently ignored by `render2.py`; only `--quick` changes render behavior.
10. **Sustained hidden background Blender processes:** They can continue after tool timeout or lose their wrapper process. Always confirm exact output count and process status.

## 21. Geometry utility caveats

- `sphere()` accepts `squash_z`, not `squash`.
- `torus()` returns `None` and writes into the supplied mesh builder; do not expect a mesh object return value.
- Do not reintroduce a signed-range `smoothstep` clamp issue.
- Current critical sweep correction depends on the explicit local frame in `structure2.keelson()`. If refactoring sweep APIs, preserve its meaning and re-check keelson bounds/in-hull placement on all three boats.

---

# Part V — Recommended successor runbook

## 22. First 30 minutes

1. Read this document and inspect file existence, Blender installation, render folder contents, and the absence/presence of `.git`.
2. Create the safety archive before any git recovery.
3. Restore the repository from its authorized remote into a safe clone or reconstruct it without losing local modifications.
4. Compare local modified source/blend files to baseline and preserve all meaningful corrections.
5. Run `py_compile`.
6. Rebuild all three boats.
7. Run targeted topology/aabb checks if you modified sweep/structural code. Confirm steam keelson stays inside external hull envelope.
8. Re-render only the first required final image: `rowing_broadside.png`.
9. View it. Write an actual ledger entry. Fix/rebuild/re-render if anything deserves correction.
10. Continue one image at a time.

## 23. Practical audit checklist for every render

Use all categories that apply:

### Geometry/assembly

- Is there a seam, floating object, interpenetration, self-shadow void, duplicate, or z-fight?
- Does a structural member connect to something plausible?
- Do port/starboard systems remain symmetric where expected?
- Are separate moving/functional parts visibly and logically separate?
- Is there accidental exterior penetration from interior equipment?

### Construction authenticity/readability

- Do frames, planking, thwarts, sole, knees, risers, and rails explain the boat rather than create visual clutter?
- Does the steam machinery appear installed and supported, not scattered?
- Is the construction/technical view labelled honestly according to what it shows?

### Materials/lighting

- Are interior and exterior material assignments correct?
- Is white sheer strake intentionally retained?
- Does metal read as metal without turning black or plastic?
- Are highlights revealing form rather than hiding it?
- Does background/floor/water support rather than distract?

### Camera/composition

- Is every hull end visible with breathing room? (Especially steam top.)
- Is the intended detail legible at 960×600?
- Is a close-up still contextual?
- Does the subject sit comfortably in frame with no accidental crop?

### Water

- Waterline correct at loaded condition?
- No detached ellipse, studio light, mirror duplicate, improper shadow?
- Do ripples/reflection look physically plausible at this scale?

### Release hygiene

- Is the exact file named correctly and in GEN-1 only after acceptance?
- Does ledger record an explicit outcome?
- Does a root-cause source fix require re-review of previous accepted images for the affected boat(s)? If so, invalidate and re-render them—do not grandfather stale images.

---

## 24. How to handle a newly found flaw without violating the protocol

When an image fails:

1. Keep a diagnostic copy outside `GEN-1` or record the issue in the ledger.
2. State a falsifiable hypothesis: e.g. “dark artifact tracks `Thwarts`, not hull,” rather than “looks weird.”
3. Isolate components with `render2.py --hide`/`--only` only for diagnosis.
4. Inspect relevant source, object transforms, mesh bounds, material slots, and topology as needed.
5. Fix source construction/material/rig/environment.
6. Rebuild every craft impacted by shared source.
7. Re-run necessary mechanical tests (compile, mesh audit, export constraints where relevant).
8. Re-render the failed image from scratch.
9. View it and document the post-fix observation.
10. Re-render/recheck earlier images that changed as a consequence of the shared fix.

A technical view may legitimately isolate a subset only when its purpose is explicit and the complete model is audited through other views. It must never be used to make an invalid complete assembly appear good.

---

# Part VI — Release content, docs, and final push

## 25. README requirements

Keep `boats/renders/GEN-1/README.md`, but update it to match final reality. The current draft already says:

- GEN-1 is separate from rejected `them2` renders;
- it contains 45 960×600 PNGs (currently false while incomplete, so only leave this assertion after completion);
- it identifies the three craft and the technical scoped steam underside;
- it lists corrected defects: thwarts, floor/keelson cap, inner shell timber, steam shell/stowage, and render environment.

Before commit, ensure it does **not** claim 45 images until integrity test passes. Add a short “validation” section with the final exact test results. If the runtime format/resolution changes, update it.

`AUDIT_LEDGER.md` should record all 45 individual reviews. Do not expose raw internal-chain-of-thought; concise engineering observations and corrections are enough.

## 26. Suggested commit boundaries

If practical after restoring git:

1. A source/build correction commit (geometry, material, rig/render source, rebuilt Blend files, perhaps tests) that can be verified independently.
2. A render release commit containing `boats/renders/GEN-1/` exact images, README, and audit ledger.
3. Export/spec/manifest/verification changes may be grouped with the correction commit if that better reflects the project structure.

The user only cares that final GEN-1 actually lands pushed; clean commit structure makes the work credible and reviewable.

Suggested truthful final commit message pattern:

```text
THEMISTOCLES-II: publish audited GEN-1 render release

- correct thwart basis, sole/keelson construction, steam shell/stowage issues
- rebuild and revalidate three craft
- add 45 individually reviewed GEN-1 renders and audit ledger
```

Only include statements actually demonstrated by final work.

## 27. Push verification

After `git add`, `git commit`, and authorized `git push origin agent/themistocles-ii`, prove the remote update rather than assuming it worked:

```bash
git status --short
git log --oneline -1
git ls-remote origin refs/heads/agent/themistocles-ii
```

Confirm the remote branch tip matches the local commit. If using the previously user-supplied credential, advise the user to rotate it after the verified push.

---

# Part VII — Final factual snapshot for fast reference

## 28. High-value facts

- User wants quality improvement with **no ceiling**, but demands physical/technical fixes instead of concealment.
- User’s generations begin at **GEN-1**; later render revisions must be **GEN-2**, etc.
- The earlier `them2` render set is rejected and must never be copied to GEN-1.
- Current local blends were rebuilt successfully after shared keelson correction:
  - rowing 43 parts;
  - whaler 43 parts;
  - steam 50 parts.
- Shell topology after repairs was recorded at 0 nonmanifold / 0 boundary for all three relevant planking meshes.
- Steam top camera margin is current 1.28; latest smoke image showed improved compositional clearance.
- Steam machinery camera changed to margin 1.10 / scale 0.50 and reads as machinery in a boat rather than detached parts.
- A normal full steam underside can visually expose unrelated internal/centreline items; release technical underside is a documented scoped exterior selection, after the actual inner keelson bug was fixed.
- No active rendering process remains from the aborted GEN-1 batch; it disappeared after making nine provisional rowing images.
- `GEN-1` currently contains only those 9 PNGs and README. It is not a release.
- Git metadata is currently missing from the workspace. Do not lose local changes while restoring it.
- `google_docs` is connected but OFF for this conversation. It is irrelevant to the task. If a user asks you to use it, first tell them to turn it on; do not use it while disabled.

## 29. What “done” looks like

Do not conclude until all are true:

- [ ] Repository safely restored and local correction work preserved.
- [ ] All source changes compile and all three Blend files rebuild.
- [ ] All relevant topology/structural checks pass after final modifications.
- [ ] Exports regenerated; every Roblox part obeys 19k triangles; `verify2.py` passes.
- [ ] `boats/renders/GEN-1/` contains exactly 45 valid release PNGs plus honest README/ledger.
- [ ] Every one of the 45 exact images has an explicit audit ledger entry based on direct review.
- [ ] All defects identified during review have underlying fixes, not camera concealment.
- [ ] No `them2` image is passed off as GEN-1.
- [ ] The complete delivery, including GEN-1, is committed to `agent/themistocles-ii`.
- [ ] The commit is pushed to remote and remote tip is verified.
- [ ] The user is told the generation/commit status and, if a chat-provided PAT was used, advised to rotate it.

---

## 30. Closing instruction to THEMISTOCLES-III

The most important behavioral correction is simple: **do not optimize for rendering throughput; optimize for deserved acceptance.** The project has already demonstrated why a pretty-looking batch can conceal real construction errors. Make the next successful result defensible at every level: geometry, topology, material semantics, camera composition, lighting, image integrity, Roblox export, documentation, commit, and push.

When in doubt, slow down, inspect the exact image, and fix the cause.
