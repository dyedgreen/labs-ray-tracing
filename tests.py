"""
Provides unit tests
"""

import unittest
import numpy as np
from trace import rays
from trace import geometry
from trace import scene
from trace import _utils

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

    @unittest.skip("Missing tests")
    def test_missing():
        pass

class TestGeometryMirror(TestCase):

    @unittest.skip("Missing tests")
    def test_missing():
        pass

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
        lens = geometry.Sphere(1, 0.5, 0.5, axis=np.array([1, 0, 0]))
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
        lens = geometry.Sphere(1, 1, 1)
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

        plane = geometry.Plane(pos=np.array([0, 0, 1]))

        ray = rays.Ray()
        ray.k = np.array([0, 0, 1])
        self.assertSameArray(np.array([0, 0, 1]), plane.intersect(ray))

        ray = rays.Ray()
        ray.k = np.array([1, 1, 0])
        self.assertSameArray(None, plane.intersect(ray))

        ray = rays.Ray()
        ray.k = np.array([0, 0, -1])
        self.assertSameArray(None, plane.intersect(ray))

class TestGeometrySphereLens(TestCase):

    def test_refract(self):
        lens = geometry.SphereLens(1, 1, 1, n=1.0)

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

class TestGeometryScreen(TestCase):

    @unittest.skip("Missing tests")
    def test_missing():
        pass

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

if __name__ == "__main__":
    unittest.main()
