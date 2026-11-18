"""
clutter.py -- Late-Victorian (c. 1889) dockside cargo, street furniture, and industrial clutter.
GENERATION II — OPERATION VICTORIA (PERICLES-II)

All prototypes are defined in local coordinates centered at (0, 0, 0).
Instanced and positioned naturally via R.place(name, x, y, z, rz).
"""
import math
from core import MeshBuilder

def crate_pyramid(mb):
    """Tiered stack of wooden shipping crates with iron corner reinforcement."""
    coords = [(-0.95, -0.95), (0.95, -0.95), (-0.95, 0.95), (0.95, 0.95)]
    for cx, cy in coords:
        mb.add_box(cx - 0.85, cy - 0.85, 0.0, cx + 0.85, cy + 0.85, 1.4, "timber")
        for dx in (-0.85, 0.85):
            for dy in (-0.85, 0.85):
                mb.add_box(cx + dx - 0.04, cy + dy - 0.04, 0.0, cx + dx + 0.04, cy + dy + 0.04, 1.4, "iron")

    mb.add_box(-0.85, -0.85, 1.4, 0.85, 0.85, 2.8, "timber")
    mb.add_box(-0.65, -0.65, 2.8, 0.65, 0.65, 4.1, "timber")


def barrel_cluster(mb):
    """Cluster of wooden casks and hogsheads bound with iron hoops."""
    centers = [(-0.6, -0.6), (0.6, -0.6), (-0.6, 0.6), (0.6, 0.6), (0.0, 0.0), (-1.2, 0.0), (1.2, 0.0)]
    for bx, by in centers:
        mb.add_cyl(bx, by, 0.0, 1.15, 0.38, "timber", seg=8, r2=0.42)
        for hz in (0.18, 0.45, 0.70, 0.98):
            mb.add_cyl(bx, by, hz, hz + 0.04, 0.43, "iron", seg=8)

    for by in (-0.45, 0.45):
        mb.add_cyl(0.0, by, 1.15, 1.15, 0.36, "timber", seg=8, axis="X")


def cotton_bale_stack(mb):
    """Jute-wrapped cotton/wool bales bound with iron straps on timber dunnage."""
    for sx in (-1.4, 0.0, 1.4):
        mb.add_box(sx - 0.12, -2.4, 0.0, sx + 0.12, 2.4, 0.15, "timber")

    for lz, (nx, ny) in enumerate([(3, 3), (2, 3), (2, 2)]):
        z_base = 0.15 + lz * 0.85
        for ix in range(nx):
            bx = -1.2 + ix * 1.2
            for iy in range(ny):
                by = -1.4 + iy * 1.4
                mb.add_box(bx - 0.52, by - 0.62, z_base, bx + 0.52, by + 0.62, z_base + 0.80, "canvas")
                for b_off in (-0.35, 0.0, 0.35):
                    mb.add_box(bx - 0.54, by + b_off - 0.02, z_base, bx + 0.54, by + b_off + 0.02, z_base + 0.82, "iron")


def grain_sack_pile(mb):
    """Pyramid of grain sacks covered with a tarpaulin."""
    mb.add_box(-1.8, -1.4, 0.0, 1.8, 1.4, 1.2, "canvas")
    mb.add_box(-1.4, -1.1, 1.2, 1.4, 1.1, 2.2, "canvas")
    for rx in (-1.2, 0.0, 1.2):
        mb.add_cyl(rx, 0.0, 0.0, 2.22, 0.03, "rope", seg=4)


def cable_spool_depot(mb):
    """Large wooden cable reels with wound wire rope and anchor chains."""
    r = 1.2
    w_reel = 1.4
    mb.add_cyl(-0.8, -w_reel * 0.5, r - r, r + r, r, "timber", seg=12, axis="Y")
    mb.add_cyl(-0.8, -w_reel * 0.42, r - r * 0.85, r + r * 0.85, r * 0.85, "steel", seg=12, axis="Y")
    mb.add_cyl(1.2, 0.0, 0.0, 1.22, 1.1, "timber", seg=12)
    mb.add_cyl(1.2, 0.0, 0.12, 1.1, 0.95, "rope", seg=12)


def anchor_chain_heap(mb):
    """Heavy stud-link anchor chain coiled on the quayside."""
    for tz, r_coil in enumerate([1.4, 1.1, 0.8]):
        z_ring = tz * 0.22
        mb.add_cyl(0.0, 0.0, z_ring, z_ring + 0.18, r_coil, "iron", seg=10, r2=r_coil * 0.85)
    mb.add_box(-1.8, -0.15, 0.0, 1.8, 0.15, 0.28, "iron")
    mb.add_cyl(0.0, 1.2, 0.14, 0.14, 0.14, "iron", seg=6, axis="Y")


def spare_ship_propeller(mb):
    """4-bladed manganese-bronze spare ship propeller resting on timber skids."""
    mb.add_box(-1.2, -0.6, 0.0, 1.2, -0.3, 0.35, "timber")
    mb.add_box(-1.2, 0.3, 0.0, 1.2, 0.6, 0.35, "timber")
    mb.add_cyl(0.0, 0.0, 0.35, 1.45, 0.45, "bronze", seg=8)
    r_blade = 1.85
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        bx = math.cos(rad) * r_blade * 0.6
        by = math.sin(rad) * r_blade * 0.6
        mb.add_box(bx - 0.35, by - 0.35, 0.75, bx + 0.35, by + 0.35, 1.05, "bronze")


def shipyard_plate_rack(mb, length=8.5):
    """Shipyard A-frame rack holding stacks of rolled steel ship plating."""
    hl = length / 2.0
    for py in range(int(-hl + 0.8), int(hl - 0.8), 2):
        mb.add_box(-1.1, py - 0.05, 0.0, 1.1, py + 0.05, 3.2, "steel_plate")
    for ey in (-hl, hl):
        mb.add_box(-1.4, ey - 0.15, 0.0, -0.9, ey + 0.15, 3.4, "timber")
        mb.add_box(0.9, ey - 0.15, 0.0, 1.4, ey + 0.15, 3.4, "timber")
        mb.add_box(-1.2, ey - 0.12, 3.3, 1.2, ey + 0.12, 3.5, "timber")


def lifebuoy_stand(mb):
    """Victorian dockside cork life ring on timber post."""
    mb.add_cyl(0.0, 0.0, 0.0, 1.8, 0.08, "paint_white", seg=6)
    mb.add_cyl(0.0, 0.12, 1.15, 1.55, 0.42, "paint_red", seg=10, r2=0.22, axis="Y")
    mb.add_cyl(0.0, 0.14, 1.18, 1.52, 0.38, "paint_white", seg=10, r2=0.24, axis="Y")


def horse_water_trough(mb):
    """Carved sandstone drinking trough for carters' draught horses."""
    mb.add_box(-1.6, -0.65, 0.0, 1.6, 0.65, 0.85, "sandstone")
    mb.add_box(-1.4, -0.48, 0.65, 1.4, 0.48, 0.75, "puddle")
    mb.add_cyl(-1.4, 0.0, 0.85, 1.95, 0.14, "iron", seg=8)
    mb.add_box(-1.8, -0.05, 1.45, -1.4, 0.05, 1.60, "iron")


def warehouse_cathead_lucam(mb):
    """Overhanging gabled cathead hoist dormer (lucam) on warehouse top floor."""
    mb.add_box(-1.6, 0.0, 0.0, 1.6, 1.8, 2.4, "timber")
    mb.add_box(-1.8, -0.2, 2.2, 1.8, 2.0, 2.5, "slate")
    mb.add_box(-0.15, -0.15, 2.0, 0.15, 2.4, 2.3, "timber")
    mb.add_cyl(0.0, 2.2, 1.8, 2.05, 0.22, "iron", seg=8, axis="X")
    mb.add_cyl(0.0, 2.2, -6.5, 1.8, 0.025, "rope", seg=4)
    mb.add_box(-0.12, 2.12, -6.8, 0.12, 2.28, -6.5, "iron")


def timber_staging(mb):
    """Shipwrights' heavy timber shores, baulks and staging planks."""
    for sx in (-2.4, 0.0, 2.4):
        for sy in (-1.2, 1.2):
            mb.add_box(sx - 0.2, sy - 0.2, 0.0, sx + 0.2, sy + 0.2, 3.6, "timber_weathered")
    for sz in (1.6, 3.4):
        mb.add_box(-2.8, -1.3, sz, 2.8, -1.1, sz + 0.22, "timber_weathered")
        mb.add_box(-2.8, 1.1, sz, 2.8, 1.3, sz + 0.22, "timber_weathered")
    for px in range(-6, 7):
        mb.add_box(px * 0.38 - 0.16, -1.4, 3.42, px * 0.38 + 0.16, 1.4, 3.52, "timber_weathered")
