"""
Provides refractive
indices's for common
materials.


Values obtained from:
M. N. Polyanskiy,
"Refractive index database,"
https://refractiveindex.info
[Accessed on 2019-02-05]
"""

# CODATA Constants
# ---
# Values obtained from:
# P. J. Mohr, B. N. Taylor, and D. B. Newell,
# "Codata recommended values of the fundamental physical constants: 2006,"
# Journal of Physical and Chemical Reference Data, vol. 37, no. 3, pp. 1187–1284, 2008.
c = 299792458.

def _f_to_l(f):
    return c / f


