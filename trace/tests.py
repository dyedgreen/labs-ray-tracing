"""
Provides unit tests
"""

import unittest
import numpy as np
import rays
import geometry

class TestCase(unittest.TestCase):

    def assertSameArray(self, a, b):
        self.assertTrue(np.array_equal(a, b))

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
        # TODO
        pass

if __name__ == "__main__":
    unittest.main()
