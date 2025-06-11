# SpectralZK - Zero-knowledge proofs from aperiodic tilings

SpectralZK is a research prototype exploring whether the complexity of aperiodic tilings can be used as a foundation for zero-knowledge protocols. This is not a production system, but a starting point for new ideas in combinatorial cryptography.

## How It Works

### 1. Tiling Generation
- The system generates deterministic aperiodic patterns using position-dependent hashing:
  ```python
  tile_type = hash(seed, position, neighbors) % num_tile_types
  ```
- **Properties:**
  - Deterministic: Same position always yields same tile
  - Aperiodic: Hash functions prevent global repetition
  - Local constraints: Neighboring tiles influence each other
- **Limitations:**
  - Not a true mathematical aperiodic tiling (like Spectre, Penrose, or Wang tilings)
  - Aperiodicity comes from hash properties, not geometric constraints
  - Local rules are simple heuristics

**Important Note:**
The current implementation does not generate true aperiodic tilings in the mathematical sense. Instead, it uses a hash function to assign tile types based on position and neighbors, which gives some aperiodic-like properties but is not equivalent to Spectre, Penrose, or Wang tilings. The cryptographic properties of true aperiodic tilings are not inherited by this hash-based construction. The security of the protocol relies on unproven assumptions about the hardness of path-finding or position recovery in these hash-based tilings.

### 2. Protocol Structure
- Setup: Public tiling instance
- Witness: Secret path through tiling
- Commitment: Hash-based commitment to path
- Challenge: Request specific positions
- Response: Reveal only requested positions
- Verification: Check consistency

### 3. Security Analysis
- **What works:**
  - Basic protocol flow is correct
  - Commitment scheme provides hiding/binding
  - Verification checks are sound
- **What doesn't:**
  - No formal security proof
  - Path-finding complexity not characterized
  - Vulnerable to brute-force on small instances
  - No reduction to known hard problems

## Background

SpectralZK is based on the mathematics of aperiodic tilings, such as Spectre tiling. These tilings can cover the infinite plane without repeating patterns. If you take a finite patch (a “snapshot”) of such a tiling, that patch can appear in multiple places, but its location in the infinite tiling is not uniquely determined by the patch itself.

This property means that, in theory, if you only reveal a small region of the tiling, an attacker cannot know where you are on the infinite plane. The mathematics suggest that local information does not reveal global position.

The protocol uses this idea: the prover commits to a path through the tiling and only reveals a few steps. The verifier can check these steps, but does not learn the whole path or the global position. In theory, if you could show that finding or verifying certain paths in a tiling is computationally hard, you could base cryptography on this property.

**This is a new direction: there is no known prior work using aperiodic tilings as a cryptographic primitive (as far as I know or could find).** The main open question is whether the underlying problem is actually hard for an attacker. The intuition is strong, but a formal proof is still needed.

This approach fits into the broader area of combinatorial cryptography, where cryptographic protocols are based on combinatorial structures and problems, rather than traditional algebraic ones.

## Experimental Results

- **Aperiodicity:**
  - Testing a 10×10 grid shows no strong periodic patterns. Low repetition rates (< 20%) suggest good mixing from the hash function.
- **Performance:**
  - Instance creation: ~0.001s for 8×8 grid
  - Witness generation: ~0.002s for 10-step path
  - Verification: ~0.0001s per challenged position
  - Scales linearly with grid size and path length.
- **Zero-Knowledge:**
  - The protocol reveals only challenged positions. Path structure remains hidden.


SpectralZK shows that ZK protocols can be built on tiling-based problems, but this is a research experiment, not a practical system. The main value is in exploring alternative ideas for cryptographic protocols and understanding ZK concepts from a different angle.

For real use, stick to traditional ZK systems based on well-studied problems. This prototype is a starting point for research into combinatorial cryptography, not a replacement for existing systems.

## Commercial Use

If you use this project or its ideas in a commercial product or service, please contact Daniel Skryseth.
