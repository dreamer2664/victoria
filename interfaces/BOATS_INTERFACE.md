# Boat interface summary

**For the ship agent.** `interfaces/boats_spec.json` is the machine-readable
contract for the three ship's boats: overall dimensions, beam and hull depth,
davit/lifting attachment positions, cradle contact points, weight estimates,
boarding locations, and export origin and orientation. The figures are generated
from the same source as the 3D models (`boats/scripts/boatgen/specs.py`), so they
cannot drift from the geometry. If your boat-handling arrangement needs different
attachment points, change them here and re-run `boats/scripts/publish_spec.py`
so both sides agree.

Key figures: 1 stud = 0.28 m; +X forward, +Y port, Z = 0 at the **load waterline**, origin on the centreline at mid-LOA; GLB export is Y-up.

**Cross-project:** this file carries an `integration` block. It maps
the liner's craft ids onto these boat ids
(`cutter_steam_25` → `steam_cutter_1888`, `cutter_rowing_25` →
`rowing_cutter_25ft`), states the export contract (metres, 19 000
triangles per part, one UV layer, moving-part origins) and gives the
**davit rating each boat requires**. The liner's published davit limit
of 2000 kg cannot hoist the steam cutter, which weighs 3212 kg light and
3532 kg loaded; the rating table says so in numbers rather than leaving
the two specs to disagree quietly.

_(auto-generated — do not edit by hand)_

## 25 ft Steam Cutter (1888 pattern)  (`steam_cutter_1888`)

- LOA: 7.62 m / 25 ft 0 in
- Beam max: 2.134 m / 7 ft 0 in
- Depth moulded amidships: 1.203 m
- Draft light / loaded: 0.5 / 0.532 m
- Freeboard light / loaded: 0.703 / 0.671 m
- Weight light / loaded: 3212 / 3532 kg
- Davit slings at x = +2.05 m and -1.55 m (spread 3.6 m)
- Cradle points: x=+1.60 z=-0.51, x=-1.60 z=-0.51
- Boarding: x = +0.35 m, 0.677 m above the waterline
- Stowage envelope: 7.72 x 2.494 x 1.62 m above the sheer

## 25 ft Clinker Rowing Cutter (10-oared)  (`rowing_cutter_25ft`)

- LOA: 7.62 m / 25 ft 0 in
- Beam max: 1.905 m / 6 ft 3 in
- Depth moulded amidships: 1.065 m
- Draft light / loaded: 0.272 / 0.397 m
- Freeboard light / loaded: 0.794 / 0.668 m
- Weight light / loaded: 1017.0 / 1897.0 kg
- Davit slings at x = +1.95 m and -1.60 m (spread 3.55 m)
- Cradle points: x=+1.55 z=-0.38, x=-1.55 z=-0.38
- Boarding: x = +0.55 m, 0.675 m above the waterline
- Stowage envelope: 8.02 x 2.205 x 0.42 m above the sheer

## 27 ft Double-ended Clinker Whaler (c.1890)  (`whaler_27ft`)

- LOA: 8.23 m / 27 ft 0 in
- Beam max: 1.829 m / 6 ft 0 in
- Depth moulded amidships: 1.032 m
- Draft light / loaded: 0.346 / 0.436 m
- Freeboard light / loaded: 0.686 / 0.596 m
- Weight light / loaded: 1007.5 / 1487.5 kg
- Davit slings at x = +1.85 m and -1.85 m (spread 3.7 m)
- Cradle points: x=+1.60 z=-0.43, x=-1.60 z=-0.43
- Boarding: x = +0.70 m, 0.596 m above the waterline
- Stowage envelope: 8.58 x 2.129 x 4.4 m above the sheer
