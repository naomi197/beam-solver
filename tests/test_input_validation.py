import pytest

from beam_solver.solver import Beam, DistributedLoad, PointLoad, Support


def valid_beam(**kwargs):
    values = {
        "length": 8.0,
        "E": 200e9,
        "I": 0.004,
        "supports": [Support(0.0), Support(8.0)],
    }
    values.update(kwargs)
    return Beam(**values)


def test_negative_length_rejected():
    with pytest.raises(ValueError, match="length"):
        valid_beam(length=-1.0)


def test_non_positive_material_properties_rejected():
    with pytest.raises(ValueError, match="Young"):
        valid_beam(E=0.0)

    with pytest.raises(ValueError, match="moment"):
        valid_beam(I=-1.0)


def test_invalid_support_configuration_rejected():
    with pytest.raises(ValueError, match="exactly two"):
        valid_beam(supports=[Support(0.0)])

    with pytest.raises(ValueError, match="different"):
        valid_beam(supports=[Support(2.0), Support(2.0)])

    with pytest.raises(ValueError, match="within"):
        valid_beam(supports=[Support(-1.0), Support(8.0)])


def test_load_outside_beam_rejected():
    with pytest.raises(ValueError, match="Point load"):
        valid_beam(point_loads=[PointLoad(9.0, 1000.0)])

    with pytest.raises(ValueError, match="Distributed load"):
        valid_beam(dist_loads=[DistributedLoad(1.0, 9.0, 10.0)])


def test_invalid_distributed_load_rejected():
    with pytest.raises(ValueError, match="start"):
        DistributedLoad(4.0, 2.0, 10.0)

    with pytest.raises(ValueError, match="non-negative"):
        DistributedLoad(0.0, 2.0, -10.0)


def test_invalid_number_of_points_rejected():
    beam = valid_beam()

    with pytest.raises(ValueError, match="n_points"):
        beam.shear_moment(n_points=1)
