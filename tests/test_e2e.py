"""
End-to-end tests for the complete SpectralZK protocol.
"""

import unittest
import time
from spectralzk import SpectralProtocol, Point


class TestEndToEnd(unittest.TestCase):
    """Test complete protocol executions."""
    
    def test_basic_protocol_flow(self):
        """Test basic protocol execution."""
        # Setup
        protocol = SpectralProtocol(seed=42)
        instance = protocol.create_instance(size=6)
        
        # Prover generates witness
        witness = protocol.generate_witness(instance, path_length=10)
        self.assertGreater(len(witness.path), 0)
        
        # Verifier challenges
        challenge = protocol.create_challenge(instance, witness.commitment, 3)
        self.assertGreater(len(challenge.positions), 0)
        
        # Prover responds
        response = protocol.respond_to_challenge(witness, challenge)
        self.assertEqual(len(response.revealed_steps), len(challenge.positions))
        
        # Verifier verifies
        is_valid = protocol.verify_response(instance, challenge, response)
        self.assertTrue(is_valid)
    
    def test_multiple_challenges(self):
        """Test multiple challenges on same witness."""
        protocol = SpectralProtocol(seed=123)
        instance = protocol.create_instance(size=5)
        witness = protocol.generate_witness(instance, path_length=8)
        
        # Multiple challenges should all verify
        for i in range(3):
            challenge = protocol.create_challenge(instance, witness.commitment, 2)
            response = protocol.respond_to_challenge(witness, challenge)
            is_valid = protocol.verify_response(instance, challenge, response)
            self.assertTrue(is_valid, f"Challenge {i} failed")
    
    def test_different_sized_instances(self):
        """Test protocol with different instance sizes."""
        for size in [3, 5, 8, 10]:
            with self.subTest(size=size):
                protocol = SpectralProtocol(seed=size)
                instance = protocol.create_instance(size=size)
                
                path_length = min(size * 2, 15)
                witness = protocol.generate_witness(instance, path_length)
                
                num_challenges = min(3, len(witness.path))
                challenge = protocol.create_challenge(instance, witness.commitment, num_challenges)
                response = protocol.respond_to_challenge(witness, challenge)
                
                is_valid = protocol.verify_response(instance, challenge, response)
                self.assertTrue(is_valid)
    
    def test_consistency_across_seeds(self):
        """Test that protocol works consistently with different seeds."""
        successes = 0
        trials = 10
        
        for seed in range(trials):
            protocol = SpectralProtocol(seed=seed)
            instance = protocol.create_instance(size=4)
            witness = protocol.generate_witness(instance, path_length=6)
            challenge = protocol.create_challenge(instance, witness.commitment, 2)
            response = protocol.respond_to_challenge(witness, challenge)
            
            if protocol.verify_response(instance, challenge, response):
                successes += 1
        
        success_rate = successes / trials
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"Success rate too low: {success_rate:.0%}")
    
    def test_performance(self):
        """Test protocol performance."""
        protocol = SpectralProtocol(seed=999)
        
        # Time instance creation
        start = time.time()
        instance = protocol.create_instance(size=10)
        instance_time = time.time() - start
        self.assertLess(instance_time, 1.0, "Instance creation too slow")
        
        # Time witness generation
        start = time.time()
        witness = protocol.generate_witness(instance, path_length=20)
        witness_time = time.time() - start
        self.assertLess(witness_time, 1.0, "Witness generation too slow")
        
        # Time verification
        challenge = protocol.create_challenge(instance, witness.commitment, 5)
        response = protocol.respond_to_challenge(witness, challenge)
        
        start = time.time()
        protocol.verify_response(instance, challenge, response)
        verify_time = time.time() - start
        self.assertLess(verify_time, 0.1, "Verification too slow")
    
    def test_zero_knowledge_property(self):
        """Test that protocol reveals minimal information."""
        protocol = SpectralProtocol(seed=42)
        instance = protocol.create_instance(size=8)
        witness = protocol.generate_witness(instance, path_length=15)
        
        # Small challenge should reveal little
        challenge = protocol.create_challenge(instance, witness.commitment, 3)
        response = protocol.respond_to_challenge(witness, challenge)
        
        revealed_ratio = len(response.revealed_steps) / response.path_length
        self.assertLessEqual(revealed_ratio, 0.3, 
                            f"Too much revealed: {revealed_ratio:.0%}")
        
        # Response should not contain full path
        self.assertNotIn('path', response.__dict__)
    
    def test_soundness_property(self):
        """Test that invalid witnesses are rejected."""
        protocol = SpectralProtocol(seed=42)
        instance = protocol.create_instance(size=5)
        
        # Create a "fake" witness with wrong tile types
        from spectralzk.protocol import Witness
        from spectralzk import Commitment
        fake_path = [(Point(0, 0), "X"), (Point(1, 0), "Y")]
        fake_commitment, fake_nonce = Commitment.create(fake_path)
        fake_witness = Witness(
            path=fake_path,
            commitment=fake_commitment,
            nonce=fake_nonce
        )
        # Challenge only positions that exist in the fake path
        challenge = protocol.create_challenge(instance, fake_witness.commitment, 2)
        # Force challenge positions to [0, 1] to match fake_path indices
        challenge.positions = [0, 1]
        response = protocol.respond_to_challenge(fake_witness, challenge)
        
        # Should not verify
        is_valid = protocol.verify_response(instance, challenge, response)
        self.assertFalse(is_valid, "Invalid witness should not verify")


if __name__ == '__main__':
    unittest.main()
