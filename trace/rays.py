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

    def __init__(self, origin=_np.zeros(3), k=_np.zeros(3)):
        self._path = []
        self._k = _np.zeros(3)
        self.pos = origin
        self.k = k
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
        return self._k

    @property
    def k_hat(self):
        return self._k / _u.vabs(self._k)

    @property
    def wavelength(self):
        return 2 * _np.pi / _u.vabs(self._k)

    @k.setter
    def k(self, val):
        if not type(val) == type(self._k) or len(val) != 3:
            raise TypeError
        self._k = val

    @wavelength.setter
    def wavelength(self, val):
        self.k = 2 * _np.pi / float(val) * self.k_hat

    @property
    def path(self):
        return self._path

    def __getitem__(self, *idx):
        return self.path.__getitem__(*idx)

    def __len__(self):
        return len(self.path)

    def __str__(self):
        return "Ray(k={}, path={})".format(self.k, self.path)

    def __repr__(self):
        return str(self)
