import hashlib
import json

from ..logging import get_logger

log = get_logger(__name__)

def stable_json_hash(inp : object) -> bytes:
    """
    Hashes a JSON serializable object in a stable way
    """
    dump = json.dumps(
        inp,
        ensure_ascii=False,
        sort_keys=True,
        indent=None,
        separators=(",",":"),
    )
    return stable_str_hash(dump)

def stable_str_hash(inp : str) -> bytes:
    """
    Hashes an input string
    """
    return stable_bytes_hash(inp.encode('utf-8'))

def stable_bytes_hash(inp : bytes) -> bytes:
    """
    Hashes an input bytes string.
    """
    m = hashlib.new('sha256')
    m.update(inp)
    return m.digest()
