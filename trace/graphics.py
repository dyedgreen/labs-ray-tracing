"""
Provides graphic packages, that
render rays and screens.
"""

import numpy as _np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as _plt

from . import _utils as _u


def render_3d(scene, extend=1.0, plot_free=True):
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
        ax.plot(x, y, z)
    for geo in scene.geometry:
        points, triangles, color = geo.model
        x = _np.array([pos[0] for pos in points])
        y = _np.array([pos[1] for pos in points])
        z = _np.array([pos[2] for pos in points])
        ax.plot_trisurf(x, y, triangles, z, alpha=0.3, color=color)
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
