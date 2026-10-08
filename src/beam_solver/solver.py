"""2D Euler-Bernoulli beam solver using stiffness method."""

from dataclasses import dataclass, field
import numpy as np


@dataclass
class Support:
    position: float          # x-coordinate along the beam (m)
    ux: bool = False         # horizontal restraint
    uy: bool = True          # vertical restraint
    rz: bool = False         # rotational restraint


@dataclass
class PointLoad:
    position: float
    fz: float                # downward load magnitude (N, positive = down)


@dataclass
class DistributedLoad:
    start: float
    end: float
    w_start: float           # N/m at start
    w_end: float = None      # N/m at end (default = w_start for uniform)


@dataclass
class Beam:
    length: float            # m
    E: float                 # Young's modulus (Pa)
    I: float                 # second moment of area (m^4)
    supports: list = field(default_factory=list)
    point_loads: list = field(default_factory=list)
    dist_loads: list = field(default_factory=list)

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
            w_avg = (dl.w_start + (dl.w_end if dl.w_end is not None else dl.w_start)) / 2.0
            span_len = dl.end - dl.start
            load_mag = w_avg * span_len
            centroid = (dl.start + dl.end) / 2.0
            total_load += load_mag
            moment_about_s1 += load_mag * (centroid - s1)
            
        R2 = moment_about_s1 / L_span
        R1 = total_load - R2
        return {0: R1, 1: R2}

    def shear_moment(self, n_points=500):
        """Return arrays (x, V, M) along the beam."""
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
                    w = dl.w_start
                    eff_len = min(xi, dl.end) - dl.start
                    w_load = w * eff_len
                    v_val += w_load
                    m_val -= w_load * (eff_len / 2.0 + max(0, xi - dl.end))
                    
            V[i] = v_val
            M[i] = m_val
            
        return x, V, M
