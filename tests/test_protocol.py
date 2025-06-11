"""
Tests for the protocol module.
"""

import unittest
from spectralzk import SpectralProtocol, Point, Commitment


class TestProtocol(unittest.TestCase):
    """Test the SpectralProtocol class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.protocol = SpectralProtocol(seed=42)
    
    def test_instance_creation(self):
        """Test instance creation."""
        instance = self.protocol.create_instance(size=5)
        
        self.assertEqual(instance.size, 5)
        self.assertEqual(len(instance.tiles), 25)
        self.assertEqual(instance.seed, 42)
    
    def test_witness_generation(self):
        """Test witness generation."""
        instance = self.protocol.create_instance(size=5)
        witness = self.protocol.generate_witness(instance, path_length=8)
        
        # Check structure
        self.assertLessEqual(len(witness.path), 8)
        self.assertEqual(len(witness.commitment), 64)
        self.assertEqual(len(witness.nonce), 32)
        
        # Check path validity
        for pos, tile in witness.path:
            self.assertIn(pos, instance.tiles)
            self.assertEqual(instance.tiles[pos], tile)
    
    def test_deterministic_witness(self):
        """Test that witness generation is deterministic with fixed start."""
        instance = self.protocol.create_instance(size=5)
        start = Point(2, 2)
        
        witness1 = self.protocol.generate_witness(instance, 6, start)
        witness2 = self.protocol.generate_witness(instance, 6, start)
        
        # Paths should be identical
        self.assertEqual(len(witness1.path), len(witness2.path))
        for (p1, t1), (p2, t2) in zip(witness1.path, witness2.path):
            self.assertEqual(p1, p2)
            self.assertEqual(t1, t2)
    
    def test_challenge_creation(self):
        """Test challenge creation."""
        instance = self.protocol.create_instance(size=4)
        commitment = "dummy_commitment"
        
        challenge = self.protocol.create_challenge(instance, commitment, 3)
        
        # Check structure
        self.assertEqual(len(challenge.challenge_id), 16)
        self.assertLessEqual(len(challenge.positions), 3)
        self.assertEqual(challenge.commitment, commitment)
        
        # Positions should be valid
        for pos in challenge.positions:
            self.assertGreaterEqual(pos, 0)
            self.assertLess(pos, 16)
    
    def test_response_generation(self):
        """Test response generation."""
        instance = self.protocol.create_instance(size=4)
        witness = self.protocol.generate_witness(instance, 8)
        challenge = self.protocol.create_challenge(instance, witness.commitment, 3)
        response = self.protocol.respond_to_challenge(witness, challenge)
        
        # Check structure
        self.assertEqual(response.challenge_id, challenge.challenge_id)
        self.assertEqual(len(response.revealed_steps), len(challenge.positions))
        self.assertEqual(response.path_length, len(witness.path))
        
        # Check revealed steps (only for in-bounds indices)
        for pos_idx, pos, tile in response.revealed_steps:
            self.assertIn(pos_idx, challenge.positions)
            if pos is not None and tile is not None and pos_idx < len(witness.path):
                self.assertEqual(witness.path[pos_idx], (pos, tile))
    
    def test_valid_verification(self):
        """Test verification of valid response."""
        instance = self.protocol.create_instance(size=5)
        witness = self.protocol.generate_witness(instance, 10)
        challenge = self.protocol.create_challenge(instance, witness.commitment, 4)
        response = self.protocol.respond_to_challenge(witness, challenge)
        
        is_valid = self.protocol.verify_response(instance, challenge, response)
        self.assertTrue(is_valid)
    
    def test_invalid_verification(self):
        """Test rejection of invalid responses."""
        instance = self.protocol.create_instance(size=5)
        witness = self.protocol.generate_witness(instance, 10)
        challenge = self.protocol.create_challenge(instance, witness.commitment, 3)
        response = self.protocol.respond_to_challenge(witness, challenge)
        
        # Test wrong challenge ID
        response.challenge_id = "wrong_id"
        self.assertFalse(self.protocol.verify_response(instance, challenge, response))
        response.challenge_id = challenge.challenge_id
        
        # Test wrong commitment
        original_commitment = response.commitment
        response.commitment = "wrong_commitment"
        self.assertFalse(self.protocol.verify_response(instance, challenge, response))
        response.commitment = original_commitment
        
        # Test wrong tile type
        if response.revealed_steps:
            original_steps = response.revealed_steps
            pos_idx, pos, tile = response.revealed_steps[0]
            response.revealed_steps = [(pos_idx, pos, "X")] + original_steps[1:]
            self.assertFalse(self.protocol.verify_response(instance, challenge, response))
            response.revealed_steps = original_steps
    
    def test_empty_path(self):
        """Test handling of empty paths."""
        instance = self.protocol.create_instance(size=3)
        
        # Force an empty path by using non-existent start
        witness = self.protocol.generate_witness(instance, 10, Point(-1, -1))
        
        # Should handle gracefully
        self.assertEqual(len(witness.path), 0)
        challenge = self.protocol.create_challenge(instance, witness.commitment, 2)
        response = self.protocol.respond_to_challenge(witness, challenge)
        
        # Should still verify (no revealed steps)
        is_valid = self.protocol.verify_response(instance, challenge, response)
        self.assertTrue(is_valid)


class TestCommitment(unittest.TestCase):
    """Test the commitment scheme."""
    
    def test_commitment_creation(self):
        """Test basic commitment creation."""
        value = "test_value"
        commitment, nonce = Commitment.create(value)
        
        self.assertEqual(len(commitment), 64)  # SHA-256
        self.assertEqual(len(nonce), 32)  # 16 bytes hex
    
    def test_commitment_verification(self):
        """Test commitment verification."""
        value = "test_value"
        commitment, nonce = Commitment.create(value)
        
        # Valid opening
        self.assertTrue(Commitment.verify(commitment, value, nonce))
        
        # Invalid openings
        self.assertFalse(Commitment.verify(commitment, "wrong_value", nonce))
        self.assertFalse(Commitment.verify(commitment, value, "wrong_nonce"))
        self.assertFalse(Commitment.verify("wrong_commitment", value, nonce))
    
    def test_commitment_hiding(self):
        """Test that commitments hide values."""
        value = "secret"
        
        # Multiple commitments to same value should differ
        c1, n1 = Commitment.create(value)
        c2, n2 = Commitment.create(value)
        
        self.assertNotEqual(c1, c2)
        self.assertNotEqual(n1, n2)
    
    def test_commitment_binding(self):
        """Test that commitments are binding."""
        value1 = "value1"
        value2 = "value2"
        
        commitment, nonce = Commitment.create(value1)
        
        # Can't open to different value
        self.assertFalse(Commitment.verify(commitment, value2, nonce))
    
    def test_vector_commitment(self):
        """Test committing to multiple values."""
        values = ["a", "b", "c", "d"]
        commitment, nonce = Commitment.create_vector(values)
        
        self.assertEqual(len(commitment), 64)
        self.assertTrue(Commitment.verify(commitment, values, nonce))


if __name__ == '__main__':
    unittest.main()
