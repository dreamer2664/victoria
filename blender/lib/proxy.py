"""
proxy.py -- BERTH CLEARANCE PROXIES.

*** THESE ARE NOT SHIP ASSETS ***

They are deliberately crude block-outs used only to prove, in a render and in the
layout auditor, that the berths actually accept the agreed integration envelope
(length 180 m, beam 20 m, draft 9 m) with working clearance. The vessel itself is
another agent's deliverable; nothing here is intended to look like a finished ship
and it is exported separately (assets/modular/_PROXY_*) so it can never be mistaken
for one. Delete the proxies before shipping the environment.
"""


def proxy_ship(mb, cx, cy, length=180.0, beam=20.0, draft=9.0, freeboard=11.0,
               bow="+Y"):
    """A slab-sided hull block-out with a waterline band, two funnels and two masts.
    Deliberately unadorned: it is a measuring stick, not a model."""
    hw = beam / 2.0
    hl = length / 2.0
    z0 = -draft                      # keel
    z1 = freeboard                   # main deck
    y0, y1 = (cy - hl, cy + hl) if bow == "+Y" else (cy + hl, cy - hl)

    # hull sides, tapered 22% at each end so the waterline footprint is realistic
    taper = 0.22
    def w(y):
        t = abs((y - cy) / hl)
        return hw * (1.0 - taper * t ** 2.2)

    n = 9
    prev = None
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        h = w(y)
        cur = (cx - h, y, cx + h, y)
        if prev:
            mb.add_quad((prev[0], prev[1], z0), (cur[0], cur[1], z0),
                        (cur[2], cur[3], z0), (prev[2], prev[3], z0), "black")
            mb.add_quad((prev[0], prev[1], z1), (prev[2], prev[3], z1),
                        (cur[2], cur[3], z1), (cur[0], cur[1], z1), "steel_plate")
            mb.add_quad((prev[0], prev[1], z0), (prev[0], prev[1], z1),
                        (cur[0], cur[1], z1), (cur[0], cur[1], z0), "steel_plate")
            mb.add_quad((cur[2], cur[3], z0), (prev[2], prev[3], z0),
                        (prev[2], prev[3], z1), (cur[2], cur[3], z1), "steel_plate")
        prev = cur
    # waterline band + boot topping
    for i in range(n):
        pass
    # superstructure blocks (two decks of cabins) and a promenade
    mb.add_box(cx - hw * 0.62, cy - hl * 0.62, z1, cx + hw * 0.62, cy + hl * 0.62,
               z1 + 4.2, "paint_white")
    mb.add_box(cx - hw * 0.5, cy - hl * 0.52, z1 + 4.2, cx + hw * 0.5, cy + hl * 0.52,
               z1 + 7.4, "paint_white")
    mb.add_box(cx - hw * 0.42, cy - hl * 0.30, z1 + 7.4, cx + hw * 0.42, cy + hl * 0.30,
               z1 + 8.6, "paint_white")
    # funnels
    for dy in (-hl * 0.16, hl * 0.10):
        mb.add_cyl(cx, cy + dy, z1 + 7.4, z1 + 15.0, 2.5, "paint_red", seg=12, r2=2.3)
        mb.add_cyl(cx, cy + dy, z1 + 14.2, z1 + 15.1, 2.35, "black", seg=12)
    # masts
    for dy in (-hl * 0.72, hl * 0.68):
        mb.add_cyl(cx, cy + dy, z1 + 4.0, z1 + 19.0, 0.28, "timber", seg=6, r2=0.14)
    # rudder + propeller boss, so the aft end reads correctly in clearance renders
    mb.add_box(cx - 0.4, cy - hl - 1.2, z0 + 1.0, cx + 0.4, cy - hl, z0 + 6.0, "black")
    return dict(length=length, beam=beam, draft=draft)


def proxy_barge(mb, cx, cy, length=22.0, beam=4.6):
    mb.add_box(cx - beam / 2, cy - length / 2, -0.9, cx + beam / 2, cy + length / 2, 0.55,
               "steel_plate")
    mb.add_box(cx - beam / 2 + 0.3, cy - length / 2 + 0.4, 0.55,
               cx + beam / 2 - 0.3, cy + length / 2 - 0.4, 1.05, "coal")
