"""
Provides unit tests
"""

import unittest
import numpy as np
import random as rand
from trace import rays
from trace import geometry
from trace import scene
from trace import _utils


class MockGeometryNormal:
    """
    Wrapper for geometry
    types that implements
    a normal. This is used
    to test abstract geometry
    classes.
    """

    def __init__(self, geo_obj, normal=_utils.vec(0,0,1)):
        self._obj = geo_obj
        self._normal = normal / _utils.vabs(normal)

    def __getattribute__(self, name):
        if name in ["__init__", "_obj", "_normal", "normal"]:
            return object.__getattribute__(self, name)
        attr = object.__getattribute__(self._obj, name)
        if callable(attr):
            # Wrapper proxies self to
            # allow access to normal
            # from methods
            def wrapper(*args, **kwargs):
                return getattr(type(self._obj), name)(self, *args, **kwargs)
            return wrapper
        else:
            return attr

    def normal(self, intersect):
        return self._normal


class TestCase(unittest.TestCase):

    def assertSameArray(self, a, b):
        """
        Helper to compare arrays
        """
        if not np.array_equal(a, b):
            raise AssertionError("{} is not {}".format(a, b))

    def assertApproxArray(self, a, b, eps=1e-10):
        """
        assertAlmostEqual() for arrays
        """
        lower = a - np.full_like(a, eps, dtype=float)
        upper = a + np.full_like(a, eps, dtype=float)
        if not np.all(np.less(lower, b)) or not np.all(np.less(b, upper)):
            raise AssertionError("{} is not approximately {}".format(a, b))

class TestUtils(TestCase):

    def test_vabs(self):
        arr = np.array([5, 0, 0])
        self.assertEqual(_utils.vabs(arr), 5)

        arr = np.array([2, 2, 1])
        self.assertEqual(_utils.vabs(arr), 3)

    def test_basis(self):
        x_list = [
            np.array([1, 5, 2]),
            np.array([-1, 3, 1]),
            np.array([234, -7, 45.8]),
            np.array([-31, 6.5, -2.67]),
        ]
        for a in x_list:
            x, y, z = _utils.basis(a)

            self.assertAlmostEqual(x.dot(a), np.sqrt(a.dot(a)))

            self.assertAlmostEqual(1, x.dot(x))
            self.assertAlmostEqual(0, y.dot(x))
            self.assertAlmostEqual(0, z.dot(x))

            self.assertAlmostEqual(0, x.dot(y))
            self.assertAlmostEqual(1, y.dot(y))
            self.assertAlmostEqual(0, z.dot(y))

            self.assertAlmostEqual(0, x.dot(z))
            self.assertAlmostEqual(0, y.dot(z))
            self.assertAlmostEqual(1, z.dot(z))

    def test_sign(self):
        cases_pos = [2,34,456.45,23.1,34.0,1e-15]
        cases_neg = [-2,-34,-456.45,-23.1,-34.0,-1e-15]

        for val in cases_pos:
            self.assertEqual(1, _utils.sign(val))

        for val in cases_neg:
            self.assertEqual(-1, _utils.sign(val))

        self.assertEqual(0, _utils.sign(0))

    def test_vec(self):
        vec = _utils.vec(1, 2, 3)
        self.assertTrue(type(vec) == np.ndarray)
        self.assertTrue(len(vec) == 3)
        self.assertEqual(vec[0], 1)
        self.assertEqual(vec[1], 2)
        self.assertEqual(vec[2], 3)

    def test_pos(self):
        pos = _utils.pos(1, 2, 3)
        self.assertTrue(type(pos) == np.ndarray)
        self.assertTrue(len(pos) == 3)
        self.assertEqual(pos[0], 1)
        self.assertEqual(pos[1], 2)
        self.assertEqual(pos[2], 3)

class TestRays(TestCase):

    def test_properties(self):
        origin = np.array([1,2,3], dtype=float)
        ray = rays.Ray(origin=origin)

        self.assertSameArray(ray.pos, origin)
        ray.k = origin * 3
        self.assertSameArray(ray.k, origin * 3)

        ray.pos = origin + origin
        self.assertTrue(len(ray) == 2)

        self.assertSameArray(ray.pos, ray[-1])
        self.assertEqual(len(ray), len(ray.path))
        self.assertSameArray(ray[0], ray.path[0])

        wavelen = 1
        ray.wavelength = wavelen
        self.assertAlmostEqual(wavelen, ray.wavelength)

        ray.k = np.array([1, 0, 0])
        self.assertAlmostEqual(ray.wavelength, 2 * np.pi)

        with self.assertRaises(TypeError):
            ray.k = [1,2,3]

        with self.assertRaises(TypeError):
            ray.pos = 6.4

        with self.assertRaises(ValueError):
            ray.wavelength = "Hello World!"

    def test_defaults(self):
        ray = rays.Ray()
        self.assertSameArray(ray.pos, np.zeros(3))
        self.assertSameArray(ray.k, np.zeros(3))

    def test_intersect_axis(self):
        ray = rays.Ray(k=_utils.vec(0,0,1))
        origin = _utils.pos(1,0,1)
        axis = _utils.vec(0,1,0)

        pt_ray, pt_axi = ray.intersect_axis(origin, axis)
        self.assertApproxArray(pt_ray, _utils.pos(0,0,1))
        self.assertApproxArray(pt_axi, _utils.pos(1,0,1))
        self.assertAlmostEqual(_utils.vabs(pt_ray-pt_axi), 1)

class TestGeometry(TestCase):

    def test_properties(self):
        generic = geometry.Geometry(n=4.3)

        self.assertEqual(generic.n, 4.3)

        generic = geometry.Geometry(np.array([3,6,8]))
        self.assertSameArray(generic.pos, np.array([3,6,8]))


    def test_defaults(self):
        generic = geometry.Geometry()
        self.assertSameArray(generic.pos, np.zeros(3))
        self.assertSameArray(generic.n, 1)

    def test_abstracts(self):
        generic = geometry.Geometry()

        with self.assertRaises(NotImplementedError):
            generic.contains(None)

        with self.assertRaises(NotImplementedError):
            generic.intersect(None)

        with self.assertRaises(NotImplementedError):
            generic.normal(None)

        with self.assertRaises(NotImplementedError):
            generic.refract(None, None, None)

class TestGeometryLens(TestCase):

    def test_implements_refract(self):
        lens = geometry.Lens()
        self.assertTrue(callable(lens.refract))

    def test_refract(self):
        # Check it updates position
        lens = MockGeometryNormal(geometry.Lens())
        ray = rays.Ray(k=_utils.vec(0,1,1))
        new_pos = _utils.pos(10, 34.2, -70)
        lens.refract(ray, new_pos, 1)
        self.assertSameArray(new_pos, ray.pos)

        # Check Babinet’s principle holds
        tests = [
            (_utils.vec(5,0,0), _utils.vec(1,0,0), 1, 2),
            (_utils.vec(1,3,5), _utils.vec(1,-2,7), 1, 3.1),
            (_utils.vec(0.246,5.8,24.9), _utils.vec(45.6,-2.888,3.1), 1, 1.1),
            (_utils.vec(-3,1.8,0), _utils.vec(1.7,2.2,-1), 1, 7.24),
            (_utils.vec(43.4,9.38,-5), _utils.vec(-1.7,22,-1), 2.1, 4.15),
            (_utils.vec(1.4,2.8,3.9), _utils.vec(-1.7,22,-1), 2, 2),
        ]
        def angle(a, b):
            return np.arccos(abs(a.dot(b) / _utils.vabs(a) / _utils.vabs(b)))
        for k, normal, n_prev, n_lens in tests:
            lens = MockGeometryNormal(geometry.Lens(n=n_lens), normal)
            ray = rays.Ray(k=k)

            n_1_sin_1 = n_prev * np.sin(angle(ray.k, normal))
            wave_1 = ray.wavelength
            lens.refract(ray, np.zeros(3), n_prev)
            n_2_sin_2 = n_lens * np.sin(angle(ray.k, normal))
            wave_2 = ray.wavelength

            self.assertAlmostEqual(n_1_sin_1, n_2_sin_2)
            self.assertAlmostEqual(wave_1, wave_2)

class TestGeometryMirror(TestCase):

    def test_implements_refract(self):
        mirror = geometry.Mirror()
        self.assertTrue(callable(mirror.refract))

    def test_refract(self):
        # Check it updates position
        mirror = MockGeometryNormal(geometry.Mirror())
        ray = rays.Ray(k=_utils.vec(0,1,1))
        new_pos = _utils.pos(10, 34.2, -70)
        mirror.refract(ray, new_pos, 1)
        self.assertSameArray(new_pos, ray.pos)

        # Check angle in is angle out
        tests = [
            (_utils.vec(5,0,0), _utils.vec(1,0,0), 1, 2),
            (_utils.vec(1,3,5), _utils.vec(1,-2,7), 1, 3.1),
            (_utils.vec(0.246,5.8,24.9), _utils.vec(45.6,-2.888,3.1), 1, 1.1),
            (_utils.vec(-3,1.8,0), _utils.vec(1.7,2.2,-1), 1, 7.24),
            (_utils.vec(43.4,9.38,-5), _utils.vec(-1.7,22,-1), 2.1, 4.15),
        ]
        def angle(a, b):
            return np.arccos(abs(a.dot(b) / _utils.vabs(a) / _utils.vabs(b)))
        for k, normal, n_prev, n_lens in tests:
            mirror = MockGeometryNormal(geometry.Mirror(n=n_lens), normal)
            ray = rays.Ray(k=k)

            ang_1 = angle(ray.k, normal)
            wave_1 = ray.wavelength
            mirror.refract(ray, np.zeros(3), n_prev)
            ang_2 = angle(ray.k, normal)
            wave_2 = ray.wavelength

            self.assertAlmostEqual(ang_1, ang_2)
            self.assertAlmostEqual(wave_1, wave_2)

class TestGeometrySplitter(TestCase):

    def test_implements_refract(self):
        splitter = geometry.Splitter()
        self.assertTrue(callable(splitter.refract))

    def test_refract(self):
        # As refract in Splitter invokes
        # super, our proxy class will
        # cause runtime errors
        class MockSplitter(geometry.Splitter):
            def normal(*_):
                return _utils.vec(0,0,1)

        # Check it updates position
        splitter = MockSplitter()
        ray = rays.Ray(k=_utils.vec(0,1,1))
        new_pos = _utils.pos(10, 34.2, -70)
        splitter.refract(ray, new_pos, 1)
        self.assertSameArray(new_pos, ray.pos)

        # Check angle in is angle out
        tests = [
            (_utils.vec(5,0,0), 1, 2),
            (_utils.vec(1,3,5), 1, 3.1),
            (_utils.vec(0.246,5.8,24.9), 1, 1.1),
            (_utils.vec(-3,1.8,0), 1, 7.24),
            (_utils.vec(43.4,9.38,-5), 2.1, 4.15),
        ]
        def angle(a, b):
            return np.arccos(abs(a.dot(b) / _utils.vabs(a) / _utils.vabs(b)))
        for k, n_prev, n_lens in tests:
            splitter = MockSplitter(n=n_lens)
            ray = rays.Ray(k=k)

            ang_1 = angle(ray.k, splitter.normal())
            wave_1 = ray.wavelength
            splitter.refract(ray, np.zeros(3), n_prev)
            ang_2 = angle(ray.k, splitter.normal())
            wave_2 = ray.wavelength

            self.assertAlmostEqual(ang_1, ang_2)
            self.assertAlmostEqual(wave_1, wave_2)

class TestGeometrySphere(TestCase):

    def test_properties(self):
        sphere = geometry.Sphere(1, 1, 1, axis=np.array([3, 5, 8]))
        self.assertEqual(_utils.vabs(sphere._Sphere__axi), 1)

        with self.assertRaises(ValueError):
            geometry.Sphere(1, 2, 1)

        with self.assertRaises(ValueError):
            geometry.Sphere(1, 1, 2)

        with self.assertRaises(TypeError):
            geometry.Sphere(True, None, "Happy")

    def test_defaults(self):
        lens = geometry.Sphere(1, 1, 1)
        self.assertSameArray(lens._Sphere__axi, np.array([0,0,1]))

    def test_contains(self):
        lens = geometry.Sphere(1, 0.5, 0.5, axis=np.array([1, 0, 0]), pos=_utils.pos(1,0,0))
        are_in = [
            np.array([0.5, 0, 0]),
            np.array([1.0, 0, 0]),
            np.array([0.5, 0.1, 0.1]),
            np.array([0.5, -0.1, 0.1]),
        ]
        are_out = [
            np.array([0.4, 0, 0]),
            np.array([1.0, 0.01, 0]),
            np.array([-0.5, 0.1, 0.1]),
            np.array([0.2, 0.5, 0.5]),
        ]
        for pos in are_in:
            self.assertTrue(lens.contains(pos))
        for pos in are_out:
            self.assertFalse(lens.contains(pos))

    def test_intersect(self):
        lens = geometry.Sphere(1, 1, 1, pos=_utils.pos(0,0,1))
        ray = rays.Ray(origin=np.array([0, 0, 2]))

        ray.k = np.array([0, 0, -1])
        self.assertSameArray(lens.intersect(ray), np.array([0,0,1]))
        ray.k = np.array([0, 1, -2])
        self.assertApproxArray(lens.intersect(ray), np.array([0,.6,.8]))

        ray.pos = np.array([0, 0, 0.1])
        ray.k = np.array([0, 0, 1])
        self.assertEqual(None, lens.intersect(ray))

        ray.pos = np.array([0, 0, -1])
        ray.k = np.array([0, 0, -1])
        self.assertEqual(None, lens.intersect(ray))

        ray = rays.Ray(origin=np.array([-1, 0, 2]))
        ray.k = np.array([1, 0, -1])
        self.assertApproxArray(np.array([0, 0, 1]), lens.intersect(ray))

        with self.assertRaises(AttributeError):
            lens.intersect(None)

    def test_normal(self):
        lens = geometry.Sphere(1, 1, 1, pos=_utils.pos(0,0,0))
        normal = _utils.vec(0,0,1)
        self.assertSameArray(normal, lens.normal(_utils.pos(0,0,0)))

class TestGeometryPlane(TestCase):

    def test_properties(self):
        # Defaults
        plane = geometry.Plane()
        self.assertSameArray(np.array([0, 0, 1]), plane.normal())

        # Normalizes
        normals = [np.array([0, 0, 7]), np.array([0, 0, 23.6]), np.array([0, .0, -2.47])]
        for n in normals:
            plane = geometry.Plane(normal=n)
            self.assertAlmostEqual(1, _utils.vabs(plane.normal()))

        plane = geometry.Plane(pos=np.array([-0.5, -0.5, 1]))

        ray = rays.Ray()
        ray.k = np.array([0, 0, 1])
        self.assertSameArray(np.array([0, 0, 1]), plane.intersect(ray))

        ray = rays.Ray()
        ray.k = np.array([1, 1, 0])
        self.assertSameArray(None, plane.intersect(ray))

        ray = rays.Ray()
        ray.k = np.array([0, 0, -1])
        self.assertSameArray(None, plane.intersect(ray))

    def test_contains(self):
        plane = geometry.Plane(pos=np.zeros(3), width=_utils.vec(1,0,0), height=_utils.vec(0,1,0))

        self.assertTrue(plane.contains(_utils.pos(0.5, 0.5, 0)))
        self.assertTrue(plane.contains(_utils.pos(1e-20, 1e-20, 0)))
        self.assertTrue(plane.contains(_utils.pos(0.5, 0.5, 0+1e-30)))

        self.assertFalse(plane.contains(_utils.pos(1.5, 0.5, 0)))
        self.assertFalse(plane.contains(_utils.pos(0, -0.5, 0)))
        self.assertFalse(plane.contains(_utils.pos(0.5, 0.5, 0.1)))

    def test_intersect(self):
        plane = geometry.Plane(pos=np.zeros(3), width=_utils.vec(1,0,0), height=_utils.vec(0,1,0))

        ray = rays.Ray(_utils.pos(.5,.5,7), k=_utils.vec(0,0,-1))
        self.assertApproxArray(plane.intersect(ray), _utils.pos(.5,.5,0))

        ray = rays.Ray(_utils.pos(.5,.5,7), k=_utils.vec(0,0,1))
        self.assertEqual(plane.intersect(ray), None)

    def test_normal(self):
        vec = _utils.vec(1,4,7)
        n, w, h = _utils.basis(vec)
        plane = geometry.Plane(normal=vec, width=w, height=h)
        self.assertApproxArray(n, plane.normal(None))

class TestGeometryScreen(TestCase):

    def test_properties(self):
        screen = geometry.Screen()
        ray = rays.Ray(origin=_utils.pos(.5,.5,1), k=_utils.vec(0,0,-1))
        screen.refract(ray, _utils.pos(.5,.5,0), 1)

        self.assertEqual(type([]), type(screen.hits))
        self.assertEqual(1, len(screen.hits))
        self.assertEqual(ray, screen.hits[0])

    def test_refract(self):
        screen = geometry.Screen()
        ray = rays.Ray(origin=_utils.pos(.5,.5,1), k=_utils.vec(0,0,-1))
        screen.refract(ray, _utils.pos(.5,.5,0), 1)

        self.assertTrue(ray.terminated)
        self.assertSameArray(ray.pos, _utils.pos(.5,.5,0))

class TestScene(TestCase):

    @unittest.skip("Missing tests")
    def test_missing():
        pass

class TestSceneSource(TestCase):

    @unittest.skip("Missing tests")
    def test_missing():
        pass

class TestSceneSpiralSource(TestCase):

    @unittest.skip("Missing tests")
    def test_missing():
        pass

class TestSceneRadialSource(TestCase):

    @unittest.skip("Missing tests")
    def test_missing():
        pass

class TestSceneDenseSource(TestCase):

    @unittest.skip("Missing tests")
    def test_missing():
        pass

class TestGeometryIntegration(TestCase):

    def test_refract_sphere_lens(self):
        lens = geometry.SphereLens(1, 1, 1, n=1.0, pos=_utils.pos(0,0,1))

        ray = rays.Ray(origin=np.array([0, 0, 2]))
        ray.k = np.array([0, 0, -1])

        inter = lens.intersect(ray)
        lens.refract(ray, inter, 1.0)
        self.assertApproxArray(ray.k, np.array([0, 0, -1]))
        self.assertSameArray(inter, ray.pos)
        self.assertEqual(None, lens.intersect(ray))

        ray = rays.Ray(origin=np.array([0, 0, 1+1e-5]))
        ray.k = np.array([0, -1, -1])

        inter = lens.intersect(ray)
        lens.refract(ray, inter, 1.0)
        self.assertApproxArray(ray.k, np.array([0, -1, -1]), eps=1e-4)
        self.assertSameArray(inter, ray.pos)
        self.assertEqual(None, lens.intersect(ray))

if __name__ == "__main__":
    unittest.main()
