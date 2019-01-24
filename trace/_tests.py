"""
Provides unit tests
"""

import unittest
import numpy as np
import rays
import geometry
import _utils

class TestCase(unittest.TestCase):

    def assertSameArray(self, a, b):
        if not np.array_equal(a, b):
            raise AssertionError("{} is not {}".format(a, b))

    def assertApproxArray(self, a, b, eps=1e-10):
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

        with self.assertRaises(TypeError):
            ray.k = [1,2,3]

        with self.assertRaises(TypeError):
            ray.pos = 6.4

        # TODO: Test wavelength property

    def test_defaults(self):
        ray = rays.Ray()
        self.assertSameArray(ray.pos, np.zeros(3))
        self.assertSameArray(ray.k, np.zeros(3))

class TestGeometry(TestCase):

    def test_properties(self):
        generic = geometry.Geometry()

        generic.n = 4.3
        self.assertEqual(generic.n, 4.3)

        generic.pos = np.array([3,6,8])
        self.assertSameArray(generic.pos, np.array([3,6,8]))

        with self.assertRaises(ValueError):
            generic.n = 0.4

        with self.assertRaises(TypeError):
            generic.n = False

        with self.assertRaises(TypeError):
            generic.pos = [1,2,3]

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
            generic.refract(None, None, None)

class TestGeometrySphere(TestCase):

    def test_properties(self):
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
        self.assertApproxArray(lens.intersect(ray), np.array([0,1,0]))
        ray.k = np.array([-np.sqrt(1/2), np.sqrt(1/2), -2])
        self.assertApproxArray(lens.intersect(ray), np.array([-np.sqrt(1/2), np.sqrt(1/2),0]))

        ray.pos = np.array([0, 0, 0.1])
        ray.k = np.array([0, 0, 1])
        self.assertEqual(None, lens.intersect(ray))

        with self.assertRaises(AttributeError):
            lens.intersect(None)

    @unittest.skip("Not yet implemented")
    def test_refract(self):
        raise NotImplementedError

if __name__ == "__main__":
    unittest.main()
