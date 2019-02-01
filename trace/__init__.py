"""
Ray Tracing Module

FIXME: Add more detailed docs here...
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
