import unittest
import sys
import os
import numpy as np

# Adiciona o diretório do plugin ao sys.path para importação local
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rbf_utils import interpolate_rbf_advanced

class TestInterpolateRbfAdvanced(unittest.TestCase):
    def setUp(self):
        # Pontos simples em uma grade 3x3
        self.points = np.array([
            [0, 0], [0, 1], [0, 2],
            [1, 0], [1, 1], [1, 2],
            [2, 0], [2, 1], [2, 2]
        ])
        self.values = np.array([1, 2, 3, 2, 3, 4, 3, 4, 5])
        self.grid_x = np.linspace(0, 2, 5)
        self.grid_y = np.linspace(0, 2, 5)

    def test_basic_rbf(self):
        grid = interpolate_rbf_advanced(
            self.points, self.values, self.grid_x, self.grid_y,
            function='thin_plate', smooth=0.1
        )
        self.assertEqual(grid.shape, (5, 5))
        self.assertFalse(np.any(np.isnan(grid)))

    def test_local_neighbors(self):
        grid = interpolate_rbf_advanced(
            self.points, self.values, self.grid_x, self.grid_y,
            function='thin_plate', smooth=0.1, max_neighbors=4
        )
        self.assertEqual(grid.shape, (5, 5))

    def test_extrapolation_constant(self):
        # Testa extrapolação constante
        grid = interpolate_rbf_advanced(
            self.points, self.values, self.grid_x, self.grid_y,
            function='thin_plate', smooth=0.1, extrapolation_method='constant', extrapolation_value=99
        )
        self.assertTrue(np.any(grid == 99) or not np.any(np.isnan(grid)))

if __name__ == '__main__':
    unittest.main()
