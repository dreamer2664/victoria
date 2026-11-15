# ROBLOX SETUP

How to get both ports from this repository into a working Roblox place.

---

## 1. The scale rule

> **1 Roblox stud = 0.28 m.** Therefore **1 m = 3.571428… studs.**

The Blender source is modelled natively in metres and every exported file is in metres.
You convert **once**, on import, and never again. If a dimension matters, take it from
`docs/port_<x>_meta.json` or the layout spec, which are authoritative, rather than
measuring the imported mesh.

| Metres | Studs |
|---|---|
| 0.28 | 1 |
| 1 | 3.571 |
| 4 (quay coping above water) | 14.29 |
| 20 (liner beam) | 71.43 |
| 24.4 (Princess Dock width, 80 ft) | 87.14 |
| 180 (liner length) | 642.86 |
| 243.8 (Princess Dock length, 800 ft) | 870.71 |

A player is ~5 studs tall in Roblox; a 4 m quay wall is 14.3 studs — about three player
heights, which is roughly right for standing on a Victorian quay coping.

---

## 2. Importing the geometry

Two routes. Use the second for anything you intend to ship.

### 2.1 Whole port (for looking at, not for shipping)

1. **Avatar → Import 3D** in Studio, choose `assets/glb/a/port_a_full.glb`.
2. Scale the imported model by **3.5714** uniformly. Do not use Freeform scaling.
3. Anchor everything. Move it to the position you want — the model's origin is the
   Blender origin, which is the river's edge at mean water level.

This produces one large mesh. Fine for a visual check or a background skybox object;
bad for a playable place, because you cannot cull or collide it sensibly.

### 2.2 Per-prototype kit (for a playable place)

1. Import every GLB in `assets/glb/a/` (one per prototype: `A_warehouse_3.glb`,
   `A_station.glb`, …) into `ReplicatedStorage.PortKit`.
2. For each, set `MeshPart` size to the exported size × 3.5714, and anchor it.
3. Place instances using the transforms in the metadata. The pattern:

```lua
local Config   = require(ReplicatedStorage.Shared.Config)
local LayoutA  = require(ReplicatedStorage.Shared.PortLayoutA)
local Kit      = ReplicatedStorage.PortKit

local function place(portCode, protoName, x, y, z, rz)
    local src = Kit[protoName]
    assert(src, "missing prototype " .. protoName)
    local m = src:Clone()
    m.Name = protoName
    m:SetPrimaryPartCFrame(
        CFrame.new(Config.toWorld(portCode, x, y, z)) * CFrame.Angles(0, math.rad(rz), 0)
    )
    m.Parent = workspace.Ports
    return m
end
```

`Config.toWorld` already applies the stud conversion and the Z-up → Y-up swap, so the
numbers you feed it are the same metres that appear in Blender and in the plan.

### 2.3 FBX

`assets/fbx/<port>/port_<x>_full.fbx` is provided for anyone on the older FBX import
path. It is exported with `FBX_SCALE_NONE`, forward −Z, up Y. It will import at metres;
apply the same 3.5714 scale.

---

## 3. Placing the two ports

They are separate places in the world already — `Config.PORTS.B.originStuds` puts Port B
20,000 studs east of Port A, far enough that neither sees the other's boundary.

---

## 4. Collision

The exported meshes are **render geometry**. Do not enable
`CollisionFidelity.Precise` on them; the ships' worth of small parts in a transit shed
will cost far more than it is worth.

Recommended approach — build collision from the plan:

| Element | Collision |
|---|---|
| Quay surface | one `Part` per berth apron, top at coping (z = +4 m = 14.29 studs) |
| Quay edge | an invisible wall 14.29 studs tall along each water edge, `CanCollide = true` |
| Buildings | one `Part` per footprint rectangle from `docs/port_<x>_layout.md` |
| Cranes / staithes / coaling hoists | a single box collider around the base |
| Bollards, lamps, capstans | **no collision** — you must be able to walk past them |

The footprints are already a list: `LayoutAuditor.items` in the build prints them, and
the layout docs tabulate them. They are rectangles in plan, which is exactly what a box
collider wants.

---

## 5. Wiring the gameplay layer

### 5.1 File placement

```
ReplicatedStorage/
  Shared/
    Config            (Config.luau)
    PortLayoutA       (PortLayoutA.luau, generated)
    PortLayoutB       (PortLayoutB.luau, generated)
    PortService       (PortService.luau)
    ShipService       (ShipService.luau)
    Mooring           (Mooring.luau)
  PortKit/            imported per-prototype MeshParts
ServerScriptService/
  PortServer          (PortServer.server.luau, as a Script)
StarterPlayer/StarterPlayerScripts/
  PortClient          (PortClient.client.luau, as a LocalScript)
```

Note: `PortClient` currently creates its own `PortNotice` RemoteEvent under PlayerGui
as a prototype convenience. For a live place, move that RemoteEvent to
`ReplicatedStorage/PortNotice` and have `PortServer` fire it — the server-side
`notify()` in `PortServer.server.luau` already looks for it.

### 5.2 The interaction model

`PortService.build` walks the generated layout and creates one invisible,
non-collidable Part per interaction point, each carrying a `ProximityPrompt` and three
attributes:

- `PortCode` — `"a"` or `"b"`
- `InteractionId` — e.g. `A-I1`
- `InteractionKind` — e.g. `ticket_purchase`, `gangway`, `mooring`

Because the kind is an attribute, systems can bind generically:

```lua
for _, part in CollectionService:GetTagged("PortInteraction") do
    if part:GetAttribute("InteractionKind") == "gangway" then
        -- ...
    end
end
```

### 5.3 The passenger flow

The terminal is a sequence, and the boarding gate enforces it:

```
Booking office  →  Customs  →  Gangway  →  ship
 (ticket_purchase)  (customs)   (gangway)
```

`ShipService.canBoard()` refuses boarding unless **all** of: a ticket is held, customs
have cleared you, the berth state is `Working`, and a gangway is shipped. Failing any
one gives a specific message rather than a generic refusal.

### 5.4 The ship cycle

```lua
local ShipService = require(ReplicatedStorage.Shared.ShipService)

-- somewhere on the server
local shipModel = ReplicatedStorage.ShipTemplates.Liner:Clone()
shipModel.Parent = workspace.Ships
ShipService.requestArrival("A-B1", shipModel)   -- Idle -> Approaching
ShipService.beginBerthing("A-B1")               -- -> Berthing
-- each mooring prompt fires ShipService.addMooringLine(); when the required
-- number is fast the berth becomes Moored
ShipService.connectGangway("A-B1", true)        -- -> Working
```

Turnaround is timed from the research: about 29 hours for a passenger berth, about
4.5 days for a coaling cargo berth. Those constants are in `ShipService.registerPort`
and are meant to be compressed for play — they are written as
`29 * 3600 / 60` precisely so the compression factor is obvious.

### 5.5 Mooring

`Mooring.DEFAULT_LINES` gives six lines — two head, two stern, two springs — with a
fraction along the hull and an offset from the berth centreline. `Mooring.makeLine`
creates a `RopeConstraint` from a ship cleat to a quay bollard. Nothing is welded to a
moving ship.

The gangway is a real model with a walkable deck and screens; it is tilted to the
difference in freeboard between quay and ship:

```lua
local gangway = Mooring.shipGangway(quayPart, shipPart, 12, 0.6)
gangway.Parent = workspace.Ports
```

---

## 6. What is not implemented

- Ship models. The brief forbids downloaded ship assets and hand-building a hull was
  out of scope; `ShipService` takes any `Model` with a `PrimaryPart` and an optional
  `BoardingPoint` BasePart.
- Cargo palletising / physics. `cargo` prompts exist and fire; they do not move crates.
- Interior lighting rigs.
- Any `.rbxl` place file — everything here is a source kit plus instructions, which is
  what the brief asked for.
