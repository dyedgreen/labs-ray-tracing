"""
Provides refractive
indices's for common
glasses.


Values obtained from:
M. N. Polyanskiy,
"Refractive index database,"
https://refractiveindex.info
https://github.com/polyanskiy/refractiveindex.info-database
[Accessed on 2019-02-05]

These values originate from
the Schott data sheet on
different types of glass.

https://www.schott.com/advanced_optics
https://www.schott.com/d/advanced_optics/ac85c64c-60a0-4113-a9df-23ee1be20428/1.1/schott-optical-glass-collection-datasheets-english-17012017.pdf
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

def accept_ray(func):
    """
    Decorator for accepting
    rays of wavelengths or
    wavelengths.

    This is useful when writing
    custom refractive index
    functions.
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

@accept_ray
def BK7(wavelen):
    return sellmeier(
        wavelen,
        (1.03961212, 0.231792344, 1.01046945),
        (0.00600069867, 0.0200179144, 103.560653)
    )

@accept_ray
def BAF10(wavelen):
    return sellmeier(
        wavelen,
        (1.5851495, 0.143559385, 1.08521269),
        (0.00926681282, 0.0424489805, 105.613573)
    )

@accept_ray
def BAK1(wavelen):
    return sellmeier(
        wavelen,
        (1.12365662, 0.309276848, 0.881511957),
        (0.00644742752, 0.0222284402, 107.297751)
    )

@accept_ray
def FK51A(wavelen):
    return sellmeier(
        wavelen,
        (0.971247817, 0.216901417, 0.904651666),
        (0.00472301995, 0.0153575612, 168.68133)
    )



# This is just here for fun / out of interest.
# These functions load glass types directly from
# the refractiveindex.info database and require
# network connection (although results are cached
# in memory)
#
# Note that the corresponding repo / website which
# sources this data may be lost at any time, so
# this is not guaranteed to work indefinitely.

from urllib.request import urlopen as _uopen

cache = {}
def online(glass_type):
    """
    Load refractive index
    directly from
    refractiveindex.info

    (requires network connection,
    but does cache results in
    memory)
    """
    if glass_type in cache:
        return cache[glass_type]
    else:
        B, C = (0,0,0), (0,0,0)
        url = "https://raw.githubusercontent.com/polyanskiy/refractiveindex.info-database/5ef7a728caf5040453ec67799f929abed37d8ebc/database/data/glass/schott/{}.yml".format(glass_type)
        with _uopen(url) as data:
            for line in data.readlines():
                line = line.decode("utf8").strip(" \n\t")
                if "coefficients" == line[:12]:
                    coeff = line[13:].split(" ")
                    B = (float(coeff[-6]), float(coeff[-4]), float(coeff[-2]))
                    C = (float(coeff[-5]), float(coeff[-3]), float(coeff[-1]))
                    break
        @accept_ray
        def ref_idx_fn(wavelen):
            return sellmeier(wavelen, B, C)
        cache[glass_type] = ref_idx_fn
        return ref_idx_fn

online_types =  [
    "BAFN6", "LF5HTi", "N-BK7HTi", "N-LAF36", "N-LASF46", "N-SF57HT", "N-ZK7A", "SF2", \
    "BK7G18", "LITHOSIL-Q", "N-F2", "N-LAF7", "N-LASF46A", "N-SF57HTultra", "P-BK7", \
    "SF4", "F2", "LITHOTEC-CAF2", "N-FK5", "N-LAK10", "N-LASF46B", "N-SF6", "P-LAF37", \
    "SF5", "F2G12", "LLF1", "N-FK51", "N-LAK12", "N-LASF9", "N-SF64", "P-LAK35", "SF56A", \
    "F2HT", "LLF1HTi", "N-FK51A", "N-LAK14", "N-LASF9HT", "N-SF66", "P-LASF47", "SF57", \
    "F5", "N-BAF10", "N-FK58", "N-LAK21", "N-PK51", "N-SF6HT", "P-LASF50", "SF57HTultra", \
    "FK3", "N-BAF3", "N-K5", "N-LAK22", "N-PK52A", "N-SF6HTultra", "P-LASF51", "SF6", \
    "FK5HTi", "N-BAF4", "N-KF9", "N-LAK33A", "N-PSK3", "N-SF8", "P-PK53", "SF66", "K10", \
    "N-BAF51", "N-KZFS11", "N-LAK33B", "N-PSK53", "N-SK10", "P-SF67", "SF6G05", "K5G20", \
    "N-BAF52", "N-KZFS2", "N-LAK34", "N-PSK53A", "N-SK11", "P-SF68", "SFL57", "K7", \
    "N-BAK1", "N-KZFS4", "N-LAK7", "N-SF1", "N-SK14", "P-SF69", "SFL6", "KZFS12", \
    "N-BAK2", "N-KZFS4HT", "N-LAK8", "N-SF10", "N-SK15", "P-SF8", "KZFSN4", "N-BAK4", \
    "N-KZFS5", "N-LAK9", "N-SF11", "N-SK16", "P-SK57", "LAFN7", "N-BAK4HT", "N-KZFS8", \
    "N-LASF31", "N-SF14", "N-SK2", "P-SK57Q1", "LAK9G15", "N-BALF4", "N-LAF2", "N-LASF31A", \
    "N-SF15", "N-SK2HT", "P-SK58A", "LAKL12", "N-BALF5", "N-LAF21", "N-LASF40", "N-SF19", \
    "N-SK4", "P-SK60", "LASF35", "N-BASF2", "N-LAF3", "N-LASF41", "N-SF2", "N-SK5", "SF1", \
    "LASFN9", "N-BASF64", "N-LAF32", "N-LASF43", "N-SF4", "N-SSK2", "SF10", "LF5", "N-BK10", \
    "N-LAF33", "N-LASF44", "N-SF5", "N-SSK5", "SF11", "LF5G15", "N-BK7", "N-LAF34", "N-LASF45", \
    "N-SF56", "N-SSK8", "SF14", "LF5G19", "N-BK7HT", "N-LAF35", "N-LASF45HT", "N-SF57", "N-ZK7", "SF15"
]
