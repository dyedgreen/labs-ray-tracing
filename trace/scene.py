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

    def __init__(self, pos, k, R=1, N=64, step=20):
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
        self.__stp = int(step)

    def spawn(self):
        """
        Generates N rays, spread radially
        outwards.
        """
        k, x, y = _u.basis(self.__k)
        rays = []
        for i in range(self.__cap):
            theta = i * 2 * _np.pi / self.__stp
            r = self.__rad * i / self.__cap
            rays.append(
                _rays.Ray(origin=(self.__pos + x*_np.cos(theta)*r + y*_np.sin(theta)*r), k=self.__k)
            )
        return rays

class Scene:
    """
    A scene contains geometry, sources, and
    rays. It also runs the trace simulation.
    """

    def __init__(self, n=1):
        self.__n = n # refractive index of vacuum
        self.__ray = []
        self.__geo = []
        self.__src = []
        self.__steps = 0

    def add(self, *elements):
        """
        Add one ore mote elements to the scene.
        Elements can be either geometry, rays
        or sources.
        """
        for elem in elements:
            self._add(elem)

    def _add(self, element):
        if isinstance(element, Source):
            self.__src.append(element)
        elif isinstance(element, _rays.Ray):
            self.__ray.append(element)
        elif isinstance(element, _geo.Geometry):
            self.__geo.append(element)
        else:
            raise TypeError("Scene can not contain element of type {}".format(type(element)))

    @property
    def rays(self):
        return self.__ray

    @property
    def geometry(self):
        return self.__geo

    @property
    def sources(self):
        return self.__src

    @property
    def elements(self):
        return [*self.__ray, *self.__geo, *self.__src]

    def trace(self, max_steps=64):
        """
        Trace all rays through the scene. Takes
        at most max_steps steps per ray. If no
        trace has run previously, it will also
        spawn new rays from any present sources.
        """
        if self.__steps == 0:
            for src in self.__src:
                rays = src.spawn()
                for r in rays:
                    self.add(r)
        self.__steps += max_steps # Record number of steps attempted

        # Run trace for each ray, this works since rays
        # don't interact with each other
        def curr_container(ray):
            for elem in self.__geo:
                if elem.contains(ray):
                    return elem
            return None

        def next_intersect(ray):
            intersect = None
            intersect_elem = None
            dist = float("inf")
            for elem in self.__geo:
                i = elem.intersect(ray)
                if i is not None:
                    dist_i = _u.vabs(ray.pos - i)
                    if dist_i < dist:
                        intersect = i
                        intersect_elem = elem
                        dist = dist_i
            return intersect, intersect_elem

        for ray in self.__ray:
            step = 0
            intersect = None
            current_n = self.__n # Test if good choice...
            while not ray.terminated and step < max_steps:
                intersect, elem = next_intersect(ray)
                if intersect is None:
                    break
                # TODO: Think about refracting in different directions -> different n order!
                elem.refract(ray, intersect, current_n)
                current_n = elem.n
                step += 1

    def reset(self):
        """
        Creates a new scene from
        this one, by clearing all
        rays and creating new
        screens.

        Since sources and geometry
        objects are immutable, they
        are shared by the copied scene.
        """
        new_scene = Scene(n=self.__n)
        for elem in self.__geo:
            if type(elem) == _geo.Screen:
                new_scene.add(_geo.Screen(normal=elem.normal(), pos=elem.pos))
            else:
                new_scene.add(elem)
        for src in self.__src:
            new_scene.add(src)
        return new_scene
