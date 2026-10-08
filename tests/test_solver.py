import numpy as np
import pytest

from beam_solver.solver import (
    Beam,
    DistributedLoad,
    PointLoad,
    Support,
)


def simple_beam(length=8.0, point_loads=None, dist_loads=None):
    return Beam(
        length=length,
        E=200e9,
        I=0.004,
        supports=[Support(position=0.0), Support(position=length)],
        point_loads=point_loads or [],
        dist_loads=dist_loads or [],
    )


def test_simple_beam_moment():
    length = 6.0
    point_load = 10000.0
    beam = simple_beam(
        length=length,
        point_loads=[PointLoad(position=length / 2, fz=point_load)],
    )

    _, _, moment = beam.shear_moment(n_points=101)

    expected_moment = point_load * length / 4
    assert np.max(np.abs(moment)) == pytest.approx(expected_moment, rel=1e-3)


def test_reactions():
    length = 6.0
    point_load = 10000.0
    beam = simple_beam(
        length=length,
        point_loads=[PointLoad(position=length / 2, fz=point_load)],
    )

    reactions = beam.reactions()

    assert reactions[0] == pytest.approx(5000.0)
    assert reactions[1] == pytest.approx(5000.0)


def test_uniform_distributed_load():
    length = 8.0
    load = 15.0
    beam = simple_beam(
        length=length,
        dist_loads=[DistributedLoad(0.0, length, load)],
    )

    reactions = beam.reactions()
    _, shear, moment = beam.shear_moment(n_points=101)

    expected_reaction = load * length / 2
    expected_moment = load * length**2 / 8

    assert reactions[0] == pytest.approx(expected_reaction)
    assert reactions[1] == pytest.approx(expected_reaction)
    assert moment[-1] == pytest.approx(0.0, abs=1e-9)
    assert np.max(moment) == pytest.approx(expected_moment, rel=1e-3)
    assert shear[-1] == pytest.approx(0.0, abs=1e-9)


def test_triangular_distributed_load():
    length = 8.0
    load_end = 20.0
    beam = simple_beam(
        length=length,
        dist_loads=[DistributedLoad(0.0, length, 0.0, load_end)],
    )

    reactions = beam.reactions()
    _, shear, moment = beam.shear_moment(n_points=101)

    total_load = load_end * length / 2
    expected_left = total_load / 3
    expected_right = 2 * total_load / 3

    assert reactions[0] == pytest.approx(expected_left)
    assert reactions[1] == pytest.approx(expected_right)
    assert shear[-1] == pytest.approx(0.0, abs=1e-9)
    assert moment[-1] == pytest.approx(0.0, abs=1e-9)


def test_trapezoidal_distributed_load_equilibrium():
    length = 8.0
    start_load = 10.0
    end_load = 20.0
    beam = simple_beam(
        length=length,
        dist_loads=[DistributedLoad(0.0, length, start_load, end_load)],
    )

    reactions = beam.reactions()
    _, shear, moment = beam.shear_moment(n_points=101)

    total_load = (start_load + end_load) * length / 2

    assert reactions[0] + reactions[1] == pytest.approx(total_load)
    assert shear[-1] == pytest.approx(0.0, abs=1e-9)
    assert moment[-1] == pytest.approx(0.0, abs=1e-9)
