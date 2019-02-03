"""
Contains geometry objects and a ray
source.
"""

import numpy as _np
from . import _utils as _u
from . import geometry as _geo
from . import rays as _rays
from ._unsafe import Volatile

class Source:
    """
    A source that can spawn rays into
    a scene.
    """

    def __init__(self, pos=_u.pos(0,0,0), k=_u.vec(0, 0, 1)):
        if not type(pos) is _np.ndarray or len(pos) != 3:
            raise TypeError
        if not type(k) is _np.ndarray or len(k) != 3:
            raise TypeError
        self._pos = pos
        self._k = k

    def spawn(self):
        """
        Generate the rays.
        """
        raise NotImplementedError

class SpiralSource(Source):
    """
    Spawns rays from a circular
    surface. The rays are arranged
    in a spiral.
    """

    def __init__(self, radius=1, step=8, N=32, **kwargs):
        super().__init__(**kwargs)
        self.__rad = float(radius)
        self.__cap = int(N)
        self.__stp = int(step)

    def spawn(self):
        k, x, y = _u.basis(self._k)
        rays = []
        for i in range(self.__cap):
            theta = i * 2 * _np.pi / self.__stp
            r = self.__rad * i / self.__cap
            rays.append(
                _rays.Ray(origin=(self._pos + x*_np.cos(theta)*r + y*_np.sin(theta)*r), k=self._k)
            )
        return rays

class RadialSource(Source):
    """
    Spawn rays from a circular
    surface. The rays are 
    arranged in lines extending
    outwards.

    The step specifies the
    angular step, rings
    specifies the number of rings
    to generate.
    """

    def __init__(self, radius=1, step=8, rings=8, **kwargs):
        super().__init__(**kwargs)
        self.__rad = float(radius)
        self.__stp = int(step)
        self.__rng = int(rings)

    def spawn(self):
        k, x, y = _u.basis(self._k)
        rays = []
        for n in range(1, self.__rng + 1):
            r = self.__rad * n / self.__rng
            for i in range(self.__stp):
                theta = i * 2 * _np.pi / self.__stp
                rays.append(
                    _rays.Ray(origin=(self._pos + x*_np.cos(theta)*r + y*_np.sin(theta)*r), k=self._k)
                )
        return rays

class DenseSource(Source):
    """
    Spawn rays from a circular
    surface. The rays are
    arranged to have approximately
    uniform density.
    """

    def __init__(self, radius=1, density=8, **kwargs):
        super().__init__(**kwargs)
        self.__rad = float(radius)
        self.__den = float(density)

    def spawn(self):
        k, x, y = _u.basis(self._k)
        rays = []
        N = int(2 * self.__rad * self.__den)
        origin = self._pos - x*self.__rad - y*self.__rad
        for i in range(N):
            for j in range(N):
                pos = origin + x*2*i*self.__rad/N + y*2*j*self.__rad/N
                if _u.vabs(pos - self._pos) <= self.__rad:
                    rays.append(
                        _rays.Ray(origin=pos, k=self._k)
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

    def trace_ray(self, ray, max_steps=64):
        """
        Trace a single ray
        through the scene.
        """

        # Local helper functions
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

        step = 0
        intersect = None
        current_n = self.__n
        while not ray.terminated and step < max_steps:
            intersect, elem = next_intersect(ray)
            if intersect is None:
                break
            # TODO: Think about refracting in different directions -> different n order!
            elem.refract(ray, intersect, current_n)
            current_n = elem.n if isinstance(elem, _geo.Lens) else current_n
            step += 1

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
        for ray in self.__ray:
            self.trace_ray(ray, max_steps)

    def reset(self):
        """
        Creates a new scene from
        this one, by clearing all
        rays and removing any screen.

        Since sources and geometry
        objects are immutable, they
        are shared by the copied scene.
        """
        new_scene = Scene(n=self.__n)
        for elem in self.__geo:
            if isinstance(elem, Volatile):
                raise ValueError("Scene contains unsafe geometry")
            if not type(elem) == _geo.Screen:
                new_scene.add(elem)
        for src in self.__src:
            new_scene.add(src)
        return new_scene
