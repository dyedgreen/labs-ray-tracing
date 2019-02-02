"""
Ray Tracing Module

Contains modules to assemble scenes
and trace rays through these scenes.

A scene can also be rendered in 3D.

Modules included are:
 - geometry (contains lenses, mirrors and screens)
 - graphics (render scenes and screens)
 - rays (ray class)
 - scene (contains scene and ray sources)

Convenience functions
included are:
 - vec (make a 3D vector)
 - pos (alias for vec)
 - basis (given a vector, make an orthonormal set)

Most user-facing classes are exposed directly
when importing trace.

For more detailed documentation please
refer to the modules and the included
demo.
"""

# Make packages available
from . import geometry
from . import graphics
from . import rays
from . import scene

# Make frequently used objects available directly
from .geometry import SphereLens, PlaneLens, Screen, SphereMirror, PlaneMirror
from .rays import Ray
from .scene import Scene, SpiralSource, RadialSource, DenseSource

# Helper for vectors
from ._utils import vec, pos, basis
