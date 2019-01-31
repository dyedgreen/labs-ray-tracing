"""
Provides internal utility functions.
"""

import numpy as _np

def vabs(vec):
    """
    Vector norm
    """
    return _np.linalg.norm(vec)

def basis(x):
    """
    Construct orthonormal basis containing (normalized) x.
    """
    x = x / vabs(x)
    y = _np.array([1, 1, 1], dtype=float)
    y = y - x * x.dot(y)
    y = y / vabs(y)
    z = _np.cross(x, y)
    return (x, y, z)

def sign(x):
    return 1 if x >= 0 else -1

def vec(x, y, z):
    return _np.array([x, y, z])

def pos(x, y, z):
    return vec(x, y, z)
