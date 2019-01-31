"""
Provides geometry that can scatter / refract
the rays.
"""

import numpy as _np
from . import _utils as _u

class Geometry:
    """
    Base class for all geometry objects. Geometry
    objects are immutable.

    Notice that contains, intersect, and refract
    do avoid runtime checks and expect correct
    arguments. This is done, since they will be
    called very often during the simulation.
    """

    def __init__(self, pos=_np.zeros(3), n=1.0):
        if type(pos) != _np.ndarray or len(pos) != 3:
            raise TypeError
        self._pos = pos
        self._n = float(n)

    @property
    def n(self):
        return self._n

    @property
    def pos(self):
        return self._pos

    def contains(self, pos):
        """
        Determine if pos is contained inside
        the object.
        """
        raise NotImplementedError

    def intersect(self, ray):
        """
        Determine if ray intersects and
        return the intersect. If the ray
        does not intersect, returns None.
        """
        raise NotImplementedError

    def normal(self, intersect):
        """
        Return surface normal at
        intersect.
        """
        raise NotImplementedError

    def refract(self, ray, intersect, n):
        """
        Refract the ray and update it's
        position and k vector. The refractive
        index of the medium that currently
        contains the ray is n.
        """
        # Obtain surface normal
        normal = self.normal(intersect)
        
        # Gather vector component perp. to
        # normal
        k_p = ray.k - normal * normal.dot(ray.k)
        k_p_vabs = _u.vabs(k_p)
        if  k_p_vabs != 0:
            k_p = k_p / k_p_vabs
        
        sin = n / self.n * k_p_vabs / _u.vabs(ray.k)

        # Root bottom elem
        root_bottom = (-1) * (sin - 1) * (sin + 1)
        if root_bottom == 0:
            # Catch numeric errors
            root_bottom = 1e-30

        wavelength = ray.wavelength

        # Parallel component, magnitude 1
        k_para = ray.k - k_p * k_p_vabs
        k_para_vabs = _u.vabs(k_para)
        if k_para_vabs != 0:
            k_para = k_para / k_para_vabs

        # Perpendicular component + perpendicular component
        ray.k = \
            k_p * _u.sign(k_p_vabs) * abs(sin / _np.sqrt(root_bottom)) \
            + k_para

        # ray.wavelength = wavelength
        # Update ray position
        ray.pos = intersect

    def __str__(self):
        return "{}(n={}, pos={})".format(type(self).__name__, self.n, self.pos)

    def __repr__(self):
        return str(self)

class Sphere(Geometry):
    """
    Represents a spherical surface lens. Refraction
    only occurs on the spherical surface.

    The lens is described by several parameters:
          -------|    /\\
         /       |    ||
       /         | aperture
     /           |    ||
    /  <-depth-> |    \\/
    | <-- 1/curvature -->  X (position)
    \\            |
     \\           |
       \\         |
         \\       |
          -------|

    <--- axis direction
    """

    def __init__(self, curvature, aperture, depth, axis=_np.array([0,0,1]), **kwargs):
        super().__init__(**kwargs)
        if type(axis) != _np.ndarray or len(axis) != 3:
            raise TypeError
        if curvature == 0 or aperture > abs(1/curvature) or depth > abs(1/curvature):
            raise ValueError
        self.__crv = float(curvature)
        self.__apt = float(aperture)
        self.__dep = float(depth)
        self.__axi = axis / _np.linalg.norm(axis)
        self.__rad = 1/self.__crv

    def contains(self, pos):
        pr = pos - self.pos # pos relative to sphere origin
        p_axi = self.__axi.dot(pr) # projection on lens axis
        p_apt = _u.vabs(pr - self.__axi * p_axi) # projection on radial (aperture)

        if self.__rad > 0:
            return self.__rad >= _u.vabs(pr) and self.__apt >= p_apt and self.__rad - self.__dep <= p_axi
        else:
            return -self.__rad <= _u.vabs(pr) and self.__apt >= p_apt and p_axi < 0 and self.__rad - self.__dep <= p_axi

    def intersect(self, ray):
        # We don't intercept, if we are inside the
        # lens already
        if self.contains(ray.pos):
            return None
        # Find intersections of ray with sphere, then check
        # if the point is contained
        d = self.pos - ray.pos
        d_square = _u.vabs(d)**2
        r_square = self.__rad**2
        d_dot_k = d.dot(ray.k_hat)
        sqrt = _np.sqrt(d_dot_k**2 - d_square + r_square)
        l_1 = d_dot_k + sqrt
        l_2 = d_dot_k - sqrt

        # We cant to check the smaller l first
        # Don't need absolute value, as l_n > 0
        # is enforced below
        if l_1 > l_2:
            l_1, l_2 = l_2, l_1

        # Check if contained
        inter_1 = ray.pos + l_1 * ray.k_hat
        inter_2 = ray.pos + l_2 * ray.k_hat

        if l_1 > 0 and self.contains(inter_1):
            return inter_1
        elif l_2 > 0 and self.contains(inter_2):
            return inter_2
        return None

    def normal(self, intersect):
        n = intersect - self.pos
        return n / _u.vabs(n)

class Screen(Geometry):
    """
    Implements an infinite optical
    screen, used to record images.
    """

    def __init__(self, normal=_np.array([0, 0, 1]), **kwargs):
        super().__init__(**kwargs)
        if type(normal) != _np.ndarray or len(normal) != 3:
            raise TypeError
        self.__nml = normal / _u.vabs(normal)
        self.__hits = []

    def contains(self, pos):
        return (self.pos - pos).dot(self.__nml) == 0

    def intersect(self, ray):
        a = ray.k_hat.dot(self.__nml)
        if a == 0:
            return ray.pos if self.contains(ray.pos) else None
        d = (self.pos - ray.pos).dot(self.__nml) / a
        if d >= 0:
            return ray.pos + ray.k_hat * d
        return None

    def normal(self, intersect=None):
        return self.__nml

    def refract(self, ray, intersect, n):
        # Update the ray and mark it as terminated
        ray.terminated = True
        ray.pos = intersect
        # Store the hit on the screen
        self.__hits.append(ray)

    @property
    def hits(self):
        return self.__hits
