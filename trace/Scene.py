"""
Contains geometry objects and a ray
source.
"""

import numpy as _np
from . import _utils as _u
from . import geometry as _geo
from . import rays as _rays

class Source:
    """
    A source that can spawn rays into
    a scene. Ray sources are circular
    and spawn N rays.
    Sources are immutable.
    """

    def __init__(self, pos, k, R=1, N=64):
        if not type(pos) is _np.ndarray or len(pos) != 3:
            raise TypeError
        if not type(k) is _np.ndarray or len(k) != 3:
            raise TypeError
        if R < 0 or N <= 0:
            raise ValueError
        self.__pos = pos
        self.__k = k
        self.__rad = R
        self.__cap = int(N)

    def spawn(self):
        """
        Generates N rays, spread radially
        outwards.
        """
        k, x, y = _u.basis(self.__k)
        rays = []
        for i in range(self.__cap):
            theta = i * 2 * _np.pi / 5
            r = self.__rad * i / self.__cap
            rays.append(
                _rays.Ray(origin=(x*_np.cos(theta)*r + y*_np.sin(theta)*r), k=self.__k)
            )
        return rays

class Scene:
    """
    A scene contains geometry, sources, and
    rays. It also runs the trace simulation.
    """

    def __init__(self):
        pass

    def add(self, element):
        """
        Add an element to the scene. Elements
        can be either geometry, rays or sources.
        """
        pass

    def trace(self, max_steps=64):
        pass