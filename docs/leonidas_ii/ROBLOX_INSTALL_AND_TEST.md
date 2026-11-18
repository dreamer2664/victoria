# SS Aurelian — Studio import and acceptance

**Status: a generated import kit and new runtime are supplied; no Studio import, live avatar test, multiplayer test or frame-time benchmark has been performed here.** Do not label this a tested playable release. The old controller scripts are retained unchanged for provenance, not intended to run alongside the new controller.

## Contents / coordinate contract

* `exports/leonidas_ii/Aurelian_Roblox_Import_Kit.tar.xz`: regional GLB files, each with embedded PBR maps and four small calibration meshes, an insertable `Aurelian_Control_Package.rbxmx`, source maps and manifests. Extract first with `tar -xJf Aurelian_Roblox_Import_Kit.tar.xz`, 7-Zip, or an archive utility supporting XZ. Import all numbered regional files exactly once; they are complementary, not alternative LODs. Solid compression avoids a redundant large ZIP; the extracted GLBs are standard uncompressed glTF 2.0, not Draco meshes. An optional convenience ZIP can be regenerated in scratch with `LII_ZIP=1 python3 tools/package_leonidas_ii.py`.
* Authoring source: `models/leonidas_ii/Aurelian_1889.blend`, metres, +X bow / +Y port / +Z baseline. Editable native 2K maps are packed and also supplied separately.
* Game GLB: **metres**, +Y up, −Z bow, −X port, amidships/load-waterline origin. Export formula is `(-y, z−6.5, -x)`. The installer derives the factor from a genuine 10 m marker separation. **Do not multiply mesh locations and sizes twice.** The final assembly is 0.28 m/stud: 592.857 studs LOA, 65.714 moulded beam, 23.214 design draught. Shell thickness slightly increases outer beam.
* Game geometry is regenerated at lower angular tessellation, with unchanged interface/berth dimensions; separate tiny shell rivet heads are omitted. No global decimation collapses table tops or floors. Regional kit images use 1K mip levels to reduce import/render memory; the original 2K maps remain supplied. All game nodes have at most 18,000 triangles and one material. This meets the *checked subset* of [Roblox's general mesh specification](https://create.roblox.com/docs/art/modeling/specifications), not automatic importer certification.
* Full game GLB can be regenerated in `exports/leonidas_ii/build/` by the exporter. It is large; the regional files are the practical import path. `build/` is scratch, intentionally not committed.

## Installation in an EMPTY TEST PLACE first

1. Save a new place. Set a water plane/terrain datum at Y=0 if desired. The installer deliberately does not overwrite Lighting, Terrain, ports, boats, global streaming settings or existing game systems.
2. Use Studio's **3D Importer** for each numbered `.glb` in the kit. Preserve object names and object separation; **do not merge all meshes**. Review texture import. Import the models, not a flattened single MeshPart. Import scale may be Studs or Metres: calibration corrects it. Do not auto-delete `CAL_Origin`, `CAL_Forward`, `CAL_Port`, `CAL_Up`.
3. Group ONLY the newly imported regional models into one **Model** named `Aurelian_Imported`. Each regional model must retain its own four calibration objects; its initial Studio placement can differ. Do not put a port, other boats or the control package inside this model.
4. Insert `Aurelian_Control_Package.rbxmx` into Workspace using **Insert from File**. This contains modules and disabled server/client templates, not a pre-uploaded mesh-ID model. There are no fabricated content IDs.
5. In the **EDIT-mode command bar**, run:

   ```lua
   require(workspace.Aurelian_Package.Aurelian_Install)(workspace.Aurelian_Imported, CFrame.new(0, 0, 0))
   ```

   The installer independently normalizes each regional import, removes calibration cubes, creates the waterline root, native collisions, ramps/guards, door/gangway colliders, actual seats, light and control locators. It welds passive parts to one anchored kinematic root and uses Motor6Ds for moving geometry. It clones the runtime to ServerScriptService and the local detail/light controller to StarterPlayerScripts.
6. If it asserts missing objects / calibration / movers, **stop**. Undo the installation or delete that imported copy and reimport with names preserved. Do not bypass assertions and call a malformed assembly verified. Re-running the installer against an installed model is intentionally rejected.
7. Disable legacy Aurelian controllers in this test place. The repository's seven legacy scripts remain untouched; importing them as well would create conflicting control owners.
8. Run the structural smoke test:

   ```lua
   require(workspace.Aurelian_Package.Aurelian_StudioAcceptance)(workspace.Aurelian)
   ```

   Save its output. Its checks are necessary, not sufficient. Play the route and motion tests below before accepting the ship.

If an importer version does not assign embedded PBR maps, upload the provided images under your own account/group and assign SurfaceAppearance maps to the matching materials. No credential or texture-ID injection is hidden in the installer. The maps use standard tangent-space normals and packed glTF roughness(G)/metalness(B); separate roughness and metalness maps are also provided for SurfaceAppearance. The Blender transmission glass is approximated by alpha PBR in GLB; review it in Studio.

## Controls and intended behaviour — implemented, not live-certified

| Location | Action | Contract |
|---|---|---|
| Bridge | Ahead / astern telegraph prompts | Nine signed orders; stop at centre; mooring/gangway interlock. |
| Engine flat | Regulator | 0 / 25 / 50 / 75 / 100%; separate from bridge order. |
| Stokehold | Firing-rate prompt | Changes simplified pressure supply, not a pressure-vessel simulation. |
| Electrical flat | Dynamo | Toggles local point-light supply; source emissive bulb pixels remain baked. |
| Bridge | Take helm | VehicleSeat steering; Q/R proximity fallbacks change requested rudder by five degrees. |
| Boarding stations | Ship/lower gangways | Both ship-owned hinged gangways; no port assets modified. Make fast before lowering. |
| Port entry | Cast off / make fast | Requires stopped ship/shaft and shipped gangways before departure. Boarding alone never clears moorings. |
| 196 compartment doors | Open / close prompts | Dimensional leaf and matching native collider move together; close is refused near an avatar. |
| Actual chair positions | Seats | Invisible native seats over the modeled cushions; no seat-per-book/detail-part collisions. |
| Bridge | Whistle | Steam/visual pulse. Optional authorised `WhistleSoundId` attribute; no unlicensed sound ID supplied. |

Expected departure: board → ship gangways → cast off → bridge ahead order → engine regulator / firing → steer. The signed shaft drives the three-throw crank, graduated crossheads/conrods, articulated eccentric links/valve spindles, tailshaft and pitched propeller. Rudder blade and steering quadrant share a pivot contract. Generator internals, steering pistons, windlass and davit falls are not full physical machinery simulations.

Server-only `Aurelian.ShipControl` BindableFunctions: `OrderTelegraph(orderName or signedStep -4..4)`, `SetRudder(deg)`, `SetMooringsClear(boolean)`, `GetSpeed()` (knots). There is no arbitrary client remote to set CFrames/RPM. Prompts check player liveness, distance and per-player rate on the server. Review authorization/crew roles for a production experience; currently nearby players may use controls.

## REQUIRED live acceptance sheet — all UNVERIFIED in this delivery

Record Studio version, device, avatar rig/scale, graphics level, client/server FPS and network statistics. Do not tick a box based on a Python result.

- [ ] Import every regional file; expected visual-node, mesh/material and native-part counts match `IMPORT_KIT_MANIFEST.json`.
- [ ] All PBR maps assigned, normal direction correct, no inside-out/reflected cabin geometry, no unexpected missing hull sections. Inspect both sides and underside.
- [ ] Board from real quay on both sides. Check the actual sloped gangway connection to a +4 m quay, interlocks, deployed/stowed colliders and safe transition through shell opening.
- [ ] Walk main → saloon → promenade → boat → bridge, fore/aft lower accommodation and BOTH after-orlop escapes. Enter every compartment/type; operate doors without wedging. Repeat with the intended largest avatar.
- [ ] Use both maintenance stair flights / return landings to the machinery flat; walk all three stokeholds, shaft alley, pump and dynamo flats and both engine working levels. Check upper-platform headroom and ladder openings.
- [ ] Open/close doors near a second character; no clipping, catapulting, wall penetration or collision ghosts.
- [ ] Sit/stand on moving ship. Carry standing passengers, jumping/landing and disembarking with two clients under network latency. Server carry is a prototype and needs particular attention.
- [ ] Ahead → stop → astern. Shaft RPM retains sign; crank/rod pins remain joined, valves travel correctly, propeller and shaft agree, rudder/helm/quadrant agree. Observe at slow RPM.
- [ ] Verify boilers/receiver/feed/exhaust/sea and steering connections visually. No claim of actual thermodynamic balance or pressure-vessel safety.
- [ ] Five minutes at berth and five minutes underway: no cumulative height drift, mooring/order glitches or script errors.
- [ ] Benchmark streaming and local detail/light culling from outside, cabin, dining and engine room on target hardware. No FPS target has been proven. The complete ship remains a substantial multi-million-triangle asset.
- [ ] External navigation collision/port interaction: the anchored-root controller is kinematic, not a hydrodynamic hull solver. It does not certify collision response to quays, grounding, turning basin, mooring lines or boat launch/hoist operations.

## Build / reproducibility

```bash
# Blender on PATH, or set BLENDER_BIN to its executable.
bash tools/build_leonidas_ii.sh
# The wrapper also runs the actual-shell/stern structural regression audit,
# regenerates GAME and packed channels, exports, packages and checks them.
# With an installed Luau interpreter/compiler and official Khronos package:
python3 tools/test_leonidas_runtime.py
node --expose-gc tools/validate_leonidas_gltf.cjs
# Create final real-model renders separately (serial Blender -> OIDN):
LII_SAMPLES=12 LII_AUDIT_SAMPLES=6 bash tools/render_leonidas_evidence.sh
python3 tools/make_leonidas_review.py
# Open/review the images and record exact hashes; gallery creation is NOT review.
python3 tools/check_leonidas_delivery.py --require-evidence --require-reviewed
```

Use the consolidated `tools/build_leonidas_ii.sh` for the complete ordered pipeline, including preparation of the packed map. Blender 4.2.3 was used; this constrained host needs its bundled shared libraries and only one Blender process at a time. The one-off `tools/leonidas_revision_fixes.py` is an audit artifact: **never rerun it as part of the build**.
