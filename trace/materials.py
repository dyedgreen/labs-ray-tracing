"""
Provides refractive
indices's for common
glasses.


Values obtained from:
M. N. Polyanskiy,
"Refractive index database,"
https://refractiveindex.info
[Accessed on 2019-02-05]
"""

import numpy as _np
from . import rays as _rays

# CODATA Constants
# ---
# Values obtained from:
# P. J. Mohr, B. N. Taylor, and D. B. Newell,
# "Codata recommended values of the fundamental physical constants: 2006,"
# Journal of Physical and Chemical Reference Data, vol. 37, no. 3, pp. 1187–1284, 2008.
c = 299792458.

def _f_to_l(f):
    return c / f

def _accept_ray(func):
    """
    Decorator for accepting
    rays of wavelengths
    """
    def wrapper(arg):
        if type(arg) == _rays.Ray:
            return func(_f_to_l(arg.frequency))
        elif arg is None:
            # When no ray is given, assume 500nm
            return func(500e-9)
        return func(float(arg))
    return wrapper

def sellmeier(wavelen, B, C):
    """
    Compute the Sellmeier refractive
    index for glasses. B and C are
    tuples that contain the Sellmeier
    constants.
    """
    l = (wavelen*1e6)**2
    return _np.sqrt(
        1 + \
        B[0] * l / (l - C[0]) + \
        B[1] * l / (l - C[1]) + \
        B[2] * l / (l - C[2])
    )


# Specific glasses

@_accept_ray
def BK7(wavelen):
    return sellmeier(
        wavelen,
        (1.03961212, 0.231792344, 1.01046945),
        (0.00600069867, 0.0200179144, 103.560653)
    )

@_accept_ray
def BAF10(wavelen):
    return sellmeier(
        wavelen,
        (1.5851495, 0.143559385, 1.08521269),
        (0.00926681282, 0.0424489805, 105.613573)
    )

@_accept_ray
def BAK1(wavelen):
    return sellmeier(
        wavelen,
        (1.12365662, 0.309276848, 0.881511957),
        (0.00644742752, 0.0222284402, 107.297751)
    )

@_accept_ray
def FK51A(wavelen):
    return sellmeier(
        wavelen,
        (0.971247817, 0.216901417, 0.904651666),
        (0.00472301995, 0.0153575612, 168.68133)
    )
