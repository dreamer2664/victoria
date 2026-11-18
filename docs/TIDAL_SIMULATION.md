# Operation Victoria — Dynamic Tide and Landing-Stage Rig

**Status:** Gen-III Phase 1 implementation (runtime controllers + asset contract)
**Units:** Blender/world layout values in metres; Roblox transforms in studs
**Roblox scale:** 1 stud = 0.28 m (`Config.STUDS_PER_METRE`)

## Runtime behaviour

- The server starts `TidalController` from `PortServer.server.luau` and owns the authoritative tide clock and transforms. It samples on `Heartbeat` at 10 Hz.
- `TidalClient.client.luau` evaluates the same deterministic curve against Roblox's synchronized server clock and interpolates tagged visual assemblies on `RenderStepped`.
- Port A uses the explicit Gen-III operating envelope `-2.0 m .. +3.5 m`. Port B uses a `3.5 m` total range (`-1.75 m .. +1.75 m`). The shared default high-to-high cycle is 20 real minutes, a gameplay compression of a semidiurnal cycle; it is configurable in both runtime scripts.
- The Port A impounded basin is held at `+3.2 m`, independent of the river tide.
- Tide curves are cosine-eased between extrema. At the server epoch (startup) the curve begins at low water, reaches high water at half-period, and returns to low water at one period.

The handoff also cites a maximum Liverpool spring range of 8.5 m, while its articulated-bridge task specifies a narrower `[-2.0, +3.5] m` operating envelope. This implementation follows the task's explicit envelope so the landing-stage bridge and existing clearance assumptions remain within their design range. Do not treat it as the complete historical spring range without a datum reconciliation.

## Important Gen-II asset gap

The runtime controller is ready, but it cannot articulate the current monolithic exports by itself. In the checked-in Gen-II source, `A_ground` combines land and water meshes, and `A_gangway_bridge` combines fixed shore abutments with the moving span. Those GLBs must be split into independently transformable objects before the animation can be seen correctly:

1. Export the river and impounded dock water as separate surfaces; remove those water faces from the static land/ground mesh so a duplicate, unmoving water plane is not left underneath.
2. Put the entire landing-stage pontoon (including the booking-office superstructure) in a `Model` tagged `VictoriaTidalPontoon`.
3. Keep the granite shore abutments and hinge bearings static. Put each gangway's trussed span, canopy, and attached mid-span support in its own `Model` tagged `VictoriaTidalGangwaySpan`.
4. Split the roller bogies into separate small models tagged `VictoriaTidalGangwayBogie`, one per track, so they can translate on the pontoon's steel trackways while the span pitches.
5. Keep all assemblies' parts anchored; the controller uses `Model:PivotTo()` and does not rely on Roblox physics constraints for this large-scale motion.

Until that asset split is made and the tags/attributes below are assigned in Studio, the scripts safely run the replicated tide clock but have no articulated asset to move. Do not tag the old combined gangway prototype as a moving span: that would rotate the fixed abutments as well.

## CollectionService tags and attributes

| Tag | Instance | Required attributes | Effect |
|---|---|---|---|
| `VictoriaTidalWaterSurface` | Model or BasePart, separate mesh surface | `PortCode` (`"a"`/`"b"`), `WaterKind` (`"river"`/`"impounded"`), `WaterDatumM` (usually `0`) | River surfaces follow the tide. `impounded` surfaces use `WaterLevelM` (default `3.2`). |
| `VictoriaTidalPontoon` | Port A landing-stage Model | `PortCode="a"`, `ReferenceTideM=0` | Translates vertically by tide minus reference tide, retaining its freeboard. |
| `VictoriaTidalGangwaySpan` | One moving span Model per bridge | `PortCode="a"`, `ReferenceTideM=0`, `ShoreZ_M=4`, `PontoonDeckOffsetM=1.5`, `SpanLengthM=36`, `TideDirectionX=-1`, `HingeX_M=-30`, `HingeY_M=75` or `195`, `HingeZ_M=4` | Rotates about its shore trunnions as the pontoon rises/falls. |
| `VictoriaTidalGangwayBogie` | One roller-carriage Model per track | Same bridge attributes as the span | Follows the pontoon vertically and slides along the track by the span endpoint's horizontal kinematic offset. |

`PortCode` is used with `Config.toWorld()`, so Port B's 20,000-stud world offset is handled without baking global Roblox coordinates into the asset metadata. The server captures each unanimated transform in the `VictoriaTideBasePivot` CFrame attribute; do not author or update this attribute manually.

For the two Port A bridges, use the corresponding `HingeY_M` values (75 m and 195 m). The hinge is at Blender `(-30, y, +4)`; the pontoon end is toward Blender `-X`. The gangway pitch is calculated from the fixed hinge elevation and the pontoon deck elevation. The bogie's `TideDirectionX=-1` sign follows that same -X track direction.

## Installation

1. Put `TideMath` and `TidalController` under `ReplicatedStorage/Shared` with the existing `Config` module.
2. Keep the `TidalController.start()` call in `PortServer.server.luau` (already wired).
3. Put `TidalClient.client.luau` in `StarterPlayer/StarterPlayerScripts`.
4. Split and import the water, pontoon, moving gangway spans, and bogies as described above; tag and set attributes using CollectionService / Studio's Attributes panel.
5. Run a server session. Check `Workspace` attributes `VictoriaTideA_M`, `VictoriaTideB_M`, and `VictoriaTideEpoch`; the tide values should remain within the configured limits. Observe the client for smooth interpolation.

## Verification

The pure tide and kinematics equations are mirrored in `tests/test_tide_math.py` using only Python's standard library. Run:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover extrema, midpoint, period wraparound, safe angle changes over the operating envelope, and bogie slide direction/magnitude. Roblox Studio verification is still required after the tagged assemblies are imported; this repository does not include a `.rbxl` place or a Studio runtime harness.
