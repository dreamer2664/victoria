"""Standard-library regression tests for the Gen-III tide equations."""
import math
import unittest


PORT_A = {"low": -2.0, "high": 3.5, "period": 20 * 60.0}
GANGWAY = {
    "shore_z": 4.0,
    "deck_offset": 1.5,
    "span": 36.0,
    "reference_tide": 0.0,
    "direction_x": -1.0,
}


def level_at(spec, elapsed):
    phase = 2.0 * math.pi * elapsed / spec["period"]
    fraction = (1.0 - math.cos(phase)) * 0.5
    return spec["low"] + (spec["high"] - spec["low"]) * fraction


def gangway_angle(tide_m, spec=GANGWAY):
    dz = tide_m + spec["deck_offset"] - spec["shore_z"]
    return math.atan(dz / (spec["direction_x"] * spec["span"]))


def bogie_slide_m(tide_m, spec=GANGWAY):
    target = gangway_angle(tide_m, spec)
    base = gangway_angle(spec["reference_tide"], spec)
    return spec["direction_x"] * spec["span"] * (math.cos(target) - math.cos(base))


class TideMathTests(unittest.TestCase):
    def test_low_high_low_extrema_and_periodicity(self):
        period = PORT_A["period"]
        self.assertAlmostEqual(level_at(PORT_A, 0), -2.0)
        self.assertAlmostEqual(level_at(PORT_A, period / 2), 3.5)
        self.assertAlmostEqual(level_at(PORT_A, period), -2.0)
        self.assertAlmostEqual(level_at(PORT_A, period / 4), 0.75)
        self.assertAlmostEqual(level_at(PORT_A, 7 * period + 23), level_at(PORT_A, 23))

    def test_port_a_stays_inside_handoff_operating_envelope(self):
        samples = [level_at(PORT_A, PORT_A["period"] * i / 1000) for i in range(1001)]
        self.assertGreaterEqual(min(samples), -2.0)
        self.assertLessEqual(max(samples), 3.5)

    def test_bridge_angle_moves_smoothly_and_changes_sign(self):
        low_angle = gangway_angle(PORT_A["low"])
        reference_angle = gangway_angle(0.0)
        high_angle = gangway_angle(PORT_A["high"])
        self.assertGreater(low_angle, reference_angle)
        self.assertGreater(reference_angle, high_angle)
        self.assertLess(abs(low_angle - high_angle), math.radians(10.0))

    def test_bogie_tracks_endpoint_in_both_tide_directions(self):
        low_slide = bogie_slide_m(PORT_A["low"])
        high_slide = bogie_slide_m(PORT_A["high"])
        # The pontoon end lies along -X from the shore hinge. At low water the
        # greater down-slope draws the roller toward the shore (+X); high water
        # produces a small offset the other way.
        self.assertGreater(low_slide, 0.0)
        self.assertLess(high_slide, 0.0)
        self.assertLess(abs(low_slide), 0.25)
        self.assertLess(abs(high_slide), 0.10)

    def test_belfast_range_is_3_5_metres_total(self):
        spec = {"low": -1.75, "high": 1.75, "period": 1200.0}
        self.assertAlmostEqual(level_at(spec, 0), -1.75)
        self.assertAlmostEqual(level_at(spec, spec["period"] / 2), 1.75)
        self.assertAlmostEqual(level_at(spec, spec["period"] / 2) - level_at(spec, 0), 3.5)


if __name__ == "__main__":
    unittest.main()
