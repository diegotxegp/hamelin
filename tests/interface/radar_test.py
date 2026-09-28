from hamelin.interface.utils.radar import robust_bounds, normalize, point_on_circle, RadarItem


def test_robust_bounds_empty():
    assert robust_bounds([]) == (0.0, 0.0)


def test_robust_bounds_trims_extremes():
    values = list(range(100))
    p5, p95 = robust_bounds(values)
    assert p5 == 4
    assert p95 == 94


def test_normalize_midpoint():
    assert normalize(5, 0, 10) == 0.5


def test_normalize_clamps_outside_range():
    assert normalize(-5, 0, 10) == 0.0
    assert normalize(15, 0, 10) == 1.0


def test_normalize_equal_bounds_returns_half():
    assert normalize(7, 3, 3) == 0.5


def test_point_on_circle_first_point_is_at_top():
    x, y = point_on_circle(0, 4, 100)
    assert abs(x) < 1e-9
    assert y == -100


def test_point_on_circle_scales_with_value():
    x, y = point_on_circle(0, 4, 100, value=0.5)
    assert abs(y) == 50


def test_radar_item_empty_values_produces_empty_path():
    item = RadarItem([], [], radius=100)
    assert item.path().elementCount() == 0


def test_radar_item_builds_closed_path_for_each_value():
    item = RadarItem([1.0, 0.5, 1.0], ["a", "b", "c"], radius=100)
    # moveTo + 2 lineTo + closeSubpath's implicit closing element
    assert item.path().elementCount() >= 3
