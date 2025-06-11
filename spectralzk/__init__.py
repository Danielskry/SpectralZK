"""
SpectralZK - Zero-knowledge proofs from aperiodic tilings.

A simple research prototype exploring whether the complexity of aperiodic
tilings can be used for zero-knowledge protocols. This is not a production
system. The code is straightforward and meant for experimentation and learning.
"""

from .protocol import SpectralProtocol, Instance, Witness, Challenge, Response
from .tiling import Tiling, Point
from .commitment import Commitment

__version__ = "0.1.0"
__all__ = [
    "SpectralProtocol",
    "Instance", 
    "Witness",
    "Challenge",
    "Response",
    "Tiling",
    "Point",
    "Commitment"
]
