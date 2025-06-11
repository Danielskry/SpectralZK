"""
Aperiodic tiling generation for SpectralZK.

This module implements a simple deterministic aperiodic tiling system
based on position-dependent hashing. The tiles are generated using
local rules that prevent global periodicity.
"""

import hashlib
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class Point:
    """A 2D point in the tiling space."""
    x: float
    y: float
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def distance_to(self, other: 'Point') -> float:
        """Euclidean distance to another point."""
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5


class Tiling:
    """
    Generates a deterministic aperiodic tiling pattern.
    
    The tiling is created using position-dependent hashing which ensures:
    1. Deterministic generation (same position -> same tile)
    2. No global periodicity (hash functions break patterns)
    3. Local structure (neighboring tiles influence each other)
    """
    
    TILE_TYPES = ["A", "B", "C", "D", "E", "F"]
    
    def __init__(self, seed: int = 0):
        """Initialize with a seed that affects the tiling pattern."""
        self.seed = seed
    
    def _hash_position(self, x: float, y: float) -> str:
        """Create a hash from a position."""
        # Include seed to allow different tiling patterns
        data = f"{self.seed}:{x:.3f},{y:.3f}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get_tile_type(self, pos: Point, neighbors: List[str] = None) -> str:
        """
        Determine tile type at a given position.
        
        Args:
            pos: Position to get tile type for
            neighbors: Types of neighboring tiles (for local constraints)
            
        Returns:
            Tile type as a string (A, B, C, etc.)
        """
        # Base tile from position hash
        pos_hash = self._hash_position(pos.x, pos.y)
        base_value = int(pos_hash[:8], 16)
        
        # Apply local constraints if neighbors provided
        if neighbors:
            # Simple rule: if surrounded by same type, force different
            if len(neighbors) >= 3 and all(n == neighbors[0] for n in neighbors):
                base_value += 1
            
            # Another rule: A and B together suggest C or D
            if "A" in neighbors and "B" in neighbors:
                base_value = base_value % 2 + 2  # Maps to C or D
        
        return self.TILE_TYPES[base_value % len(self.TILE_TYPES)]
    
    def get_neighbors(self, center: Point, radius: float = 1.5) -> List[Point]:
        """Get positions of neighboring tiles."""
        neighbors = []
        
        # Check 8 surrounding positions
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                neighbor = Point(center.x + dx, center.y + dy)
                if center.distance_to(neighbor) <= radius:
                    neighbors.append(neighbor)
                    
        return neighbors
    
    def generate_region(self, width: int, height: int, 
                       origin: Point = None) -> Dict[Point, str]:
        """
        Generate a rectangular region of the tiling.
        
        Args:
            width: Width of region to generate
            height: Height of region to generate
            origin: Starting point (default: (0, 0))
            
        Returns:
            Dictionary mapping positions to tile types
        """
        if origin is None:
            origin = Point(0, 0)
            
        tiles = {}
        
        # Generate in reading order to allow neighbor influence
        for y in range(height):
            for x in range(width):
                pos = Point(origin.x + x, origin.y + y)
                
                # Get already-placed neighbors
                neighbors = self.get_neighbors(pos)
                neighbor_types = []
                
                for n in neighbors:
                    if n in tiles:
                        neighbor_types.append(tiles[n])
                
                # Determine tile type
                tile_type = self.get_tile_type(pos, neighbor_types)
                tiles[pos] = tile_type
                
        return tiles
    
    def check_periodicity(self, tiles: Dict[Point, str], 
                         max_period: int = 5) -> Dict[Tuple[int, int], float]:
        """
        Check for periodic patterns in a tiling.
        
        Returns dictionary of (period_x, period_y) -> match_percentage
        """
        results = {}
        
        for px in range(1, max_period + 1):
            for py in range(1, max_period + 1):
                matches = 0
                total = 0
                
                for pos, tile_type in tiles.items():
                    shifted = Point(pos.x + px, pos.y + py)
                    if shifted in tiles:
                        total += 1
                        if tiles[shifted] == tile_type:
                            matches += 1
                
                if total > 0:
                    results[(px, py)] = matches / total
                    
        return results
    
    def find_path(self, tiles: Dict[Point, str], 
                  start: Point, length: int) -> List[Tuple[Point, str]]:
        """
        Find a path through the tiling (for witness generation).
        
        This is a simple random walk - in a real implementation,
        this might involve more sophisticated pathfinding.
        """
        import random
        
        path = []
        current = start
        
        if current not in tiles:
            return path
            
        for _ in range(length):
            path.append((current, tiles[current]))
            
            # Find valid next positions
            neighbors = self.get_neighbors(current)
            valid_next = [n for n in neighbors if n in tiles]
            
            if not valid_next:
                break
                
            # Choose next position
            # In real implementation, this might use the seed
            current = random.choice(valid_next)
            
        return path
