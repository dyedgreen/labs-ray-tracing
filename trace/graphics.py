"""
Provides graphic packages, that
render rays and screens.
"""

import numpy as _np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as _plt

from . import materials as _m
from . import _utils as _u


def render_3d(scene, extend=1.0, plot_free=True, labels=True, chromatic=False):
    """
    Render all rays in scene
    as 3d lines using matplotlib
    as a back-end.
    """
    fig = _plt.figure()
    ax = fig.gca(projection='3d')
    for ray in scene.rays:
        if len(ray.path) == 1 and not plot_free:
            continue
        x = [pos[0] for pos in ray.path]
        y = [pos[1] for pos in ray.path]
        z = [pos[2] for pos in ray.path]
        if not ray.terminated:
            x.append(ray.pos[0] + ray.k[0] * extend)
            y.append(ray.pos[1] + ray.k[1] * extend)
            z.append(ray.pos[2] + ray.k[2] * extend)
        if not chromatic:
            ax.plot(x, y, z)
        else:
            ax.plot(x, y, z, color=ray_to_color(ray))
    for geo in scene.geometry:
        points, triangles, color = geo.model
        x = _np.array([pos[0] for pos in points])
        y = _np.array([pos[1] for pos in points])
        z = _np.array([pos[2] for pos in points])
        ax.plot_trisurf(x, y, triangles, z, alpha=0.3, color=color)
        if labels:
            ax.text3D(*geo._pos, str(geo))
    return fig

def render_2d(screen):
    """
    Render all rays that hit
    a screen using matplotlib
    as a back-end.
    """
    fig, ax = _plt.subplots()
    n, x, y = _u.basis(screen.normal())
    for ray in screen.hits:
        ax.scatter(x.dot(ray.pos),y.dot(ray.pos))
    return fig

def ray_to_color(ray):
    """
    Used by render_3d to display
    rays in their chromatic color.

    Approximation based on: Earl F. Glynn's
    http://www.efg2.com/Lab/ScienceAndEngineering/Spectra.htm
    """
    gamma = .8
    intensity_max = 255

    l = _m._f_to_l(ray.frequency) * 1e9

    # Something about vision limits
    fac = 0
    if l >= 380 and l < 420:
        fac = 0.3 + 0.7 * (l - 380) / 40
    elif l >= 420 and l < 701:
        fac = 1
    elif l > 701 and l < 781:
        f = 0.3 + 0.7 * (780 - l) / 80

    # Red Green Blue
    r, g, b = 0, 0, 0
    if l >= 380  and l < 440:
        r = (440 - l) / 60
        g, b = 0, 1
    elif l >= 440 and l < 490:
        g = (l - 440) / 50
        r, b = 0, 1
    elif l >= 490 and l < 510:
        r, g = 0, 1
        b = (510 - l) / 20
    elif l >= 510 and l < 580:
        r = (l - 510) / 70
        g, b = 1, 0
    elif l >= 580 and l < 645:
        g = (645 - l) / 65
        r, b = 1, 0
    elif l >= 645 and l < 781:
        r, g, b = 1, 0, 0

    r = int(round(intensity_max * (r * fac)**gamma)) if r != 0 else 0
    g = int(round(intensity_max * (g * fac)**gamma)) if g != 0 else 0
    b = int(round(intensity_max * (b * fac)**gamma)) if b != 0 else 0

    return "#" + "".join(["{:02X}".format(n) for n in (r, g, b)])
