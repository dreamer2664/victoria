# Generation 2 Verified Renders (RENDERS-GEN-2)

This directory contains the Generation 2 renders for both **Port A** (Aldermouth Liner Terminal & Trafalgar Dock) and **Port B** (Carrickmore Shipbuilding Yard & Graving Docks).

All 19 renders reflect the complete visual inspection, geometry audits, architectural anchoring, and material calibrations conducted in Generation II.

---

## Defects Audited & Fixed in Generation 2

1. **Floating Puddle Elimination (Port B `07_roofscape` & `09_dry_dock_altars`)**:
   - *Issue*: A flat puddle plane (`B_puddle.002`) was placed at `(100, 100, 4.0)`, directly hovering mid-air over the excavated chamber of the Princess Graving Dock ($Z \in [-7.0, 4.0]$).
   - *Fix*: Removed invalid coordinates over open excavations and repositioned surface puddles onto solid ground apron setts. Both `07_roofscape` and `09_dry_dock_altars` now display clean, unobstructed views of the stepped granite altars, keel blocks, and timber shoring props.

2. **Floating Sky Timber Planks (Port B `03_street` & `05_slipways`)**:
   - *Issue*: Timber stacks placed at `(60, 250, 4.0)` coincided with the open declined cavity of Slipway No. 3, appearing from street cameras as disconnected wooden planks floating in the sky.
   - *Fix*: Relocated timber stacks to solid ground at `(80, 280)` in the timber storage yard.

3. **Accumulator Tower & Railway Collision (Port A `04_dockside` & `10_accumulator_tower`)**:
   - *Issue*: Jesse Hartley's hydraulic accumulator tower was positioned at `(24, -52)`, directly on the path of the quayside railway line (`y = -52.0`), causing tracks to clip straight through the brick plinth and obstructing 60% of the working quay view in `04_dockside`.
   - *Fix*: Shifted accumulator tower inland to `(24, -34)`, placing it behind the quayside railway corridor where a dock hydraulic engine house historically belongs. Quayside trackage now runs unobstructed for the full 200 m length of the North Quay, and camera `10_accumulator_tower` captures the complete monumental tower, stringcourses, quoins, water tank, and surrounding dock architecture.

4. **Camera Framing & Obstruction Fixes**:
   - *Port B `08_sheer_legs`*: Repositioned camera from `(-48, 250, 16)` inside the sheer legs truss to `(-56.0, 220.0, 8.5)` looking at `(-20.0, 280.0, 16.0)` (38 mm lens), yielding a clean, dramatic framing of the 80-ton tubular sheer legs, guy stays, fitting-out wharf, and harbour lighthouse.
   - *Port A `07_roofscape`*: Shifted camera from `(30, -140, 58)` to `(60.0, -110.0, 50.0)` looking down the main warehouse and station spine `(125.0, 80.0, 14.0)` at 52 mm, eliminating distant river boundary corner clipping and framing the entire Victorian roofscape, monitors, and arched train shed.

5. **River Water Plane & Horizon Continuity (Port A & B `01_aerial`, `02_waterfront`, `05_landing_stage`)**:
   - *Issue*: River geometry previously ended at 1200 m, creating a visible water boundary line against the sky at extreme distances.
   - *Fix*: Expanded river water geometry to $8000 \times 4000\text{ m}$ spanning $X \in [-4000, -30]$ and $Y \in [-4000, 4000]$ with an 80 m grid step. Camera `clip_end` was extended to $10,000\text{ m}$, ensuring natural blending with the physical Nishita sky horizon with zero clipping edges. All prototypes remain strictly under the Roblox 20,000-triangle limit (`A_ground`: 18,418 tris, `B_ground`: 18,286 tris).

6. **Watertight Solid Roofs & Grounded Bridges**:
   - All roofs feature solid Welsh slate, closed triangular masonry gables, solid ridge caps, and raised clerestory monitors.
   - Swing bridge rests upon a 6.8 m cylindrical granite pivot pier founded in the lock channel bed.
   - Articulated landing stage gangway bridges connect from massive granite shore abutment pylons with pillow blocks across intermediate floating bents to roller carriages on the pontoon deck.

---

## Directory Layout

Each render is available in two naming schemes:
- In subdirectories: `port_a/<camera>.png` and `port_b/<camera>.png`
- Flat in root: `port_<port>_<camera>.png`

---

## Port A: Aldermouth Liner Terminal (10 Cameras)

| File | Camera | Focal | Description |
|---|---|---|---|
| `port_a_01_aerial.png` | `01_aerial` | 40 mm | Comprehensive high-altitude overview of terminal, floating stage, lock entrance, and Trafalgar Basin. |
| `port_a_02_waterfront.png` | `02_waterfront` | 46 mm | Mersey frontage showing the floating landing stage, articulated bridges, and terminal facade. |
| `port_a_03_street.png` | `03_street` | 38 mm | Cobblestone streetscape flanked by classical passenger terminal and pedimented office block row. |
| `port_a_04_dockside.png` | `04_dockside` | 40 mm | Unobstructed working quayside view along North Quay with railway track, mineral wagons, and portal cranes. |
| `port_a_05_landing_stage.png` | `05_landing_stage` | 42 mm | Prince's Landing Stage floating pontoon with articulated bowstring lattice gangway bridges and mooring booms. |
| `port_a_06_dock_basin.png` | `06_dock_basin` | 42 mm | Impounded Trafalgar Dock basin with realistic estuary water reflections, Armstrong hydraulic portal cranes, and lock gates. |
| `port_a_07_roofscape.png` | `07_roofscape` | 52 mm | Roofscape showing curved slate barrel vault train shed, raised clerestory monitors, and warehouse gables. |
| `port_a_08_terminal_court.png` | `08_terminal_court` | 38 mm | Forecourt of Baggage Hall and Custom House with yellow stock brick, cornices, and dray wagons. |
| `port_a_09_swing_bridge.png` | `09_swing_bridge` | 45 mm | Wrought-iron bowstring lattice swing bridge resting on cylindrical granite pivot pier over lock channel. |
| `port_a_10_accumulator_tower.png` | `10_accumulator_tower` | 38 mm | Italianate hydraulic accumulator tower in red terracotta brick with ashlar stone quoins and water tank. |

---

## Port B: Carrickmore Shipbuilding Yard (9 Cameras)

| File | Camera | Focal | Description |
|---|---|---|---|
| `port_b_01_aerial.png` | `01_aerial` | 40 mm | Complete yard overview: 3 building slips, 2 graving docks, platers' sheds, boiler shop, and fitting wharf. |
| `port_b_02_waterfront.png` | `02_waterfront` | 45 mm | River frontage showing slipway launching ways, timber piling, and fitting-out quay wall. |
| `port_b_03_street.png` | `03_street` | 40 mm | Shipbuilding yard street with worker terrace cottages, yard pub, gatehouse, and cobblestone roadway. |
| `port_b_04_graving_dock.png` | `04_graving_dock` | 42 mm | Looking along Princess Graving Dock: granite stepped altars, keel blocks, shoring props, and caisson gates. |
| `port_b_05_slipways.png` | `05_slipways` | 40 mm | Declivity of building slipways showing timber groundways, sliding ways, and retaining side walls. |
| `port_b_06_shops.png` | `06_shops` | 42 mm | Heavy industrial machine shops, multi-pane factory sash windows, and sawtooth north-light gables. |
| `port_b_07_roofscape.png` | `07_roofscape` | 45 mm | Shipyard industrial roofscape showing moulding loft, boiler shop, engine works, and masonry chimney stacks. |
| `port_b_08_sheer_legs.png` | `08_sheer_legs` | 38 mm | Day, Summers & Co. 80-ton tubular masting sheer legs on the fitting-out wharf beside the lighthouse. |
| `port_b_09_dry_dock_altars.png` | `09_dry_dock_altars` | 40 mm | Low-angle view inside the dry dock showing 6-tier granite altars, access stairs, slide chutes, and keel blocks. |
