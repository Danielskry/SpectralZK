"""
Simple commitment scheme for SpectralZK.

This implements a basic hash-based commitment scheme. In a real implementation, 
this would use a cryptographically secure commitment scheme.
"""

import hashlib
import json
import secrets
from typing import Any, Tuple


class Commitment:
    """
    A simple commitment scheme using hash functions.
    
    Commitment = Hash(value || nonce)
    
    This provides:
    - Hiding: Can't determine value from commitment
    - Binding: Can't find different value with same commitment
    """
    
    @staticmethod
    def create(value: Any, nonce: str = None) -> Tuple[str, str]:
        """
        Create a commitment to a value.
        
        Args:
            value: Value to commit to (will be JSON serialized)
            nonce: Random nonce (generated if not provided)
            
        Returns:
            Tuple of (commitment, nonce)
        """
        if nonce is None:
            nonce = secrets.token_hex(16)
        
        # Serialize value deterministically
        if isinstance(value, str):
            serialized = value
        else:
            serialized = json.dumps(value, sort_keys=True, default=str)
        
        # Create commitment
        data = f"{serialized}||{nonce}"
        commitment = hashlib.sha256(data.encode()).hexdigest()
        
        return commitment, nonce
    
    @staticmethod
    def verify(commitment: str, value: Any, nonce: str) -> bool:
        """
        Verify a commitment opening.
        
        Args:
            commitment: The commitment to verify
            value: The claimed value
            nonce: The nonce used in commitment
            
        Returns:
            True if commitment is valid
        """
        expected_commitment, _ = Commitment.create(value, nonce)
        return commitment == expected_commitment
    
    @staticmethod
    def create_vector(values: list, nonce: str = None) -> Tuple[str, str]:
        """
        Create a commitment to multiple values.
        
        This commits to all values at once, useful for committing
        to an entire path without revealing individual steps.
        """
        return Commitment.create(values, nonce)
