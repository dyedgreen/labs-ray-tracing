"""
Provides geometry that can scatter / refract
the rays.
"""

import numpy as _np

class Geometry:
    """
    Base class for all geometry objects.
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
        val = float(val)
        if val < 1:
            raise TypeError("Expected n >= 1")
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

class Sphere:
    """
    Represents a spherical surface.
    """

    def __init__(self, curvature, apature, axis=_np.array([0,0,1]), **kwargs):
        super().__init__(**kwargs)
        if type(axis) != _np.ndarray or (curvature != 0 and apature > abs(1/curvature)):
            raise TypeError
        self.__crv = curvature
        self.__apt = apature
        self.__axi = axis

    def intersect(self, ray):
        pass

    def refract(self, ray):
        pass
