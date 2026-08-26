import hashlib
import json
from typing import Any

def generate_record_hash(data: dict[str, Any]) -> str:
    """
    Generates a deterministic SHA-256 hash for a canonical record dictionary.
    Keys are sorted to ensure determinism regardless of JSON ordering.
    """
    # Create a deterministic string representation
    canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
