import hashlib
import sys
from spectralzk import Point, Tiling, Commitment, SpectralProtocol


def test_section(name):
    """Print a test section header."""
    print(f"\n{'='*50}")
    print(f" Testing: {name}")
    print(f"{'='*50}")


def verify_basic_components():
    """Test basic mathematical and cryptographic components."""
    test_section("Basic Components")
    
    # Test Point class
    print("\n1. Testing Point class...")
    p1 = Point(0, 0)
    p2 = Point(3, 4)
    distance = p1.distance_to(p2)
    assert distance == 5.0, f"Distance calculation failed: {distance}"
    print("   ✓ Point distance calculation works")
    
    # Test hashing
    print("\n2. Testing hash determinism...")
    data = "test_data"
    hash1 = hashlib.sha256(data.encode()).hexdigest()
    hash2 = hashlib.sha256(data.encode()).hexdigest()
    assert hash1 == hash2, "Hash should be deterministic"
    print("   ✓ Hash functions are deterministic")
    
    # Test commitment scheme
    print("\n3. Testing commitment scheme...")
    value = "secret_value"
    commitment, nonce = Commitment.create(value)
    
    assert len(commitment) == 64, f"Wrong commitment length: {len(commitment)}"
    assert Commitment.verify(commitment, value, nonce), "Valid commitment should verify"
    assert not Commitment.verify(commitment, "wrong_value", nonce), "Invalid value should not verify"
    print("   ✓ Commitment scheme works correctly")
    
    print("\n✓ All basic components verified")


def verify_tiling_properties():
    """Test the aperiodic tiling generation."""
    test_section("Tiling Properties")
    
    tiling = Tiling(seed=123)
    
    # Test determinism
    print("\n1. Testing tiling determinism...")
    pos = Point(5.0, 7.0)
    type1 = tiling.get_tile_type(pos, [])
    type2 = tiling.get_tile_type(pos, [])
    assert type1 == type2, "Tile generation should be deterministic"
    print("   ✓ Tiling is deterministic")
    
    # Test region generation
    print("\n2. Testing region generation...")
    region = tiling.generate_region(10, 10)
    assert len(region) == 100, f"Wrong number of tiles: {len(region)}"
    
    # Count tile types
    type_counts = {}
    for tile_type in region.values():
        type_counts[tile_type] = type_counts.get(tile_type, 0) + 1
    
    print("   Tile distribution:")
    for tile_type, count in sorted(type_counts.items()):
        print(f"     {tile_type}: {count} tiles ({count/len(region)*100:.1f}%)")
    
    # All types should appear
    assert len(type_counts) >= 4, "Should have diverse tile types"
    print("   ✓ Good tile type distribution")
    
    # Test aperiodicity
    print("\n3. Testing aperiodicity...")
    periods = tiling.check_periodicity(region, max_period=5)
    
    print("   Periodicity check:")
    max_repetition = 0
    for (px, py), rate in sorted(periods.items()):
        print(f"     Period ({px},{py}): {rate:.1%} repetition")
        max_repetition = max(max_repetition, rate)
    
    # Should not have high repetition rates
    assert max_repetition < 0.5, f"Too much repetition: {max_repetition:.1%}"
    print("   ✓ No strong periodic patterns detected")
    
    print("\n✓ Tiling properties verified")


def verify_protocol():
    """Test the complete protocol execution."""
    test_section("Protocol Execution")
    
    # Initialize
    print("\n1. Testing protocol initialization...")
    protocol = SpectralProtocol(seed=42)
    instance = protocol.create_instance(size=5)
    
    assert instance.size == 5, f"Wrong size: {instance.size}"
    assert len(instance.tiles) == 25, f"Wrong tile count: {len(instance.tiles)}"
    print("   ✓ Protocol initialization works")
    
    # Generate witness
    print("\n2. Testing witness generation...")
    witness = protocol.generate_witness(instance, path_length=8)
    
    assert len(witness.path) == 8, f"Wrong path length: {len(witness.path)}"
    assert len(witness.commitment) == 64, f"Wrong commitment length: {len(witness.commitment)}"
    
    # Verify path is valid
    for i, (pos, tile) in enumerate(witness.path):
        assert pos in instance.tiles, f"Step {i}: position not in tiling"
        assert instance.tiles[pos] == tile, f"Step {i}: wrong tile type"
    print("   ✓ Witness generation works")
    
    # Create challenge
    print("\n3. Testing challenge generation...")
    challenge = protocol.create_challenge(instance, witness.commitment, num_challenges=3)
    
    assert len(challenge.positions) <= 3, f"Too many challenges: {len(challenge.positions)}"
    assert all(0 <= p < 25 for p in challenge.positions), "Invalid challenge positions"
    print("   ✓ Challenge generation works")
    
    # Generate response
    print("\n4. Testing response generation...")
    response = protocol.respond_to_challenge(witness, challenge)
    
    assert response.challenge_id == challenge.challenge_id, "Challenge ID mismatch"
    assert len(response.revealed_steps) == len(challenge.positions), "Wrong number of revealed steps"
    print("   ✓ Response generation works")
    
    # Verify
    print("\n5. Testing verification...")
    is_valid = protocol.verify_response(instance, challenge, response)
    
    assert is_valid, "Valid protocol execution should verify"
    print("   ✓ Verification works")
    
    # Test invalid response
    print("\n6. Testing rejection of invalid responses...")
    
    # Modify a revealed tile type
    if response.revealed_steps:
        bad_steps = response.revealed_steps.copy()
        pos_idx, pos, tile = bad_steps[0]
        bad_steps[0] = (pos_idx, pos, "X")  # Invalid tile type
        
        bad_response = Response(
            challenge_id=response.challenge_id,
            revealed_steps=bad_steps,
            path_length=response.path_length,
            commitment=response.commitment,
            nonce=response.nonce
        )
        
        is_invalid = protocol.verify_response(instance, challenge, bad_response)
        assert not is_invalid, "Modified response should not verify"
        print("   ✓ Invalid responses are rejected")
    
    print("\n✓ Protocol execution verified")


def verify_consistency():
    """Test consistency across multiple runs."""
    test_section("Consistency Check")
    
    print("\nRunning 20 protocol executions...")
    
    successes = 0
    for i in range(20):
        protocol = SpectralProtocol(seed=i)
        instance = protocol.create_instance(size=4)
        witness = protocol.generate_witness(instance, path_length=6)
        challenge = protocol.create_challenge(instance, witness.commitment, 2)
        response = protocol.respond_to_challenge(witness, challenge)
        
        if protocol.verify_response(instance, challenge, response):
            successes += 1
    
    success_rate = successes / 20
    print(f"\nSuccess rate: {success_rate:.0%} ({successes}/20)")
    
    assert success_rate >= 0.95, f"Success rate too low: {success_rate:.0%}"
    print("✓ High consistency verified")


def main():
    """Run all verification tests."""
    print("🔍 SpectralZK Implementation Verification")
    print("="*50)
    
    try:
        verify_basic_components()
        verify_tiling_properties()
        verify_protocol()
        verify_consistency()
        
        print("\n" + "="*50)
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("="*50)
        print("\n✅ The implementation works correctly")
        print("✅ Core components function as expected")
        print("✅ Protocol executes successfully")
        print("✅ Results are consistent and reproducible")
        
        print("\n⚠️  IMPORTANT:")
        print("This verifies the implementation works as designed.")
        print("It does NOT prove cryptographic security.")
        print("This is a research prototype for exploration only.")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        print("="*50)
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("="*50)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
