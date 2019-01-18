"""
Provides geometry that can scatter / refract
the rays.
"""

import numpy as _np

def vabs(vec):
    return _np.linalg.norm(vec)

class Geometry:
    """
    Base class for all geometry objects. Geometry
    objects are immutable, except for their base-
    properties pos and n.
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

class Sphere(Geometry):
    """
    Represents a spherical surface lens.
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
        pr = self.pos - pos # pos relative to sphere origin
        p_axi = self.__axi.dot(pr) # projection on lens axis
        p_apt = vabs(pr - self.__axi * p_axi) # projection on radial (aperture)

        if self.__rad > 0:
            return self.__rad <= vabs(pr) and self.__apt >= p_apt and self.__rad - self.__dep <= p_axi
        else:
            return -self.__rad >= vabs(pr) and self.__apt >= p_apt and p_axi < 0 and self.__rad - self.__dep <= p_axi

    def intersect(self, ray):
        pass

    def refract(self, ray):
        pass
