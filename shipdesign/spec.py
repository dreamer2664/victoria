"""MASTER DIMENSION SPECIFICATION for SS *Aurelian* (fictional, 1889).

Every number used by every generator script and every Blender module in this
repository is derived from this file or from hull.py, which is itself driven by
SHIP below.  Nothing is eyeballed at modelling time.

COORDINATE SYSTEM (Blender, metres, real world scale)
----------------------------------------------------
  X : longitudinal, +X = forward (bow), 0 = amidships (L/2 from each end)
  Y : transverse, +Y = port.  0 = centreline
  Z : vertical, +Z up, 0 = base line (top of keel plate)
  Waterline at load draught : z = 7.00

Historical anchors for these numbers are listed in DIMENSION_MANIFEST.json and
in research/HISTORICAL_EVIDENCE.md.  Summary of the comparative set used
(all late-1880s British twin-screw liners):

    ship            built  L(ft)   B(ft)  draft  gross t   IHP     knots
    Umbria/Etruria   1884   501    57.2   23.5   7,718     14,320  19.6
    City of Paris    1888   527    63.0   ~26   10,499     20,100  20.0
    Teutonic         1889   565    57.7   26.0   9,984     17,500  20.2
    Majestic         1889   565    57.6   26.0   9,861     17,000  20.1
    (Aurelian)       1889   166 m  18.4 m  7.1    ~8,600   14,000  19.3
"""

from math import pi

# --------------------------------------------------------------------------
# 1. PRINCIPAL DIMENSIONS
# --------------------------------------------------------------------------
SHIP = {
    "name": "Aurelian",
    "prefix": "SS",                       # single-screw merchant steamer
    "company": "Albion & Western Steam Navigation Co., Liverpool",
    "company_short": "Albion & Western",
    "flag": "British",
    "port_of_registry": "Liverpool",
    "yard": "Birkenhead Iron Works & Shipbuilding Co., Birkenhead",
    "yard_number": 147,
    "designed_by": "A. R. Fenwick, M.I.N.A.",
    "laid_down": "November 1887",
    "launched": "14 March 1889",
    "completed": "20 June 1889",
    "service": "Liverpool - Queenstown - New York (fortnightly)",
    "year": 1889,

    # --- hull form ---------------------------------------------------------
    "loa": 166.0,          # length overall, stem to counter transom
    "lwl": 159.5,          # length on load waterline
    "lbp": 158.0,          # length between perpendiculars
    "beam": 18.4,          # moulded breadth
    "beam_max": 18.4,
    "depth_moulded": 11.80, # keel plate top to upper (strength) deck, amidships
    "depth_main_deck": 8.80,
    "depth_saloon_deck": 11.80,
    "depth_promenade": 14.40,
    "depth_boat_deck": 16.60,
    "freeboard_main": 2.30,          # main (tween) deck side
    "freeboard_upper_deck": 5.30,  # upper/saloon deck side, the freeboard deck
    "draft": 6.50,         # load draught, base line -> waterline (21 ft 4 in)
    "freeboard_upper": 5.30,   # promenade deck side above water
    "block_coef": 0.695,   # Cb at load draught
    "midship_coef": 0.972,
    "prismatic_coef": 0.720,
    "waterplane_coef": 0.815,
    "lcb_pct_fwd_midship": 1.6,   # % of LWL, forward of midships
    "entrance_half_angle_deg": 18.0,
    "run_half_angle_deg": 22.0,

    # --- tonnage / capacity ------------------------------------------------
    "gross_register_est": 8480,   # Thames measurement on enclosed spaces
    "net_register_est": 4720,
    "displacement_t": 13600,      # at load draught 6.50 m, salt water
    "lightship_t": 9950,
    "deadweight_t": 4750,
    "cargo_capacity_t": 2600,     # general cargo in fore/after holds
    "coal_capacity_t": 1450,      # bunkers, 13 days at 19.3 kn + reserve
    "coal_consumption_tpd": 108,  # at 19.3 kn service, ~1.55 lb/IHP/hr
    "fresh_water_t": 320,
    "ballast_t": 380,

    # --- accommodation -----------------------------------------------------
    "passengers": {"first": 228, "second": 132, "third": 720, "total": 1080},
    "crew": {"deck": 46, "engine_room": 62, "stewards_catering": 88, "total": 196},
    "berths_third_total": 720,

    # --- machinery ---------------------------------------------------------
    "propulsion": "single screw, 4-bladed manganese-bronze propeller",
    "engines": "one set vertical inverted direct-acting triple-expansion,"
               " surface-condensing, 3 cranks at 120 deg",
    "cylinder_dia_m": (0.965, 1.575, 2.565),   # 38 in, 62 in, 101 in
    "stroke_m": 1.295,                          # 51 in
    "engine_ihp": 14000,
    "engine_rpm": 62,
    "boilers": "9 cylindrical single-ended return-tube, 4 furnaces each",
    "boiler_dia_m": 4.20,
    "boiler_length_m": 3.35,
    "boiler_pressure_bar": 11.0,               # 160 lb/in2
    "boiler_rows": 3,
    "boilers_per_row": 3,
    "condensers": 2,
    "funnels": 2,
    "funnel_dia_m": 3.60,
    "funnel_height_above_deck_m": 17.5,
    "funnel_spacing_m": 24.0,
    "masts": 3,
    "mast_positions_x_m": (70.0, 2.0, -62.0),  # fore, main, mizzen
    "service_speed_kn": 19.3,
    "max_speed_kn": 20.2,
    "prop_diameter_m": 5.30,
    "prop_pitch_m": 6.90,
    "prop_blades": 4,
    "shaft_dia_m": 0.46,
    "rudder_area_m2": 17.0,

    # --- structure ---------------------------------------------------------
    "frame_spacing_m": 0.9144,    # 3 ft frames, H&W standard practice
    "num_frames": 173,
    "bulkheads": 11,              # 10 watertight + 1 collision
    "double_bottom_height_m": 1.30,
    "shell_plate_thickness_mm": 19.0,  # amidships, tapering to 13 fwd/aft
    "keel_plate_width_m": 1.22,
    "keel_plate_thickness_mm": 25.0,
    "rivet_pitch_m": 0.089,
    "rivet_dia_m": 0.022,
    "strake_height_m": 1.83,     # 6 ft plates, standard rolling width
}

# --------------------------------------------------------------------------
# 2. DECK SCHEDULE  (z = top of deck plating at side, amidships)
# --------------------------------------------------------------------------
# Victorian liners of this generation: 5 continuous decks + 2 partial.
from .layout import DECKS, DECK_Z, DECK_EXT, DECK_NAME, SHEER_MID, SHEER_BOW, SHEER_STERN, BULKHEADS

DECK_PLATE_T = 0.0105
BULWARK_H = 1.15
BULWARK_T = 0.012
RAIL_H = 1.07
STANCHION_SPACING = 1.524

# --------------------------------------------------------------------------
# 3. LONGITUDINAL ZONES  (x in metres, +forward)
# --------------------------------------------------------------------------
ZONES = {
    "collision_bh": 72.0,        # collision bulkhead aft face
    "fore_hold": (38.0, 72.0),
    "boiler_room_fwd_bh": 31.0,
    "boiler_room": (-4.0, 40.0),
    "engine_room_fwd_bh": -6.0,
    "engine_room": (-27.0, -6.0),
    "tunnel_aft_bh": -27.0,
    "shaft_alley": (-62.0, -27.0),
    "steering_gear": (-74.0, -62.0),
    "after_hold": (-76.0, -30.0),
    "grand_stair": (-0.0, 12.0),      # x range of stairwell

    # public rooms, first class (top deck of each room)
    "dining_saloon": (-52.0, -14.0),   # main deck
    "dining_gallery": (-50.0, -16.0),  # saloon deck (open gallery over saloon)
    "library": (-6.0, 14.0),           # promenade deck
    "music_room": (16.0, 30.0),        # promenade deck
    "smoking_room_1c": (-34.0, -18.0), # promenade deck, port side aft
    "barber": (-40.0, -34.0),
    "ladies_drawing": (-16.0, -6.0),   # promenade deck, stbd
    "smoking_room_2c": (-66.0, -54.0), # promenade deck, aft house
    "dining_2c": (-64.0, -50.0),       # upper deck, aft house
    "third_berths_fwd": (38.0, 70.0),  # lower deck, bow
    "third_berths_aft": (-76.0, -58.0),# lower deck, stern
    "third_dining": (-50.0, -30.0),    # main deck after
    "galley": (-72.0, -56.0),          # upper deck, aft of dining saloon (port)
    "pantry": (-56.0, -48.0),
    "hospital": (56.0, 64.0),          # promenade deck, fwd, stbd
    "captain_cabin": (24.0, 30.0),     # boat deck fwd of bridge
    "chart_room": (30.0, 35.0),        # bridge deck aft of wheelhouse
    "officers_1": (14.0, 24.0),
    "crew_fwd": (44.0, 58.0),          # upper deck forecastle area
}

# --------------------------------------------------------------------------
# 4. FUNNEL / MAST
# --------------------------------------------------------------------------
# Funnel positions are set so each uptake rises through a DEDICATED CASING
# between two public rooms, never through a room (see layout.FUNNEL_CASINGS).
# This mirrors Teutonic, where the library sat between the two funnels.
FUNNELS = [
    {"x": 30.0, "dia": 3.60, "top_z": 30.60, "rake": 0.0, "casing": "boiler room fwd"},
    {"x": 4.5, "dia": 3.60, "top_z": 30.60, "rake": 0.0, "casing": "boiler room aft"},
]
# funnel colours (Albion & Western house flag): buff with black top band, red
# inner mouth.  Documented as house livery in spec, period-plausible vs.
# Cunard red / White Star buff / Inman black-green.
FUNNEL_COLORS = {"body": (0.78, 0.62, 0.36), "top_band": (0.06, 0.06, 0.06),
                 "band_height": 2.2, "inside": (0.30, 0.05, 0.03)}

# Masts rise through MAST TRUNKS in vestibules/alleyways, never through a
# furnished room: foremast on the forecastle, mainmast in the promenade
# vestibule, mizzen abaft the second-class smoking room.
# The mizzen is stepped in the upper (saloon) deck aft, abaft the galley
# block; every mast is on a trunk or a bulkhead, never inside a room.
MASTS = [
    {"name": "foremast",  "x": 70.0, "rake_deg": 1.5, "height_m": 24.0, "diameter": 0.55},
    {"name": "mainmast",  "x": -2.0, "rake_deg": 1.5, "height_m": 27.0, "diameter": 0.62},
    {"name": "mizzenmast","x": -45.6,"rake_deg": 1.5, "height_m": 21.0, "diameter": 0.48},
]
# rig: schooner rig for fore & aft sails; no yards (Teutonic 1889 was the first
# White Star ship without square rig - the trend is well documented).  Our ship
# keeps two square yards on the foremast only (as Umbria/Etruria did), plus a
# fore-and-aft sail on main and mizzen for steadying.
RIG = {
    "fore_square_yards": 2,
    "fore_and_aft": True,
    "wire_rigging": True,
}

# --------------------------------------------------------------------------
# 5. LIFEBOATS  (must match Agent 02's boats_spec.json)
# --------------------------------------------------------------------------
LIFEBOATS = {
    "steam_cutter": {
        "label": "25 ft steam cutter", "loa": 7.62, "beam": 2.28, "weight_kg": 1850,
        "davit_type": "Trotman radial davit, 2 per boat", "crew": 2, "capacity": 32,
    },
    "rowing_cutter": {
        "label": "27 ft ship's cutter (rowing)", "loa": 8.23, "beam": 2.44,
        "weight_kg": 980, "davit_type": "Trotman radial davit, 2 per boat",
        "crew": 1, "capacity": 34,
    },
}
# positions: (side, x of boat centre) on boat deck z=13.4
STARBOARD_BOATS = [(38.0, "steam_cutter"), (26.0, "rowing_cutter")]
PORT_BOATS = [(38.0, "rowing_cutter")]

# boat davit geometry
BOAT_DAVIT_H = 2.6
BOAT_INBOARD_OFFSET = 1.05

# --------------------------------------------------------------------------
# 6. COLOURS / MATERIAL INDICES (shared with Blender material library)
# --------------------------------------------------------------------------
PALETTE = {
    "hull_black":    (0.030, 0.032, 0.034, 1),   # anti-fouling/boot-topping composite looked black
    "boot_white":    (0.82, 0.80, 0.74, 1),
    "upper_white":   (0.86, 0.85, 0.80, 1),      # white painted topsides above sheer strake
    "deck_wood":     (0.42, 0.33, 0.22, 1),      # scrubbed deck planking ~9 in pitch pine
    "teak":          (0.33, 0.22, 0.12, 1),
    "mahogany":      (0.26, 0.11, 0.06, 1),
    "oak_light":     (0.55, 0.43, 0.28, 1),
    "brass":         (0.72, 0.55, 0.22, 1),
    "steel":         (0.36, 0.37, 0.38, 1),
    "cast_iron":     (0.14, 0.15, 0.15, 1),
    "paint_red_lead":(0.45, 0.16, 0.10, 1),
    "fabric_green":  (0.12, 0.24, 0.17, 1),
    "fabric_red":    (0.36, 0.09, 0.08, 1),
    "white_ceiling": (0.80, 0.78, 0.72, 1),
    "rope_hemp":     (0.55, 0.48, 0.33, 1),
    "glass":         (0.55, 0.62, 0.62, 0.35),
}

SCALE = {"metres_per_stud": 0.28}   # Roblox documented unit conversion

def half_beam_at_x(x):
    """Placeholder - real value from hull.HullForm."""
    raise NotImplementedError
