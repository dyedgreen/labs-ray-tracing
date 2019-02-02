"""
Provides high performance optimizers
for specific situations, by utilizing
implementation details.

Basically, this module provides
mutable geometry types and scene
types.

Note that these are meant for
careful use within optimizers. No
runtime-checks are performed for
any mutation.
"""

from . import geometry as _geo
from . import scene as _scene
from ._unsafe import Volatile


class VolatileGeometry(Volatile, _geo.Geometry):
    """
    Base class for optim
    geometry objects. These
    objects can be mutated,
    but are less safe to
    use.

    They warp any other geometry
    object and make one of it's
    parameters mutable.
    """

    def __init__(self, obj):
        if not isinstance(obj, _geo.Geometry):
            raise TypeError
        self.__obj = obj

    def __getattr__(self, name):
        return getattr(self.__obj, name)

    def __str__(self):
        return "Volatile" + str(self.__obj)

class VolatileMirror(VolatileGeometry, _geo.Mirror):

    def __init__(self, mirror):
        if not isinstance(mirror, _geo.Mirror):
            raise TypeError
        self.__obj = mirror

class VolatileScene(_scene.Scene):
    """
    Unsafe version of scene, allowing
    things to be changed in place.
    """

    def reset():
        """
        Resets the scene
        in-place, removing
        any rays, wiping any
        screens.
        """
        self._Scene__ray = []
        self._Scene__steps = 0
        for geo in self.geometry:
            if type(geo) == _geo.Screen:
                geo._Screen__hits = []

def make_volatile(a, b):
    """
    Makes any geometry object
    volatile. Mark the attribute
    you want to change, by
    passing two instances, that
    differ by that attribute.

    Only numerical attributes are
    supported, and only one
    attribute may be volatile.

    The objects passed should
    be considered unsafe after
    this function returns.

    Returns a VolatileGeometry
    object and a function that
    accepts exactly one argument,
    which updates the value that
    differs between a and b.

    The returned object has the
    same attributes as a.
    """
    if type(a) is not type(b):
            raise TypeError("{} is not the same as {}".format(a, b))
    attrs_a = dir(a)
    attrs_b = dir(b)
    attr = None
    for attr_a in attrs_a:
        if attr_a in a.__dict__ and type(getattr(a, attr_a)) in [float, int]:
            # We know that the curvature is never used internally, discard:
            if attr_a == "_Sphere__crv":
                continue
            # Detect difference, raise error if multiple different
            if getattr(a, attr_a) != getattr(b, attr_a):
                if attr is not None:
                    raise Exception("Multiple parameters differ")
                attr = attr_a
    # Know detail about spheres: radius is set as inverse (curvature)
    if attr == "_Sphere__rad":
        def update(new_value):
            setattr(a, attr, 1/float(new_value))
    else:
        def update(new_value):
            setattr(a, attr, float(new_value))
    volatile_a = VolatileMirror(a) if isinstance(a, _geo.Mirror) else VolatileGeometry(a)
    return volatile_a, update
