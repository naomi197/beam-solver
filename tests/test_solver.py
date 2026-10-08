import pytest
import numpy as np
from beam_solver.solver import Beam, Support, PointLoad

def test_simple_beam_moment():
    # تیر ۶ متری، بار ۱۰ کیلونیوتن در وسط (۳ متر)
    L = 6.0
    P = 10000.0
    beam = Beam(
        length=L,
        E=200e9,
        I=5000e-8,
        supports=[Support(position=0), Support(position=L)],
        point_loads=[PointLoad(position=L/2, fz=P)]
    )
    
    x, V, M = beam.shear_moment(n_points=101)
    
    # مقدار تئوری لنگر در وسط: P*L/4 = 10000 * 6 / 4 = 15000 Nm
    max_m_calc = np.max(np.abs(M))
    expected_m = (P * L) / 4
    
    assert pytest.approx(max_m_calc, rel=1e-3) == expected_m
    print(f"\nTest Passed: Calculated M={max_m_calc}, Expected M={expected_m}")

def test_reactions():
    # تقارن: واکنش‌ها باید نصف بار کل باشند
    L = 6.0
    P = 10000.0
    beam = Beam(
        length=L,
        E=200e9,
        I=5000e-8,
        supports=[Support(position=0), Support(position=L)],
        point_loads=[PointLoad(position=L/2, fz=P)]
    )
    R = beam.reactions()
    assert R[0] == 5000.0
    assert R[1] == 5000.0
