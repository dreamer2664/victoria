"""
vessels.py -- Late-Victorian (c. 1889) historic vessels and harbour craft.
GENERATION II — OPERATION VICTORIA (PERICLES-II)

All prototypes are built in local coordinates centered at (0, 0, 0) with:
- X across the beam (-hw to +hw)
- Y along the centerline (-hl to +hl, bow at +Y, stern at -Y)
- Z elevation (waterline at z = 0.0)

They are instanced and rotated naturally via R.place(name, x, y, z, rz).
"""
import math
from core import MeshBuilder, WATER_Z

def build_transatlantic_liner(mb, length=148.0, beam=16.8, draft=5.8, freeboard=9.2):
    """Grand late-Victorian transatlantic passenger steamship (c. 1889).
    Raked clipper bow, counter stern, black iron hull, red boot-topping,
    promenade deck, twin raked ochre funnels, twin rigged masts, lifeboats on davits."""
    hl = length / 2.0
    hw = beam / 2.0
    z_k = -draft
    z_wl = 0.0
    z_d = freeboard

    # 1. Hull stations along Y
    stations = [
        (-hl,        0.0,        0.0,        z_d + 1.8),
        (-hl * 0.92, hw * 0.45,  hw * 0.55,  z_d + 1.2),
        (-hl * 0.75, hw * 0.82,  hw * 0.88,  z_d + 0.6),
        (-hl * 0.50, hw * 0.98,  hw * 1.00,  z_d + 0.2),
        (0.0,        hw * 1.00,  hw * 1.00,  z_d),
        (hl * 0.50,  hw * 0.98,  hw * 1.00,  z_d + 0.3),
        (hl * 0.75,  hw * 0.80,  hw * 0.86,  z_d + 0.8),
        (hl * 0.92,  hw * 0.42,  hw * 0.48,  z_d + 1.6),
        (hl,         0.0,        0.0,        z_d + 2.4),
    ]

    for i in range(len(stations) - 1):
        y0, b_wl0, b_dk0, d0 = stations[i]
        y1, b_wl1, b_dk1, d1 = stations[i+1]

        # Red boot-topping (waterline to keel)
        mb.add_quad((-b_wl0, y0, z_wl), (0.0, y0, z_k), (0.0, y1, z_k), (-b_wl1, y1, z_wl), "paint_red")
        mb.add_quad((b_wl0, y0, z_wl), (b_wl1, y1, z_wl), (0.0, y1, z_k), (0.0, y0, z_k), "paint_red")

        # Black iron topsides
        mb.add_quad((-b_dk0, y0, d0 - 0.4), (-b_wl0, y0, z_wl), (-b_wl1, y1, z_wl), (-b_dk1, y1, d1 - 0.4), "black")
        mb.add_quad((b_dk0, y0, d0 - 0.4), (b_dk1, y1, d1 - 0.4), (b_wl1, y1, z_wl), (b_wl0, y0, z_wl), "black")

        # White sheer strake
        mb.add_quad((-b_dk0, y0, d0), (-b_dk0, y0, d0 - 0.4), (-b_dk1, y1, d1 - 0.4), (-b_dk1, y1, d1), "paint_white")
        mb.add_quad((b_dk0, y0, d0), (b_dk1, y1, d1), (b_dk1, y1, d1 - 0.4), (b_dk0, y0, d0 - 0.4), "paint_white")

        # Bulwarks & timber cap rail
        mb.add_quad((-b_dk0, y0, d0 + 1.1), (-b_dk0, y0, d0), (-b_dk1, y1, d1), (-b_dk1, y1, d1 + 1.1), "black")
        mb.add_quad((b_dk0, y0, d0 + 1.1), (b_dk1, y1, d1 + 1.1), (b_dk1, y1, d1), (b_dk0, y0, d0), "black")
        mb.add_box(-b_dk0 - 0.08, y0, d0 + 1.05, -b_dk1 + 0.08, y1, d1 + 1.15, "timber")
        mb.add_box(b_dk0 - 0.08, y0, d0 + 1.05, b_dk1 + 0.08, y1, d1 + 1.15, "timber")

        # Plated weather deck
        mb.add_quad((-b_dk0, y0, d0), (b_dk0, y0, d0), (b_dk1, y1, d1), (-b_dk1, y1, d1), "plank")

    # 2. Superstructure: Promenade deckhouse & Boat deck
    sup_y0 = -hl * 0.48
    sup_y1 = hl * 0.42
    sup_w = hw * 0.76
    z_prom = z_d + 2.8
    z_boat = z_prom + 2.6

    # Lower deckhouse
    mb.add_box(-sup_w, sup_y0, z_d, sup_w, sup_y1, z_prom, "paint_white")
    # Promenade deck planking
    mb.add_box(-sup_w - 0.4, sup_y0 - 0.6, z_prom, sup_w + 0.4, sup_y1 + 0.6, z_prom + 0.15, "plank")
    # Upper cabin deckhouse
    mb.add_box(-sup_w * 0.82, sup_y0 + 2.0, z_prom + 0.15, sup_w * 0.82, sup_y1 - 2.0, z_boat, "paint_white")
    # Boat deck
    mb.add_box(-sup_w * 0.88, sup_y0 + 1.4, z_boat, sup_w * 0.88, sup_y1 - 1.4, z_boat + 0.15, "plank")

    # Flying Navigating Bridge forward
    br_y = sup_y1 - 1.5
    br_z = z_boat + 0.15
    mb.add_box(-sup_w * 0.95, br_y - 2.8, br_z, sup_w * 0.95, br_y + 1.2, br_z + 2.4, "paint_white")
    # Bridge wings
    mb.add_box(-hw - 0.3, br_y - 1.2, br_z + 1.1, hw + 0.3, br_y + 0.8, br_z + 1.25, "timber")
    mb.add_box(-hw - 0.3, br_y + 0.7, br_z + 1.25, hw + 0.3, br_y + 0.8, br_z + 2.2, "iron")
    mb.add_cyl(0.0, br_y - 0.8, br_z + 2.4, br_z + 3.4, 0.28, "brass", seg=8)

    # 3. Twin Raked Funnels (Victorian red/ochre with black top band)
    funnel_y = [-hl * 0.18, hl * 0.12]
    for fy in funnel_y:
        fz0 = z_boat + 0.15
        fz1 = fz0 + 9.5
        fz_top = fz1 + 2.8
        mb.add_cyl(0.0, fy, fz0, fz1, 1.65, "paint_red", seg=12, r2=1.55)
        mb.add_cyl(0.0, fy - 0.4, fz1, fz_top, 1.55, "black", seg=12, r2=1.45)
        # Steam pipe
        mb.add_cyl(0.7, fy + 0.4, fz0, fz_top + 0.8, 0.12, "copper", seg=6)

    # 4. Twin Wood-and-Iron Masts with cross-trees & booms
    mast_specs = [
        (-hl * 0.62, z_d + 0.6, 26.0),
        (hl * 0.58, z_d + 1.0, 28.0),
    ]
    for my, mz0, mh in mast_specs:
        xt_z = mz0 + mh * 0.55
        mb.add_cyl(0.0, my, mz0, xt_z, 0.38, "paint_white", seg=8, r2=0.30)
        mb.add_box(-1.8, my - 0.4, xt_z, 1.8, my + 0.4, xt_z + 0.18, "timber")
        mb.add_cyl(0.0, my - 0.4, xt_z, mz0 + mh, 0.22, "timber", seg=6, r2=0.10)
        # Derrick boom
        mb.add_cyl(0.0, my + 0.6, mz0 + 1.8, mz0 + 8.5, 0.14, "timber", seg=6)

    # 5. Lifeboats on Davits (4 on port, 4 on starboard)
    lb_l = 7.4
    lb_w = 2.2
    for side in (-1, 1):
        x_dav = side * (sup_w * 0.92)
        for by in [-hl * 0.32, -hl * 0.14, hl * 0.04, hl * 0.22]:
            bz = z_boat + 0.8
            mb.add_box(x_dav - side * lb_w * 0.5, by - lb_l * 0.45, bz,
                       x_dav + side * lb_w * 0.5, by + lb_l * 0.45, bz + 1.1, "paint_white")
            mb.add_box(x_dav - side * lb_w * 0.45, by - lb_l * 0.42, bz + 1.05,
                       x_dav + side * lb_w * 0.45, by + lb_l * 0.42, bz + 1.25, "canvas")
            for dy in (-lb_l * 0.48, lb_l * 0.48):
                mb.add_cyl(x_dav - side * 0.5, by + dy, z_boat + 0.15, bz + 1.6, 0.08, "iron", seg=6)

    # 6. Cowl Ventilators
    for vx, vy in [(-2.2, -hl * 0.06), (2.2, -hl * 0.06), (-2.2, hl * 0.24), (2.2, hl * 0.24)]:
        vz = z_boat + 0.15
        mb.add_cyl(vx, vy, vz, vz + 2.0, 0.32, "paint_white", seg=8)
        mb.add_cyl(vx, vy + 0.2, vz + 2.0, vz + 2.6, 0.55, "paint_red", seg=8)

    # 7. Bowsprit / Jackstaff & Stern Ensign Staff
    mb.add_cyl(0.0, hl - 0.4, z_d + 2.4, z_d + 6.0, 0.10, "timber", seg=6)
    mb.add_cyl(0.0, -hl + 0.8, z_d + 1.8, z_d + 5.2, 0.08, "timber", seg=6)

    # 8. Stern Propeller & Rudder
    mb.add_cyl(0.0, -hl * 0.94, z_k + 1.8, z_k + 1.8, 1.8, "bronze", seg=8, axis="Y")
    mb.add_box(-0.15, -hl * 0.98, z_k + 0.4, 0.15, -hl * 0.92, z_k + 4.2, "iron")


def build_cargo_steamer(mb, length=76.0, beam=11.2, draft=4.5, freeboard=6.4):
    """Victorian coastal collier / cargo steamer (c. 1889).
    Raised forecastle and poop, well deck, tarpaulin cargo hatches, derricks, central funnel."""
    hl = length / 2.0
    hw = beam / 2.0
    z_k = -draft
    z_d = freeboard

    # Hull (red bottom, black topsides)
    mb.add_box(-hw, -hl * 0.88, z_k, hw, hl * 0.88, 0.0, "paint_red")
    mb.add_box(-hw, -hl * 0.88, 0.0, hw, hl * 0.88, z_d, "black")
    # Weather deck
    mb.add_box(-hw + 0.15, -hl * 0.85, z_d, hw - 0.15, hl * 0.85, z_d + 0.15, "plank")

    # Raised forecastle and poop
    mb.add_box(-hw, hl * 0.65, z_d + 0.15, hw, hl * 0.88, z_d + 1.8, "black")
    mb.add_box(-hw, -hl * 0.88, z_d + 0.15, hw, -hl * 0.62, z_d + 1.6, "black")

    # Cargo hatches with tarpaulins
    for hy in [-hl * 0.35, hl * 0.35]:
        mb.add_box(-hw * 0.55, hy - 4.5, z_d + 0.15, hw * 0.55, hy + 4.5, z_d + 0.95, "timber")
        mb.add_box(-hw * 0.52, hy - 4.3, z_d + 0.95, hw * 0.52, hy + 4.3, z_d + 1.15, "canvas")

    # Superstructure & wheelhouse
    mb.add_box(-hw * 0.65, -6.0, z_d + 0.15, hw * 0.65, 6.0, z_d + 2.8, "paint_white")
    mb.add_box(-hw * 0.45, 1.0, z_d + 2.8, hw * 0.45, 5.5, z_d + 4.8, "timber")

    # Funnel
    mb.add_cyl(0.0, -1.8, z_d + 2.8, z_d + 10.5, 1.15, "black", seg=10, r2=1.05)
    mb.add_cyl(0.4, -1.4, z_d + 2.8, z_d + 10.8, 0.08, "brass", seg=6)

    # Masts & derricks
    for my in [-hl * 0.48, hl * 0.48]:
        mb.add_cyl(0.0, my, z_d + 0.15, z_d + 18.0, 0.28, "timber", seg=6, r2=0.12)
        mb.add_cyl(0.0, my + 0.4, z_d + 1.6, z_d + 7.2, 0.12, "timber", seg=6)


def build_steam_tug(mb, length=26.0, beam=6.2, draft=2.8, freeboard=2.2):
    """Harbour steam tugboat (c. 1889).
    Heavy bow rope pudding fender, tall slender funnel, towing bitt."""
    hl = length / 2.0
    hw = beam / 2.0
    z_k = -draft
    z_d = freeboard

    mb.add_box(-hw, -hl * 0.85, z_k, hw, hl * 0.85, 0.0, "paint_red")
    mb.add_box(-hw, -hl * 0.85, 0.0, hw, hl * 0.85, z_d, "black")
    mb.add_box(-hw + 0.1, -hl * 0.82, z_d, hw - 0.1, hl * 0.82, z_d + 0.12, "plank")

    # Bow rope pudding fender
    mb.add_cyl(0.0, hl * 0.82, z_d - 0.2, z_d + 0.4, 0.45, "rope", seg=8, axis="X")

    # Deckhouse & wheelhouse
    mb.add_box(-hw * 0.55, -hl * 0.45, z_d + 0.12, hw * 0.55, hl * 0.35, z_d + 1.8, "paint_white")
    mb.add_box(-hw * 0.45, hl * 0.05, z_d + 1.8, hw * 0.45, hl * 0.32, z_d + 3.6, "timber")

    # Funnel
    mb.add_cyl(0.0, -hl * 0.12, z_d + 1.8, z_d + 8.2, 0.52, "black", seg=8)
    mb.add_cyl(0.0, -hl * 0.14, z_d + 5.2, z_d + 6.2, 0.54, "paint_red", seg=8)

    # Towing bitt
    mb.add_cyl(-0.6, -hl * 0.55, z_d + 0.12, z_d + 1.6, 0.18, "iron", seg=6)
    mb.add_cyl(0.6, -hl * 0.55, z_d + 0.12, z_d + 1.6, 0.18, "iron", seg=6)
    mb.add_box(-0.8, -hl * 0.58, z_d + 1.4, 0.8, -hl * 0.52, z_d + 1.65, "iron")


def build_harbour_lighter(mb, length=18.0, beam=4.6):
    """Open hold iron harbour lighter / coal barge."""
    hl = length / 2.0
    hw = beam / 2.0
    # Iron hull
    mb.add_box(-hw, -hl, -1.2, hw, hl, 0.55, "steel_plate")
    # Timber rubbing strake / gunwale
    mb.add_box(-hw - 0.08, -hl, 0.40, hw + 0.08, hl, 0.65, "timber")
    # Hold coaming
    mb.add_box(-hw + 0.45, -hl + 2.4, 0.55, hw - 0.45, hl - 1.8, 1.05, "iron")
    # Coal heap inside hold
    mb.add_box(-hw + 0.55, -hl + 2.6, 0.55, hw - 0.55, hl - 2.0, 1.45, "coal")
    mb.add_box(-hw + 0.85, -hl + 3.8, 1.45, hw - 0.85, hl - 3.2, 1.75, "coal")
    # Wooden cuddy cabin at stern
    mb.add_box(-hw * 0.65, -hl + 0.3, 0.55, hw * 0.65, -hl + 2.1, 1.65, "timber")
    mb.add_cyl(0.35, -hl + 0.9, 1.65, 2.35, 0.06, "black", seg=6)  # stovepipe
    # Tiller
    mb.add_cyl(0.0, -hl + 0.2, 0.55, 1.25, 0.07, "brass", seg=6)
    # Mooring bitts
    for bx, by in [(-hw + 0.5, hl - 0.8), (hw - 0.5, hl - 0.8), (-hw + 0.5, -hl + 0.6), (hw - 0.5, -hl + 0.6)]:
        mb.add_cyl(bx, by, 0.55, 1.15, 0.12, "iron", seg=6)


def build_slipway_hull(mb, length=68.0, beam=10.4):
    """Iron ship hull under construction on building slip.
    Heavy bar keel laid on keel blocks, vertical transverse iron frame ribs, ribbands, shores, scaffolding."""
    hl = length / 2.0
    hw = beam / 2.0

    # 1. Keel blocks
    for ky in range(int(-hl), int(hl), 3):
        mb.add_box(-0.6, ky - 0.6, 0.0, 0.6, ky + 0.6, 1.4, "timber")

    # 2. Keel bar
    mb.add_box(-0.15, -hl, 1.4, 0.15, hl, 1.8, "steel")

    # 3. Transverse iron ribs
    n_ribs = 18
    for i in range(n_ribs):
        t = i / (n_ribs - 1)
        ry = -hl * 0.92 + t * (hl * 1.84)
        rib_w = hw * (1.0 - 0.32 * (abs(ry) / hl) ** 2.2)
        rib_h = 7.2 * (1.0 - 0.15 * (abs(ry) / hl))

        for side in (-1, 1):
            mb.add_box(0.0, ry - 0.08, 1.8, side * rib_w * 0.7, ry + 0.08, 2.3, "steel")
            mb.add_box(side * rib_w * 0.65, ry - 0.08, 2.1, side * rib_w, ry + 0.08, 3.8, "steel")
            mb.add_box(side * (rib_w - 0.15), ry - 0.08, 3.6, side * rib_w, ry + 0.08, 1.8 + rib_h, "steel")
            mb.add_box(-rib_w * 0.95, ry - 0.06, 1.8 + rib_h - 0.2, rib_w * 0.95, ry + 0.06, 1.8 + rib_h, "steel")

    # 4. Longitudinal ribbands
    for side in (-1, 1):
        for rz in (3.2, 5.4, 7.8):
            mb.add_box(side * (hw - 0.08), -hl * 0.88, rz, side * hw, hl * 0.88, rz + 0.18, "timber")

    # 5. Staging scaffolding & shores
    for sy in range(int(-hl * 0.8), int(hl * 0.8), 6):
        for side in (-1, 1):
            mb.add_box(side * (hw + 3.2), sy - 0.15, 0.0, side * (hw + 0.1), sy + 0.15, 5.0, "timber")
            mb.add_cyl(side * (hw + 1.8), sy, 0.0, 9.2, 0.12, "timber", seg=6)
            mb.add_box(side * (hw + 1.2), sy - 3.0, 4.2, side * (hw + 2.2), sy + 3.0, 4.35, "plank")
            mb.add_box(side * (hw + 1.2), sy - 3.0, 7.0, side * (hw + 2.2), sy + 3.0, 7.15, "plank")


def build_drydock_hull(mb, length=110.0, beam=14.4):
    """Large iron steamship under repair inside Princess Graving Dock.
    Sitting on keel blocks, propped by heavy diagonal timber shores from altars."""
    hl = length / 2.0
    hw = beam / 2.0
    z_k = 1.2

    # Hull
    mb.add_box(-hw, -hl * 0.85, z_k, hw, hl * 0.85, z_k + 4.2, "paint_red")
    mb.add_box(-hw, -hl * 0.85, z_k + 4.2, hw, hl * 0.85, z_k + 9.5, "steel_plate")

    # Weather deck
    mb.add_box(-hw + 0.15, -hl * 0.82, z_k + 9.5, hw - 0.15, hl * 0.82, z_k + 9.7, "plank")

    # Propeller & Rudder
    mb.add_cyl(0.0, -hl * 0.92, z_k + 2.4, z_k + 2.4, 1.9, "bronze", seg=8, axis="Y")
    mb.add_box(-0.18, -hl * 0.98, z_k + 0.4, 0.18, -hl * 0.90, z_k + 5.2, "iron")

    # Diagonal shores to altars
    for sy in range(int(-hl * 0.75), int(hl * 0.75), 8):
        for side in (-1, 1):
            mb.add_box(side * (hw + 3.8), sy - 0.18, 3.2, side * (hw - 0.1), sy + 0.18, 4.8, "timber")
            mb.add_box(side * (hw + 4.8), sy - 0.18, 6.2, side * (hw - 0.1), sy + 0.18, 7.8, "timber")

    # Suspended staging
    for side in (-1, 1):
        mb.add_box(side * (hw + 0.4), -hl * 0.4, z_k + 4.5, side * (hw + 1.2), hl * 0.4, z_k + 4.65, "plank")
        for ry in [-hl * 0.35, -hl * 0.1, hl * 0.15, hl * 0.35]:
            mb.add_cyl(side * (hw + 0.8), ry, z_k + 4.65, z_k + 9.5, 0.04, "rope", seg=4)
