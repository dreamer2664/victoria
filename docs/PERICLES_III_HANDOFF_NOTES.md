# PERICLES-III — Branch Review and Implementation Notes

**Review date:** 2026-11-18
**Repository:** `dreamer2664/victoria` (public branch snapshots cloned without credentials)
**Working branch:** `agent/pericles-iii`, based on `agent/pericles-ii`

## Branches reviewed

- `agent/ports` (`dbcc091fb20f4a3f53ab29b46a09055ca0e735f4`): first-generation port-construction baseline; current tree includes the architectural/industrial assets, generated layouts, interaction layer, historical-evidence/asset-license documentation, QA report, and exported GLBs/renders. The branch's own report identifies the datum burial, quay-axis, track-over-water, geometry, historical machinery, and Roblox runtime defects that Gen II was meant to fix.
- `agent/pericles-ii` (`ef8b6c6d40fdefbf29265fda898534746e14915b`): reconstruction and historical-realism pass, including vessels/clutter, expanded layouts, clearance/overlap inspection, existing Roblox berth/ship services, and the Generation-I inspection report. It documents known visual issues and the exact historical cut-off/evidence register.
- The attached `PERICLES_III_HANDOFF.md` was read in full. Its Gen-III mandate is tide, mechanical animation, caisson/drydock sequencing, Luau replication/interactions, effects, and NPCs.

## Reconciliation findings

The supplied handoff is useful direction, but it does not exactly describe the checked-out repository state. Resolve these before calling the world production-ready:

1. **The repository was not already in the workspace.** `/home/user/repo` did not exist. The public GitHub branches were cloned to `victoria-agent-ports` and `victoria-agent-pericles-ii`; no token was needed for reading them.
2. **Port A's historical basis conflicts across documents.** `HISTORICAL_EVIDENCE.md` and `docs/port_a_layout.md` describe Liverpool's enclosed dock as non-tidal and its impounded water as fixed. The new handoff asks for a tidal river landing stage and fixed impounded dock water. These can coexist if the tidal surface is only the outer river and the lock isolates the inner basin; do not tide the inner dock.
3. **Datum/range conflict:** the handoff mentions an 8.5 m Liverpool spring range and separately specifies the bridge's operational range as `-2.0 .. +3.5 m`. The runtime follows the explicit operational envelope for now; historical spring datums still need a single agreed reference before being widened.
4. **Gen-II pontoon deck mismatch:** `maritime.pontoon()` currently defaults to `+1.35 m`; the gangway is built to `+1.5 m`, and the interface documents `+1.5 m`. Gen-III rig attributes use `+1.5 m` to match the gangway, so the DCC baseline should be reconciled (prefer one shared constant and rebuild/audit).
5. **The current meshes are not animation rigs.** `A_ground` includes both land and water; the monolithic `A_gangway_bridge` contains fixed shore masonry and movable structure. They must be split into separate water surfaces, static abutments, moving spans, and roller bogies. The controller intentionally does not rotate the old combined bridge.
6. **Per-prototype GLB assets in the Pericles-II checkout need regeneration.** A binary audit found 127 of 129 per-port GLBs contain no mesh primitives (132-byte containers); only 2 contain meshes. The full-port GLB/FBX are populated. The likely cause is that prototype objects are exported while their whole collection is hidden. `build_ports.py` now temporarily unhides that collection and validates every modular and full-port GLB, but a Blender rebuild is still required to regenerate the assets. Do not assume the committed individual GLBs are usable.
7. **Counts in the handoff differ from the branch report.** The checked-in Pericles-II README/QC report state 61 Port A prototypes / 485 instances and 54 Port B / 356 instances; the handoff claims 82/74 prototypes and different totals. Use fresh build output as authority, not either stale count.
8. **The repository has no Rojo project file or `.rbxl` place.** Roblox Studio wiring/import/tagging and runtime tests remain manual. The working clone also has no Blender or Luau compiler in this environment, so Python mathematical tests are not a substitute for Studio validation.

## Gen-III work started

- Added `TideMath.luau` for a deterministic cosine tide curve, gangway pitch, and roller travel.
- Added server-authoritative `TidalController.luau`, started from `PortServer.server.luau`, publishing tide levels and updating tagged anchored assemblies at 10 Hz.
- Added `TidalClient.client.luau` for synchronized, smoothed `CFrame` interpolation on `RenderStepped`.
- Added `docs/TIDAL_SIMULATION.md` and the Roblox setup notes with required tags/attributes and the asset-splitting prerequisite.
- Added `tests/test_tide_math.py`; all five tests pass under Python's standard library.

## Credential handling

A personal access token was included in the conversation. It was **not** copied to files, shell history, or workspace. Treat it as exposed and revoke/rotate it in GitHub. Public read access was sufficient for branch review; publishing changes requires a fresh token via a proper secret manager or an enabled GitHub integration, not a checked-in or workspace plaintext file.
