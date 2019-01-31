"""
Provides graphic packages, that
render rays and screens.
"""

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as _plt

def render_3d(scene, extend=1.0):
    """
    Render all rays as 3d
    lines using matplotlib
    as a back-end.
    """
    fig = _plt.figure()
    ax = fig.gca(projection='3d')
    for ray in scene.rays:
        if len(ray.path) == 1:
            continue
        x = [pos[0] for pos in ray.path]
        y = [pos[1] for pos in ray.path]
        z = [pos[2] for pos in ray.path]
        if not ray.terminated:
            x.append(ray.pos[0] + ray.k[0] * extend)
            y.append(ray.pos[1] + ray.k[1] * extend)
            z.append(ray.pos[2] + ray.k[2] * extend)
        ax.plot(x, y, z)
    return fig