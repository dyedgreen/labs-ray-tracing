"""
Provides geometry that can scatter / refract
the rays.
"""

import numpy as _np
from . import _utils as _u


# Abstract classes

class Geometry:
    """
    Base class for all geometry objects. Geometry
    objects are immutable.

    Notice that contains, intersect, and refract
    avoid runtime checks and expect correct
    arguments. This is done, since they will be
    called very often during the simulation.
    """

    def __init__(self, pos=_np.zeros(3), n=1.0):
        if type(pos) != _np.ndarray or len(pos) != 3:
            raise TypeError
        self._pos = pos
        self._n = float(n)

    @property
    def n(self):
        return self._n

    @property
    def pos(self):
        return self._pos

    @property
    def model(self):
        """
        Return points and triangulation that
        form (approximate) geometry wire-frame.
        This must also return the color
        desired when rendering.
        """
        raise NotImplementedError

    @property
    def color(self):
        """
        Color used for rendering objects.
        """
        return "#000000"

    def contains(self, pos):
        """
        Determine if pos is contained inside
        the object.
        """
        raise NotImplementedError

    def intersect(self, ray):
        """
        Determine if ray intersects and
        return the intersect. If the ray
        does not intersect, returns None.
        """
        raise NotImplementedError

    def normal(self, intersect):
        """
        Return surface normal at
        intersect.
        """
        raise NotImplementedError

    def refract(self, ray, intersect, n):
        """
        Refract the ray and update it's
        position and k vector. The refractive
        index of the medium that currently
        contains the ray is n.
        """
        raise NotImplementedError

    def __str__(self):
        return "{}(n={}, pos={})".format(type(self).__name__, self.n, self.pos)

    def __repr__(self):
        return str(self)

class Lens(Geometry):
    """
    Base class for lenses. Any lens will
    subclass this and it's respective geometry.
    """

    def refract(self, ray, intersect, n):
        # Obtain surface normal
        normal = self.normal(intersect)
        
        # Gather vector component perp. to
        # normal
        k_p = ray.k - normal * normal.dot(ray.k)
        k_p_vabs = _u.vabs(k_p)
        if  k_p_vabs != 0:
            k_p = k_p / k_p_vabs
        
        sin = n / self.n * k_p_vabs / _u.vabs(ray.k)

        # Root bottom elem
        root_bottom = (-1) * (sin - 1) * (sin + 1)
        if root_bottom <= 0:
            # Catch numeric errors
            root_bottom = 1e-30

        wavelength = ray.wavelength

        # Parallel component, magnitude 1
        k_para = ray.k - k_p * k_p_vabs
        k_para_vabs = _u.vabs(k_para)
        if k_para_vabs != 0:
            k_para = k_para / k_para_vabs

        # Perpendicular component + perpendicular component
        ray.k = \
            k_p * _u.sign(k_p_vabs) * abs(sin / _np.sqrt(root_bottom)) \
            + k_para

        ray.wavelength = wavelength

        # Update ray position
        ray.pos = intersect

class Mirror(Geometry):
    """
    Base class for mirrors.
    """

    def refract(self, ray, intersect, n):
        # Obtain surface normal
        normal = self.normal(intersect)

        # Flip the parallel k component
        k = ray.k - normal * 2 * normal.dot(ray.k)

        # Update k and pos
        ray.pos = intersect
        ray.k = k

# Geometry classes (abstract)

class Sphere(Geometry):
    """
    Represents a spherical surface. Refraction
    only occurs on the spherical surface.

    The lens is described by several parameters:
          -------|    /\\
         /       |    ||
       /         | aperture
     /           |    ||
    /  <-depth-> |    \\/
    | <-- 1/curvature -->  X (position)
    \\            |
     \\           |
       \\         |
         \\       |
          -------|

    <--- axis direction

    See self.pos for a note about position!
    """

    def __init__(self, curvature, aperture, depth, axis=_u.vec(0,0,1), **kwargs):
        super().__init__(**kwargs)
        if type(axis) != _np.ndarray or len(axis) != 3:
            raise TypeError
        if curvature == 0 or aperture > abs(1/curvature) or depth > abs(1/curvature):
            raise ValueError
        self.__crv = float(curvature)
        self.__apt = float(aperture)
        self.__dep = float(depth)
        self.__axi = axis / _u.vabs(axis)
        self.__rad = 1/self.__crv

    @property
    def pos(self):
        """
        This is the position of the sphere
        origin, as this is the most useful for
        calculations. However, the position
        given during construction is the position
        of the center of the spherical surface.
        """
        return self._pos - self.__rad * self.__axi

    @property
    def model(self):
        # We build the wire-frame
        # from the top down, in circles
        N = 8
        M = 16
        points = []
        _, x, y = _u.basis(self.__axi)
        if self.__rad > 0:
            # Positive curvature
            pos = self.pos + self.__axi * (self.__rad - self.__dep)
            for n in range(N):
                height = self.__dep * (1 - n/(N-1))
                radius = _np.sqrt(self.__rad**2 - height**2)
                origin = pos + self.__axi * height
                if n == 0:
                    points.append(origin)
                else:
                    for m in range(M):
                        theta = m*2*_np.pi/M
                        points.append(origin + min(radius, self.__apt) * (x * _np.cos(theta) + y * _np.sin(theta)))
        else:
            # Negative curvature
            pos = self.pos + self.__axi * self.__rad
            for n in range(N-1):
                height = - (self.__rad + _np.sqrt(self.__rad**2 - self.__apt**2)) * n/(N-1)
                radius = _np.sqrt(-2*height*self.__rad - height**2)
                origin = pos + self.__axi * height
                if n == 0:
                    points.append(origin)
                else:
                    for m in range(M):
                        theta = m*2*_np.pi/M
                        points.append(origin + radius * (x * _np.cos(theta) + y * _np.sin(theta)))
            for m in range(M):
                        theta = m*2*_np.pi/M
                        points.append(
                            pos - self.__axi*self.__dep + self.__apt * (x * _np.cos(theta) + y * _np.sin(theta))
                        )
        # Build triangles
        trigs = []
        # Top section
        for m in range(M-1):
            trigs.append((0, m+1, m+2))
        trigs.append((M, 1, 0))
        # Rings after top
        for n in range(0, N-2):
            for m in range(M-1):
                trigs.append((1+n*M+m, 1+(n+1)*M+m, 2+(n+1)*M+m))
                trigs.append((2+(n+1)*M+m, 2+n*M+m, 1+n*M+m))
            trigs.append((n*M+M, 1+(n+1)*M, 1+n*M))
            trigs.append(((n+2)*M, 1+(n+1)*M, n*M+M))
        return points, trigs, self.color

    def contains(self, pos):
        pr = pos - self.pos # pos relative to sphere origin
        p_axi = self.__axi.dot(pr) # projection on lens axis
        p_apt = _u.vabs(pr - self.__axi * p_axi) # projection on radial (aperture)

        eps = 1e-10 # Give some wiggle-room for rounding errors
        if self.__rad > 0:
            return \
                (self.__rad + eps) >= _u.vabs(pr) and \
                self.__apt + eps >= p_apt and \
                self.__rad - self.__dep <= p_axi + eps
        else:
            return \
                -(self.__rad + eps) <= _u.vabs(pr) and \
                self.__apt + eps >= p_apt and \
                p_axi < 0 and \
                self.__rad - self.__dep <= p_axi + eps

    def intersect(self, ray):
        # We don't intercept, if we are inside the
        # lens already
        if self.contains(ray.pos):
            return None
        # Find intersections of ray with sphere, then check
        # if the point is contained
        d = self.pos - ray.pos
        d_square = _u.vabs(d)**2
        r_square = self.__rad**2
        d_dot_k = d.dot(ray.k_hat)
        sqrt = _np.sqrt(abs(d_dot_k**2 - d_square + r_square))
        l_1 = d_dot_k + sqrt
        l_2 = d_dot_k - sqrt

        # We cant to check the smaller l first
        # Don't need absolute value, as l_n > 0
        # is enforced below
        if l_1 > l_2:
            l_1, l_2 = l_2, l_1

        # Check if contained
        inter_1 = ray.pos + l_1 * ray.k_hat
        inter_2 = ray.pos + l_2 * ray.k_hat

        if l_1 > 0 and self.contains(inter_1):
            return inter_1
        elif l_2 > 0 and self.contains(inter_2):
            return inter_2
        return None

    def normal(self, intersect):
        n = intersect - self.pos
        return n / _u.vabs(n)

class Plane(Geometry):
    """
    Represents a planar surface.

    The plane is described by a set
    of vectors.
     /\\
     || height
     ||
     ||
    (pos)-----> width

    The normal will be normalized for
    you and points upwards in the above
    picture. Note that the height and
    width and normal need to be orthogonal.
    """

    def __init__(self, normal=_u.vec(0,0,1), width=_u.vec(1,0,0), height=_u.vec(0,1,0), **kwargs):
        super().__init__(**kwargs)
        for vec in [normal, width, height]:
            if type(vec) != _np.ndarray or len(vec) != 3:
                raise TypeError
        eps = 1e-10
        if abs(normal.dot(width)) > eps or abs(normal.dot(height)) > eps or abs(width.dot(height)) > eps:
            raise ValueError("Need orthogonal vectors to specify plane")
        self.__n = normal
        self.__x = width
        self.__y = height
        self.__wid = _u.vabs(width)
        self.__hei = _u.vabs(height)
        self.__n = self.__n / _u.vabs(normal)
        self.__x = self.__x / self.__wid
        self.__y = self.__y / self.__hei

    @property
    def model(self):
        # This is a simple model
        points = [
            self.pos,
            self.pos + self.__x*self.__wid,
            self.pos + self.__y*self.__hei,
            self.pos + self.__x*self.__wid + self.__y*self.__hei,
        ]
        trigs = [(2, 1, 0), (1, 2, 3)]
        return points, trigs, self.color

    def contains(self, pos):
        pos = pos - self.pos
        z, x, y = self.__n.dot(pos), self.__x.dot(pos), self.__y.dot(pos)
        eps = 1e-10
        return \
            abs(z) < eps and \
            _u.sign(x) == _u.sign(self.__wid) and _u.sign(y) == _u.sign(self.__hei) and \
            abs(self.__wid) + eps >= abs(x) and 0 <= abs(x) and \
            abs(self.__hei) + eps >= abs(y) and 0 <= abs(y)

    def intersect(self, ray):
        a = ray.k_hat.dot(self.__n)
        if a == 0 or self.contains(ray.pos):
            return None
        d = (self.pos - ray.pos).dot(self.__n) / a
        if d >= 0:
            intersect = ray.pos + ray.k_hat * d
            return intersect if self.contains(intersect) else None
        return None

    def normal(self, intersect=None):
        return self.__n

# User classes

class SphereLens(Lens, Sphere):

    @property
    def color(self):
        return "#5555FF"

class PlaneLens(Lens, Plane):

    @property
    def color(self):
        return "#5555FF"

class SphereMirror(Mirror, Sphere):

    @property
    def color(self):
        return "#AAAA00"

class PlaneMirror(Mirror, Plane):

    @property
    def color(self):
        return "#AAAA00"

class Screen(Plane):
    """
    Implements an optical
    screen, used to record images.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__hits = []

    def refract(self, ray, intersect, n):
        # Update the ray and mark it as terminated
        ray.terminated = True
        ray.pos = intersect
        # Store the hit on the screen
        self.__hits.append(ray)

    def RMS(self, center):
        """
        Compute RMS of hits from
        center.
        """
        if not self.contains(center):
            raise ValueError("Center must be on screen")
        ms = sum([_u.vabs(h.pos - center)**2 for h in self.hits]) / len(self.hits)
        return _np.sqrt(ms)

    @property
    def hits(self):
        return self.__hits
