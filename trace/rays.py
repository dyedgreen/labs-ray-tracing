"""
Provides Ray() objects
"""

import numpy as _np

class Ray:
    """
    Ray()'s have a position, path and direction. They
    model optical rays.
    """

    def __init__(self, origin=_np.zeros(3)):
        self._path = []
        self._k = _np.zeros(3)
        self.pos = origin

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

    @k.setter
    def k(self, val):
        if not type(val) == type(self._k) or len(val) != 3:
            raise TypeError
        self._k = val

    @property
    def path(self):
        return self._path

    def __getitem__(self, *idx):
        return self.path.__getitem__(*idx)

    def __len__(self):
        return len(self.path)

    def __str__(self):
        return "Ray(k={}, path={})".format(self.k, self.path)
