# HARBOUR INTEGRATION SPECIFICATION (PERICLES-II)

**Author:** PERICLES-II  
**Recipients:** LEONIDAS-II (*SS Aurelian*), THEMISTOCLES-II (Small Boats)  
**Datum Horizon:** 1889 British Maritime Operations  
**Date:** 2026-11-16  

---

## 1. Scale, Coordinate System and Global Datums

- **Roblox Conversion Factor:** `1 Roblox Stud = 0.28 metres` (`STUDS_PER_METRE = 3.57142857`).
- **Export Coordinate System:** Right-handed Cartesian: `+X` East, `+Y` North, `+Z` Up.
- **Reference Elevations:**
  - `WATER_Z = 0.0 m` (Mean Water Datum / 0.00 studs).
  - `HIGH_WATER_SPRINGS = +1.2 m` (+4.29 studs).
  - `LOW_WATER_SPRINGS = -1.2 m` (-4.29 studs).
  - `QUAY_Z = +4.0 m` (+14.29 studs above datum).
  - `RIVER_BED_Z = -11.0 m` (-39.29 studs).
  - `WET_DOCK_BED_Z = -9.0 m` (-32.14 studs).
  - `PRINCESS_DOCK_FLOOR_Z = -7.0 m` (-25.00 studs).
  - `PRINCESS_DOCK_SILL_Z = -4.5 m` (-16.07 studs).
  - `LANDING_STAGE_DECK_Z = +1.5 m` (+5.36 studs above current water surface, maintaining constant freeboard via pontoons).

---

## 2. Ocean Liner Integration (*SS Aurelian*)

### 2.1 Principal Dimensions Verification
From `interfaces/ship_spec.json`:
- Length Overall (`LOA`): `166.0 m` (592.86 studs).
- Length Waterline (`LWL`): `159.5 m`.
- Moulded Beam: `18.4 m` (65.71 studs).
- Design Draft: `6.5 m` (23.21 studs).
- Saloon Deck Height (Freeboard above baseline): `11.8 m` (giving `11.8 - 6.5 = 5.3 m` freeboard above waterline).
- Mast Heights above baseline: Fore `24.0 m`, Main `27.0 m`, Mizzen `21.0 m`.
- Funnel Top Height above baseline: `30.6 m`.

### 2.2 Passenger Terminal Berth (Port A — Berth A-B1, Prince's Landing Stage)
- **Berth Envelope:** `240.0 m` length × `26.0 m` clear width × `11.0 m` water depth.
- **Clearance Analysis:**
  - Fore/Aft Clearance: `(240.0 - 166.0) / 2 = 37.0 m` clear water beyond both stem and stern.
  - Under-Keel Clearance: `11.0 m depth - 6.5 m draft = 4.5 m` (16.07 studs) minimum water under keel at low water springs.
- **Mooring Layout:**
  - 12 heavy cast-iron bollards spaced at `20.0 m` intervals along the outer edge of the pontoon (`x = -80.0 m`).
  - Vessel secures with:
    - 2 bow head lines to bollards at `y = 230.0 m`.
    - 2 forward breast lines to bollards at `y = 190.0 m`.
    - 2 forward springs leading aft to bollards at `y = 130.0 m`.
    - 2 after springs leading forward to bollards at `y = 110.0 m`.
    - 2 after breast lines to bollards at `y = 70.0 m`.
    - 2 stern lines to bollards at `y = 30.0 m`.
- **Passenger Boarding Brow:**
  - Articulated timber-and-iron passenger brow positioned at `(-80.0, 130.0, 1.5)`.
  - Brow connects Landing Stage deck (`z = +1.5 m`) to *SS Aurelian*'s Saloon Deck side shell door (`z = +5.3 m`).
  - Vertical rise: `3.8 m` over `9.0 m` horizontal span (angle: `22.8°`), fitted with stepped non-slip treads and heavy canvas safety side curtains.

### 2.3 Shipbuilding & Overhaul Berths (Port B)
- **Fitting-Out Quay (Berth B-B1):**
  - Length: `210.0 m`, Depth: `10.0 m`.
  - Heavy Masting Equipment: 80-ton tubular sheer legs centered at `x = -30.0 m, y = 250.0 m`. Jib overhangs berth by `12.0 m` with a hook height of `32.0 m` above water, allowing boilers, machinery, and lower masts to be stepped into *SS Aurelian*.
- **Princess Graving Dock (Dry Dock):**
  - Coping dimensions: `244.0 m` length × `24.4 m` clear entrance width.
  - Floor width: `20.0 m`. Coping elevation: `+4.0 m`. Floor elevation: `-7.0 m`.
  - Fit Analysis for *SS Aurelian*:
    - Length: `244.0 m - 166.0 m = 78.0 m` longitudinal clearance (permitting full rudder and propeller removal astern).
    - Beam: `24.4 m - 18.4 m = 6.0 m` total clearance (`3.0 m` per side at waterline).
    - Sill Depth: `4.5 m` below water datum. High tide allows entry up to `8.5 m` draft, comfortably passing *SS Aurelian*'s `6.5 m` draft.
  - Centerline Keel Blocks: 160 oak keel blocks (`1.2 m` height × `1.0 m` width × `1.8 m` length) spaced at `1.2 m` centers along `x = 108.2 m`.

---

## 3. Small Boats Integration (Themistocles-II)

### 3.1 Vessel Dimensions & Drafts
- **Steam Cutter:** `LOA 7.62 m`, `Beam 2.28 m`, `Draft 0.53 m`, `Displacement 3532 kg`.
- **Rowing Cutter:** `LOA 7.915 m` (incl. rudder), `Beam 1.905 m`, `Draft 0.397 m`.
- **Whaler:** `LOA 8.23 m`, `Beam 1.829 m`, `Draft 0.436 m`.

### 3.2 Landing Stage Boat Steps (Port A — Berth A-B2)
- Located on the sheltered inner (eastern) side of the Prince's Landing Stage at `(-66.0, 44.0)`.
- Stepped granite slip from `z = +1.5 m` down to `z = +0.2 m` (water interaction level).
- Mooring cleats: Heavy cast bronze cleats spaced at `4.0 m` along the steps.
- Fendering: Heavy vertical oak timbers backed by coiled hemp rope fenders.

---

## 4. Architectural & Engineering Interfaces

- **Quay Wall Ladders:** Recessed cast-iron vertical rungs installed every `24.0 m` along all vertical masonry faces, from `z = -0.5 m` to `z = +4.0 m`, with forged hoop handgrips set into the granite coping stones.
- **Mooring Rings:** Flush forged-iron ring bolts set into wall recesses at `z = +1.85 m` (for small boats and lighters during tidal fluctuation).
- **Drainage & Scuppers:** Stone culverts and iron scuppers discharge at `z = +1.2 m`, maintaining dry quayside paving during torrential rainfall.
