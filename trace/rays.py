"""
Provides Ray() objects.
"""

import numpy as _np
from . import _utils as _u

class Ray:
    """
    Ray()'s have a position, path and direction. They
    model optical rays.
    """

    def __init__(self, origin=_np.zeros(3), k=_np.zeros(3), frequency=1):
        self._path = []
        self._k = _np.zeros(3)
        self._f = 1.0
        self.pos = origin
        self.k = k
        self.frequency = frequency
        self.terminated = False # For use by simulation and screens

    @property
    def pos(self):
        return self[-1]

    @pos.setter
    def pos(self, val):
        if not type(val) == type(self._k) or len(val) != 3:
            raise TypeError
        self._path.append(val)

    @property
    def k(self):
        """
        Direction of light
        propagation
        """
        return self._k

    @property
    def k_hat(self):
        """
        Alias for k
        """
        return self._k

    @property
    def frequency(self):
        return self._f

    @k.setter
    def k(self, val):
        if not type(val) == type(self._k) or len(val) != 3:
            raise TypeError
        mag = _u.vabs(val)
        self._k = val / mag if mag != 0 else _np.zeros(3)

    @frequency.setter
    def frequency(self, val):
        self._f = float(val)

    @property
    def path(self):
        return self._path

    def intersect_axis(self, origin, axis):
        """
        Find the intersect of the ray with
        the given axis.
        Returns the closest points along
        the ray and axis.
        """
        a, b, c, d, e, f, g = \
            self.pos.dot(self.k), \
            self.k.dot(self.k), \
            self.k.dot(origin), \
            self.k.dot(axis), \
            self.pos.dot(axis), \
            origin.dot(axis), \
            axis.dot(axis)
        # Solve set of linear equations: closest points are pos + k * lam, origin + axis * gam
        bottom = b*g - d**2
        if bottom == 0:
            bottom = 1e-30
        lam = (-a*g + c*g + d*e - d*f) / bottom
        gam = (b*(e-f) - d*(a-c)) / bottom
        if lam < -1e-10:
            # The ray only goes forward
            return None, None
        return self.pos + self.k * lam, origin + axis * gam

    def __getitem__(self, *idx):
        return self.path.__getitem__(*idx)

    def __len__(self):
        return len(self.path)

    def __str__(self):
        return "Ray(k={}, path={})".format(self.k, self.path)

    def __repr__(self):
        return str(self)
