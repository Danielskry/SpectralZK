"""
SpectralZK protocol implementation.

This implements the zero-knowledge protocol based on aperiodic tilings.
The protocol allows a prover to demonstrate knowledge of a path through
a tiling without revealing the entire path.
"""

import secrets
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple

from .tiling import Tiling, Point
from .commitment import Commitment


@dataclass
class Instance:
    """Public instance of the tiling problem."""
    tiles: Dict[Point, str]
    size: int
    seed: int


@dataclass
class Witness:
    """Private witness (path through the tiling)."""
    path: List[Tuple[Point, str]]
    commitment: str
    nonce: str


@dataclass
class Challenge:
    """Verifier's challenge."""
    challenge_id: str
    positions: List[int]
    commitment: str


@dataclass
class Response:
    """Prover's response to challenge."""
    challenge_id: str
    revealed_steps: List[Tuple[int, Point, str]]
    path_length: int
    commitment: str
    nonce: str


class SpectralProtocol:
    """
    The SpectralZK protocol implementation.
    
    Protocol flow:
    1. Setup: Generate public tiling instance
    2. Witness: Prover finds path and commits
    3. Challenge: Verifier requests random positions
    4. Response: Prover reveals requested positions
    5. Verify: Check revealed positions are valid
    """
    
    def __init__(self, seed: int = None):
        """Initialize protocol with optional seed."""
        self.seed = seed if seed is not None else secrets.randbits(32)
        self.tiling = Tiling(self.seed)
    
    def create_instance(self, size: int) -> Instance:
        """
        Create a public tiling instance.
        
        Args:
            size: Size of the square tiling region
            
        Returns:
            Public instance
        """
        tiles = self.tiling.generate_region(size, size)
        return Instance(tiles=tiles, size=size, seed=self.seed)
    
    def generate_witness(self, instance: Instance, 
                        path_length: int,
                        start: Point = None) -> Witness:
        """
        Generate a witness (secret path through tiling).
        
        Args:
            instance: Public tiling instance
            path_length: Length of path to generate
            start: Starting position (random if None)
            
        Returns:
            Witness containing path and commitment
        """
        # Choose starting position
        if start is None:
            positions = list(instance.tiles.keys())
            start = random.choice(positions)
        
        # Generate path
        path = self._find_path(instance.tiles, start, path_length)
        
        # Create commitment to path
        path_data = [(str(pos), tile) for pos, tile in path]
        commitment, nonce = Commitment.create(path_data)
        
        return Witness(path=path, commitment=commitment, nonce=nonce)
    
    def create_challenge(self, instance: Instance, 
                        commitment: str,
                        num_challenges: int = 3) -> Challenge:
        """
        Create a verifier challenge.
        
        Args:
            instance: Public instance
            commitment: Prover's commitment
            num_challenges: Number of positions to challenge
            
        Returns:
            Challenge with random positions
        """
        challenge_id = secrets.token_hex(8)
        
        # In a real implementation, these would be derived from
        # a hash of the commitment for non-interactivity
        max_positions = instance.size * instance.size
        positions = []
        
        for _ in range(min(num_challenges, max_positions)):
            pos = secrets.randbelow(max_positions)
            if pos not in positions:
                positions.append(pos)
        
        return Challenge(
            challenge_id=challenge_id,
            positions=sorted(positions),
            commitment=commitment
        )
    
    def respond_to_challenge(self, witness: Witness, 
                           challenge: Challenge) -> Response:
        """
        Generate response to a challenge.
        
        Args:
            witness: Prover's witness
            challenge: Verifier's challenge
            
        Returns:
            Response revealing requested positions
        """
        revealed_steps = []
        
        for pos_idx in challenge.positions:
            if pos_idx < len(witness.path):
                pos, tile = witness.path[pos_idx]
                revealed_steps.append((pos_idx, pos, tile))
            else:
                revealed_steps.append((pos_idx, None, None))
        
        return Response(
            challenge_id=challenge.challenge_id,
            revealed_steps=revealed_steps,
            path_length=len(witness.path),
            commitment=witness.commitment,
            nonce=witness.nonce
        )
    
    def verify_response(self, instance: Instance,
                       challenge: Challenge,
                       response: Response) -> bool:
        """
        Verify a response to a challenge.
        For every challenge position < path_length, a valid step must be revealed and must match the instance.
        No extra or missing revealed steps for in-bounds challenge positions are allowed.
        All revealed steps for in-bounds challenge positions must match the instance exactly.
        """
        if response.challenge_id != challenge.challenge_id:
            return False
        if response.commitment != challenge.commitment:
            return False
        # Build a map for quick lookup
        revealed_map = {pos_idx: (pos, claimed_tile) for pos_idx, pos, claimed_tile in response.revealed_steps}
        # All in-bounds challenge positions must be present and valid
        for pos_idx in challenge.positions:
            if pos_idx < response.path_length:
                if pos_idx not in revealed_map:
                    return False
                pos, claimed_tile = revealed_map[pos_idx]
                if pos is None or claimed_tile is None:
                    return False
                if pos not in instance.tiles:
                    return False
                if instance.tiles[pos] != claimed_tile:
                    return False
        # No extra revealed steps for in-bounds challenge positions
        for pos_idx, (pos, claimed_tile) in revealed_map.items():
            if pos_idx < response.path_length:
                if pos_idx not in challenge.positions:
                    return False
                # Also check that the revealed value matches the instance
                if pos is None or claimed_tile is None:
                    return False
                if pos not in instance.tiles:
                    return False
                if instance.tiles[pos] != claimed_tile:
                    return False
        if response.path_length < 0 or response.path_length > len(instance.tiles):
            return False
        return True
    
    def _find_path(self, tiles: Dict[Point, str], 
                   start: Point, length: int) -> List[Tuple[Point, str]]:
        """Find a path through the tiling."""
        path = []
        current = start
        visited = set()
        
        for _ in range(length):
            if current not in tiles or current in visited:
                break
                
            path.append((current, tiles[current]))
            visited.add(current)
            
            # Find unvisited neighbors
            neighbors = self.tiling.get_neighbors(current)
            valid_next = [n for n in neighbors 
                         if n in tiles and n not in visited]
            
            if not valid_next:
                break
            
            # Use deterministic selection based on position
            # This makes path generation reproducible
            valid_next.sort(key=lambda p: (p.x, p.y))
            current = valid_next[0]
            
        return path
