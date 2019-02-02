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
from . import _unsafe


class VolatileGeometry(_unsafe.Volatile, _geo.Geometry):
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

    def __getattribute__(self, name):
        if name in ["__init__", "__str__", "_VolatileGeometry__obj"]:
            return object.__getattribute__(self, name)
        return getattr(self.__obj, name)

    def __str__(self):
        return "Volatile" + str(self.__obj)

class VolatileMirror(VolatileGeometry, _geo.Mirror):

    def __init__(self, mirror):
        if not isinstance(mirror, _geo.Mirror):
            raise TypeError
        self.__obj = mirror

class VolatileScene(_unsafe.Volatile, _scene.Scene):
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

class Variable(float, _unsafe.Volatile):
    """
    Pass to mark parameters
    that should be varied.

    Note: The value set in
    the actual geometry instance
    is undefined until the object
    is made volatile.
    """

    # Global variable register
    _all = []

    def __init__(self, val):
        self._val = val
        self._closure = []
        self.__n = len(Variable._all)
        Variable._all.append(self)

    def __getattr__(self, name):
        return getattr(self._val, name)

    def __float__(self):
        # Note: This is somewhat of a hack: We mark
        # variables, by setting it to a very specific
        # float that is unlikely to occur...
        return 3063372375.0 + self.__n

    def __int__(self):
        # Note: See __float__
        return 3063372375 + self.__n

    def _register(self, closure):
        self._closure.append(closure)

    def set(self, value):
        """
        Update the variable
        """
        if len(self._closure) == 0:
            raise Exception("Container was not marked volatile")
        for closure in self._closure:
            closure(value)

def make_volatile(obj):
    """
    Makes any geometry object
    volatile. Mark the attribute
    you want to change, by
    passing Variable() to
    instantiate it.

    Only numerical attributes are
    supported.

    The objects passed should
    be considered unsafe after
    this function returns.

    Returns a VolatileGeometry
    object.
    """
    variables = []
    attributes = []
    for attr in dir(obj):
        if attr in obj.__dict__ and type(getattr(obj, attr)) in [float, int]:
            for var in Variable._all:
                if getattr(obj, attr) in [float(var), int(var)]:
                    variables.append(var)
                    if attr == "_Sphere__crv":
                        # Need extra catch here
                        attributes.append("_Sphere__rad")
                    else:
                        attributes.append(attr)
    def localize(attr):
        # Needed to get local copy of attr in for loop
        # when registering more than one variable
        if attr == "_Sphere__rad":
            var._register(lambda x: setattr(obj, attr, 1/float(x)))
        else:
            var._register(lambda x: setattr(obj, attr, float(x)))
    for var, attr in zip(variables, attributes):
        localize(attr)
        var.set(var._val)
    return VolatileMirror(obj) if isinstance(obj, _geo.Mirror) else VolatileGeometry(obj)
