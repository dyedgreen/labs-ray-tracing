"""
Provides geometry that can scatter / refract
the rays.
"""

import numpy as _np
import _utils as _u

class Geometry:
    """
    Base class for all geometry objects. Geometry
    objects are immutable, except for their base-
    properties pos and n.

    Notice that contains, intersect, and refract
    do avoid runtime checks and expect correct
    arguments. This is done, since they will be
    called very often during the simulation.
    """

    def __init__(self, pos=_np.zeros(3), n=1.0):
        self._pos = _np.zeros(3)
        self._n = 1
        self.pos = pos
        self.n = n

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, val):
        if type(val) != float:
            raise TypeError
        if val < 1:
            raise ValueError("Expected n >= 1")
        self._n = val

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, val):
        if type(val) != type(self._pos) or len(val) != 3:
            raise TypeError
        self._pos = val

    def contains(self, pos):
        """
        Determine if pos is contained inside
        the object.
        """
        raise NotImplementedError

    def intersect(self, ray):
        """
        Determine if ray intersects and
        return the intersect.
        """
        raise NotImplementedError

    def refract(self, intersect, ray, n):
        """
        Refract the ray and update it's
        position and k vector.
        """
        raise NotImplementedError

    def __str__(self):
        return "{}(n={}, pos={})".format(type(self).__name__, self.n, self.pos)

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

        # Check if contained
        inter_1 = ray.pos + l_1 * ray.k_hat
        inter_2 = ray.pos + l_2 * ray.k_hat

        if self.contains(inter_1):
            return inter_1
        elif self.contains(inter_2):
            return inter_2
        return None

    def refract(self, ray, intersect):
        # Obtain basis for surface normal
        normal = intersect - self.pos
        n, x, y = _u.basis(normal)
        # Update k vector
        k_n = ray.k.dot(n)
        k_x = ray.k.dot(x)
        k_y = ray.k.dot(y)
        sin_1_inv = _u.vabs(ray.k) / k_n
        sqrt = np.sqrt(sin_1_inv**2 / 4 - k_x**2 - k_y**2)
        k_1 = sin_1_inv / 2 + sqrt
        k_2 = sin_1_inv / 2 - sqrt
        # Choose the one that is in the correct direction
        k_n = k_1 if k_1 * k_n >= 0 else k_2
        wavelen = ray.wavelength
        ray.k = n*k_n + x*k_x + y*k_y
        ray.wavelength = wavelen
        # Update ray position
        ray.pos = intersect
