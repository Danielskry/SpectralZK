#!/usr/bin/env python3
"""
Interactive demonstration of the SpectralZK protocol.

This shows how the protocol works step by step with a simple example.
"""

import sys
import time
from spectralzk import SpectralProtocol, Point


def print_header(text):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")


def print_tiling_sample(tiles, size=5):
    """Display a small section of the tiling."""
    print("\nTiling sample (top-left corner):")
    for y in range(min(size, 5)):
        row = ""
        for x in range(min(size, 5)):
            pos = Point(x, y)
            if pos in tiles:
                row += tiles[pos] + " "
            else:
                row += ". "
        print(f"  {row}")
    
    if size > 5:
        print("  ...")


def run_demo():
    """Run the interactive demonstration."""
    print_header("SpectralZK Protocol Demonstration")
    
    print("\nThis demo shows a zero-knowledge proof based on aperiodic tilings.")
    print("The prover will demonstrate knowledge of a path through a tiling")
    print("without revealing the entire path.\n")
    
    # Initialize protocol
    print("1. SETUP PHASE")
    print("-" * 40)
    
    seed = 42  # Fixed seed for reproducibility
    protocol = SpectralProtocol(seed=seed)
    print(f"Protocol initialized with seed: {seed}")
    
    # Create public instance
    size = 8
    print(f"\nGenerating {size}x{size} aperiodic tiling...")
    start_time = time.time()
    instance = protocol.create_instance(size)
    setup_time = time.time() - start_time
    
    print(f"Created tiling with {len(instance.tiles)} tiles in {setup_time:.3f}s")
    print_tiling_sample(instance.tiles, size)
    
    # Check for periodicity
    print("\nChecking tiling properties...")
    from spectralzk.tiling import Tiling
    tiling = Tiling(seed)
    periods = tiling.check_periodicity(instance.tiles, max_period=3)
    
    print("Period analysis (lower is better):")
    for (px, py), match_rate in sorted(periods.items()):
        print(f"  Period ({px},{py}): {match_rate:.1%} repetition")
    
    # Generate witness
    print("\n2. WITNESS GENERATION (Prover)")
    print("-" * 40)
    
    path_length = 12
    start_pos = Point(1, 1)
    print(f"Prover generating secret path of length {path_length}...")
    print(f"Starting position: ({start_pos.x}, {start_pos.y})")
    
    start_time = time.time()
    witness = protocol.generate_witness(instance, path_length, start_pos)
    witness_time = time.time() - start_time
    
    print(f"Generated path in {witness_time:.3f}s")
    print(f"Path commitment: {witness.commitment[:16]}...")
    
    # Show first few steps (in real protocol, this would be secret)
    print("\nFirst 3 steps of secret path:")
    for i, (pos, tile) in enumerate(witness.path[:3]):
        print(f"  Step {i}: ({pos.x}, {pos.y}) -> {tile}")
    print("  ... (remaining steps hidden)")
    
    # Create challenge
    print("\n3. CHALLENGE (Verifier)")
    print("-" * 40)
    
    num_challenges = 4
    print(f"Verifier creating challenge for {num_challenges} positions...")
    
    challenge = protocol.create_challenge(instance, witness.commitment, num_challenges)
    print(f"Challenge ID: {challenge.challenge_id}")
    print(f"Requested positions: {challenge.positions}")
    
    # Generate response
    print("\n4. RESPONSE (Prover)")
    print("-" * 40)
    
    print("Prover revealing only the requested positions...")
    response = protocol.respond_to_challenge(witness, challenge)
    
    print(f"Revealed {len(response.revealed_steps)} positions:")
    for pos_idx, pos, tile in response.revealed_steps:
        if pos is not None and tile is not None:
            print(f"  Position {pos_idx}: ({pos.x}, {pos.y}) -> {tile}")
        else:
            print(f"  Position {pos_idx}: (out of bounds)")
    
    print(f"\nTotal path length: {response.path_length}")
    print(f"Information revealed: {len(response.revealed_steps)}/{response.path_length} steps ({100*len(response.revealed_steps)/response.path_length:.1f}%)")
    
    # Verify
    print("\n5. VERIFICATION (Verifier)")
    print("-" * 40)
    
    print("Verifier checking response...")
    start_time = time.time()
    is_valid = protocol.verify_response(instance, challenge, response)
    verify_time = time.time() - start_time
    
    print(f"Verification completed in {verify_time:.3f}s")
    print(f"\nResult: {'✓ VALID' if is_valid else '✗ INVALID'}")
    
    # Summary
    print_header("Summary")
    
    total_time = setup_time + witness_time + verify_time
    print(f"Total protocol time: {total_time:.3f}s")
    print(f"Tiling size: {size}x{size} = {len(instance.tiles)} tiles")
    print(f"Path length: {response.path_length} steps")
    print(f"Revealed: {len(response.revealed_steps)} steps ({100*len(response.revealed_steps)/response.path_length:.1f}%)")
    print(f"Verification: {'PASSED' if is_valid else 'FAILED'}")
    
    # Analysis
    print("\nProtocol properties:")
    print("✓ Completeness: Honest prover can convince verifier")
    print("✓ Zero-knowledge: Only reveals challenged positions")
    print("? Soundness: Security depends on path-finding hardness")
    print("⚠️  This is a research prototype - not for production use!")
    
    return is_valid


def run_multiple_trials(num_trials=5):
    """Run multiple protocol executions to show consistency."""
    print_header("Running Multiple Trials")
    
    successes = 0
    times = []
    
    for i in range(num_trials):
        print(f"\nTrial {i+1}/{num_trials}...", end=" ")
        
        protocol = SpectralProtocol(seed=i)
        instance = protocol.create_instance(size=6)
        
        start_time = time.time()
        witness = protocol.generate_witness(instance, path_length=8)
        challenge = protocol.create_challenge(instance, witness.commitment, 3)
        response = protocol.respond_to_challenge(witness, challenge)
        is_valid = protocol.verify_response(instance, challenge, response)
        trial_time = time.time() - start_time
        
        times.append(trial_time)
        if is_valid:
            successes += 1
            print("✓ Valid")
        else:
            print("✗ Invalid")
    
    success_rate = successes / num_trials
    avg_time = sum(times) / len(times)
    
    print(f"\nResults:")
    print(f"  Success rate: {success_rate:.0%} ({successes}/{num_trials})")
    print(f"  Average time: {avg_time:.3f}s")
    print(f"  Time range: {min(times):.3f}s - {max(times):.3f}s")


if __name__ == "__main__":
    print("SpectralZK - Zero-Knowledge Proofs from Aperiodic Tilings")
    print("A research prototype by Daniel Skryseth")
    print()
    
    # Run main demo
    success = run_demo()
    
    # Run multiple trials
    print("\n" + "="*60)
    run_multiple_trials()
    
    print("\n" + "="*60)
    print("Demo complete!")
    
    sys.exit(0 if success else 1)
