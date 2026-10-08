"""2D Euler-Bernoulli beam solver using stiffness method."""

from dataclasses import dataclass, field
import numpy as np


@dataclass
class Support:
    position: float          # x-coordinate along the beam (m)
    ux: bool = False         # horizontal restraint
    uy: bool = True          # vertical restraint
    rz: bool = False         # rotational restraint

    def __post_init__(self):
        if not np.isfinite(self.position):
            raise ValueError("Support position must be finite.")


@dataclass
class PointLoad:
    position: float
    fz: float                # downward load magnitude (N, positive = down)

    def __post_init__(self):
        if not np.isfinite(self.position):
            raise ValueError("Point load position must be finite.")
        if not np.isfinite(self.fz):
            raise ValueError("Point load magnitude must be finite.")


@dataclass
class DistributedLoad:
    start: float
    end: float
    w_start: float           # N/m at start
    w_end: float = None      # N/m at end (default = w_start for uniform)

    def __post_init__(self):
        if not np.isfinite(self.start) or not np.isfinite(self.end):
            raise ValueError("Distributed load positions must be finite.")
        if self.start >= self.end:
            raise ValueError("Distributed load start must be less than end.")

        if not np.isfinite(self.w_start) or self.w_start < 0:
            raise ValueError("Distributed load intensity must be finite and non-negative.")

        if self.w_end is not None:
            if not np.isfinite(self.w_end) or self.w_end < 0:
                raise ValueError("Distributed load intensity must be finite and non-negative.")


@dataclass
class Beam:
    length: float            # m
    E: float                 # Young's modulus (Pa)
    I: float                 # second moment of area (m^4)
    supports: list = field(default_factory=list)
    point_loads: list = field(default_factory=list)
    dist_loads: list = field(default_factory=list)

    def __post_init__(self):
        if not np.isfinite(self.length) or self.length <= 0:
            raise ValueError("Beam length must be finite and greater than zero.")
        if not np.isfinite(self.E) or self.E <= 0:
            raise ValueError("Young's modulus E must be finite and greater than zero.")
        if not np.isfinite(self.I) or self.I <= 0:
            raise ValueError("Second moment of area I must be finite and greater than zero.")

        if len(self.supports) != 2:
            raise ValueError("Beam requires exactly two supports.")

        support_positions = [support.position for support in self.supports]
        if any(position < 0 or position > self.length for position in support_positions):
            raise ValueError("Support positions must lie within the beam.")
        if support_positions[0] == support_positions[1]:
            raise ValueError("Support positions must be different.")

        for load in self.point_loads:
            if load.position < 0 or load.position > self.length:
                raise ValueError("Point load position must lie within the beam.")

        for load in self.dist_loads:
            if load.start < 0 or load.end > self.length:
                raise ValueError("Distributed load must lie within the beam.")

    def _flex_coeff(self, a, b):
        """Simply supported beam Green's function for unit load."""
        L = self.length
        if a > b:
            a, b = b, a
        # Deflection at a due to load at b for simple span
        return (a * (L - b) * (L**2 - a**2 - (L - b)**2)) / (6 * self.E * self.I * L)

    def reactions(self):
        """Calculate support reactions for simply supported beam."""
        if len(self.supports) != 2:
            raise NotImplementedError("Currently supports 2-pin/roller spans.")
        
        s1, s2 = self.supports[0].position, self.supports[1].position
        L_span = s2 - s1
        
        # Equilibrium: sum(M) about s1 = 0, sum(Fz) = 0
        total_load = 0.0
        moment_about_s1 = 0.0
        
        for pl in self.point_loads:
            total_load += pl.fz
            moment_about_s1 += pl.fz * (pl.position - s1)
            
        for dl in self.dist_loads:
            w_end = dl.w_end if dl.w_end is not None else dl.w_start
            span_len = dl.end - dl.start
            load_mag = (dl.w_start + w_end) * span_len / 2.0
            if load_mag:
                centroid_offset = span_len * (
                    dl.w_start + 2.0 * w_end
                ) / (3.0 * (dl.w_start + w_end))
            else:
                centroid_offset = span_len / 2.0
            centroid = dl.start + centroid_offset
            total_load += load_mag
            moment_about_s1 += load_mag * (centroid - s1)
            
        R2 = moment_about_s1 / L_span
        R1 = total_load - R2
        return {0: R1, 1: R2}

    def shear_moment(self, n_points=500):
        """Return arrays (x, V, M) along the beam."""
        if not isinstance(n_points, (int, np.integer)) or n_points < 2:
            raise ValueError("n_points must be an integer greater than or equal to 2.")

        x = np.linspace(0, self.length, n_points)
        R = self.reactions()
        s1, s2 = self.supports[0].position, self.supports[1].position
        
        V = np.zeros(n_points)
        M = np.zeros(n_points)
        
        for i, xi in enumerate(x):
            v_val = 0.0
            m_val = 0.0
            
            # Reactions contribution
            if xi >= s1:
                v_val -= R[0]
                m_val += R[0] * (xi - s1)
            if xi >= s2:
                v_val -= R[1]
                m_val += R[1] * (xi - s2)
                
            # Point loads
            for pl in self.point_loads:
                if xi >= pl.position:
                    v_val += pl.fz
                    m_val -= pl.fz * (xi - pl.position)
                    
            # Distributed loads
            for dl in self.dist_loads:
                if xi > dl.start:
                    w_end = dl.w_end if dl.w_end is not None else dl.w_start
                    loaded_len = min(xi, dl.end) - dl.start
                    full_len = dl.end - dl.start
                    slope = (w_end - dl.w_start) / full_len
                    w_load = (
                        dl.w_start * loaded_len
                        + 0.5 * slope * loaded_len**2
                    )
                    if w_load:
                        load_centroid = (
                            dl.w_start * loaded_len**2 / 2.0
                            + slope * loaded_len**3 / 3.0
                        ) / w_load
                    else:
                        load_centroid = loaded_len / 2.0
                    lever_arm = xi - (dl.start + load_centroid)
                    v_val += w_load
                    m_val -= w_load * lever_arm
                    
            V[i] = v_val
            M[i] = m_val
            
        return x, V, M
