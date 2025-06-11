"""
Tests for the tiling module.
"""

import unittest
from spectralzk import Point, Tiling


class TestPoint(unittest.TestCase):
    """Test the Point class."""
    
    def test_creation(self):
        """Test point creation."""
        p = Point(3.0, 4.0)
        self.assertEqual(p.x, 3.0)
        self.assertEqual(p.y, 4.0)
    
    def test_distance(self):
        """Test distance calculation."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        self.assertEqual(p1.distance_to(p2), 5.0)
    
    def test_equality(self):
        """Test point equality."""
        p1 = Point(1.0, 2.0)
        p2 = Point(1.0, 2.0)
        p3 = Point(1.0, 2.1)
        
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)
    
    def test_hash(self):
        """Test point hashing."""
        p1 = Point(1.0, 2.0)
        p2 = Point(1.0, 2.0)
        
        # Equal points should have same hash
        self.assertEqual(hash(p1), hash(p2))
        
        # Should be usable in sets/dicts
        point_set = {p1}
        self.assertIn(p2, point_set)


class TestTiling(unittest.TestCase):
    """Test the Tiling class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tiling = Tiling(seed=42)
    
    def test_determinism(self):
        """Test that tile generation is deterministic."""
        pos = Point(5.0, 7.0)
        
        type1 = self.tiling.get_tile_type(pos)
        type2 = self.tiling.get_tile_type(pos)
        
        self.assertEqual(type1, type2)
    
    def test_valid_tile_types(self):
        """Test that only valid tile types are generated."""
        pos = Point(10.0, 20.0)
        tile_type = self.tiling.get_tile_type(pos)
        
        self.assertIn(tile_type, Tiling.TILE_TYPES)
    
    def test_neighbor_influence(self):
        """Test that neighbors can influence tile type."""
        pos = Point(5.0, 5.0)
        
        # No neighbors
        type_alone = self.tiling.get_tile_type(pos, [])
        
        # Surrounded by same type
        type_surrounded = self.tiling.get_tile_type(pos, ["A", "A", "A", "A"])
        
        # Local constraint should force different type
        self.assertNotEqual(type_alone, type_surrounded)
    
    def test_get_neighbors(self):
        """Test neighbor generation."""
        center = Point(5, 5)
        neighbors = self.tiling.get_neighbors(center)
        
        # Should have 8 neighbors
        self.assertEqual(len(neighbors), 8)
        
        # All should be within radius
        for n in neighbors:
            self.assertLessEqual(center.distance_to(n), 1.5)
    
    def test_region_generation(self):
        """Test region generation."""
        region = self.tiling.generate_region(5, 5)
        
        # Should have correct number of tiles
        self.assertEqual(len(region), 25)
        
        # All positions should be covered
        for x in range(5):
            for y in range(5):
                self.assertIn(Point(x, y), region)
        
        # All should have valid types
        for tile_type in region.values():
            self.assertIn(tile_type, Tiling.TILE_TYPES)
    
    def test_different_seeds(self):
        """Test that different seeds produce different tilings."""
        tiling1 = Tiling(seed=1)
        tiling2 = Tiling(seed=2)
        
        region1 = tiling1.generate_region(5, 5)
        region2 = tiling2.generate_region(5, 5)
        
        # Should be different
        differences = 0
        for pos in region1:
            if region1[pos] != region2[pos]:
                differences += 1
        
        # At least some tiles should differ
        self.assertGreater(differences, 0)
    
    def test_periodicity_check(self):
        """Test periodicity checking."""
        region = self.tiling.generate_region(10, 10)
        periods = self.tiling.check_periodicity(region, max_period=3)
        
        # Should check all requested periods
        self.assertEqual(len(periods), 9)  # 3x3 periods
        
        # All rates should be between 0 and 1
        for rate in periods.values():
            self.assertGreaterEqual(rate, 0)
            self.assertLessEqual(rate, 1)
    
    def test_find_path(self):
        """Test path finding."""
        region = self.tiling.generate_region(5, 5)
        start = Point(2, 2)
        
        path = self.tiling.find_path(region, start, length=5)
        
        # Should return a path
        self.assertIsInstance(path, list)
        self.assertLessEqual(len(path), 5)
        
        # Each step should be valid
        for pos, tile_type in path:
            self.assertIn(pos, region)
            self.assertEqual(region[pos], tile_type)


if __name__ == '__main__':
    unittest.main()
