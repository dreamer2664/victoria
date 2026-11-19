# LEONIDAS-II static validation

**This is not Roblox Studio acceptance.**

## PASS — All planned compartments have an explicit inventory
203

## PASS — Unique object names
1437

## PASS — UV0 on every source mesh
[]

## PASS — Finite source bounds with positive extent on each axis
Post-build object bounding boxes; not a positive signed-volume proof

## PASS — Compartment rectangles do not overlap
[]

## PASS — Stair escape footprints clear of cabin walls
[]

## PASS — Fixture geometry fits compartment envelope (100mm tolerance)
[]

## PASS — No substantial furniture-pair AABB overlap suspects
[]

## INFO — Built passenger and crew berths counted separately
{"mesh_objects": 1437, "triangles": 4341224, "physical_compartments": 203, "actual_first_berths": 228, "actual_second_berths": 132, "actual_third_berths": 268, "actual_crew_berths": 117}

## PASS — Main conrod pin-to-crosshead distance over 2163 poses
8.881784197001252e-16

## PASS — Roblox axis transform / scale
{"loa_studs": 592.8571428571428, "beam_studs": 65.71428571428571, "forward": "-Z", "port": "-X", "up": "+Y", "load_waterline_y": 0}

## PASS — Propeller tip vs counter vertical clearance
0.628

## INFO — Kinematic target knots at nominal RPM
19.295

## PASS — Actual-collider local doorway passability, all doors open
[]

## INFO — Doorway joins deck largest walk component
[{"id": "O_ThirdAP", "deck": "orlop", "inside_clear": true, "outside_clear": true, "same_component": true, "on_largest_component": false, "inside": [-60.5, 2.52], "outside": [-60.5, 3.48], "component": 4}, {"id": "O_ThirdAS", "deck": "orlop", "inside_clear": true, "outside_clear": true, "same_component": true, "on_largest_component": false, "inside": [-60.5, -2.52], "outside": [-60.5, -3.48], "component": 3}, {"id": "O_CrewP", "deck": "orlop", "inside_clear": true, "outside_clear": true, "same_component": true, "on_largest_component": false, "inside": [-41.5, 4.619999999999999], "outside": [-41.5, 5.58], "component": 4}, {"id": "O_CrewS", "deck": "orlop", "inside_clear": true, "outside_clear": true, "same_component": true, "on_largest_component": false, "inside": [-41.5, -4.619999999999999], "outside": [-41.5, -5.58], "component": 3}, {"id": "L_ThirdWomen", "deck": "lower", "inside_clear": true, "outside_clear": true, "same_component": true, "on_largest_component": false, "inside": [48.52, 0.0], "outside": [49.48, 0.0], "component": 10}, {"id": "L_ThirdMen", "deck": "lower", "inside_clear": true, "outside_clear": true, "same_component": true, "on_largest_component": false, "inside": [49.879999999999995, 0.0], "outside": [48.92, 0.0], "component": 10}, {"id": "L_ThirdWash", "deck": "lower", "inside_clear": true, "outside_clear": true, "same_component": true, "on_largest_component": false, "inside": [63.879999999999995, 0.0], "outside": [62.92, 0.0], "component": 10}, {"id": "L_ThirdMess", "deck": "lower", "inside_clear": true, "outside_clear": true, "same_component": true, "on_largest_component": false, "inside": [70.78, 0.0], "outside": [69.82, 0.0], "component": 10}]

## PASS — Multideck component reachability from boarding landing
{"unreachable": [], "stair_endpoints": [{"id": "Grand_Main", "from_component": ["main", 1], "to_component": ["saloon", 2]}, {"id": "Grand_Upper", "from_component": ["saloon", 2], "to_component": ["promenade", 1]}, {"id": "Prom_To_Boat", "from_component": ["promenade", 1], "to_component": ["boat", 1]}, {"id": "Forward_Lower", "from_component": ["lower", 10], "to_component": ["main", 1]}, {"id": "Forward_Orlop", "from_component": ["orlop", 8], "to_component": ["lower", 10]}, {"id": "After_Lower", "from_component": ["lower", 3], "to_component": ["main", 1]}, {"id": "After_Orlop", "from_component": ["orlop", 4], "to_component": ["lower", 3]}, {"id": "After_Orlop_Starboard", "from_component": ["orlop", 3], "to_component": ["lower", 3]}, {"id": "After_Upper", "from_component": ["main", 1], "to_component": ["saloon", 2]}, {"id": "After_Promenade", "from_component": ["saloon", 2], "to_component": ["promenade", 1]}, {"id": "Engine_Access", "from_component": ["machinery", 1], "to_component": ["lower", 3]}, {"id": "Engine_Main", "from_component": ["lower", 3], "to_component": ["main", 1]}, {"id": "Bridge_Access", "from_component": ["boat", 1], "to_component": ["bridge", 1]}], "assumption": "nearest .4m endpoint; separate stair headroom test below"}

## PASS — Machinery service-aisle anchors reachable from boarding
[{"aisle": "Engine_Port", "component": ["machinery", 1], "reachable": true}, {"aisle": "Engine_Starboard", "component": ["machinery", 1], "reachable": true}, {"aisle": "After_Stokehold", "component": ["machinery", 1], "reachable": true}, {"aisle": "Middle_Stokehold", "component": ["machinery", 1], "reachable": true}, {"aisle": "Forward_Stokehold", "component": ["machinery", 1], "reachable": true}, {"aisle": "Dynamo_Aisle", "component": ["machinery", 1], "reachable": true}, {"aisle": "Pump_Aisle", "component": ["machinery", 1], "reachable": true}, {"aisle": "Shaft_Alley_Port", "component": ["machinery", 1], "reachable": true}, {"aisle": "Shaft_Alley_Starboard", "component": ["machinery", 1], "reachable": true}]

## PASS — Cooking furnace fronts face reachable working aisles
[{"room": "S_Galley", "range_faces_working_aisle": true, "firing_position": [-37.0, -2.9], "reachable": true}, {"room": "S_Bakery", "range_faces_working_aisle": true, "firing_position": [-37.0, 3.05], "reachable": true}]

## PASS — Stair sampled avatar head/body envelope
[{"id": "Grand_Main", "blocked_by": []}, {"id": "Grand_Upper", "blocked_by": []}, {"id": "Prom_To_Boat", "blocked_by": []}, {"id": "Forward_Lower", "blocked_by": []}, {"id": "Forward_Orlop", "blocked_by": []}, {"id": "After_Lower", "blocked_by": []}, {"id": "After_Orlop", "blocked_by": []}, {"id": "After_Orlop_Starboard", "blocked_by": []}, {"id": "After_Upper", "blocked_by": []}, {"id": "After_Promenade", "blocked_by": []}, {"id": "Engine_Access", "blocked_by": []}, {"id": "Engine_Main", "blocked_by": []}, {"id": "Bridge_Access", "blocked_by": []}, {"id": "EngineLadder_575", "blocked_by": []}, {"id": "EngineLadder_576", "blocked_by": []}, {"id": "EngineLadder_577", "blocked_by": []}, {"id": "EngineLadder_578", "blocked_by": []}]

## PASS — Game export regenerated from current master
05fcdf10d429f83bd5e671b27e026d5c577e90a6e44f20c26750e9e3e069a526

## PASS — Game mesh node <=18000 triangles / finite UV0 / closed components
{"mesh_nodes": 1461, "unique_meshes": 1160, "placed_triangles": 3199238, "unique_triangles": 3101586, "reused_nodes": 301, "max_node_triangles": 18000, "removed_zero_area_triangles": 0, "calibration_nodes": 4, "storage_meshes_including_calibration": 1161, "corrected_shading_corners": 11169, "source_precision_vertices": 57}

## PASS — All actual mover / door names exist in the game export
[]

## PASS — Master/GAME interfaces and collider-envelope tolerance
{"interface_arrays_equal": true, "colliders_master": 4040, "colliders_game": 4040, "max_fixture_delta_m": 0.0219, "nonconforming": [], "runtime_uses": "master proxies, not lower-detail bounding boxes"}

## UNVERIFIED — Roblox Studio live acceptance
No Roblox Studio in this workspace. Static collider graph does not certify avatar headroom on slopes, moving passengers, imported collisions, multiplayer security or frame time.
