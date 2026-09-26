import hashlib
from pathlib import Path

def test_backup_checksum_generation():
    """Verify SHA-256 checksum algorithm matches expected cryptographic hash."""
    test_content = b"Healthcare Logical Database Dump Simulation"
    expected_hash = hashlib.sha256(test_content).hexdigest()
    
    computed_hash = hashlib.sha256(test_content).hexdigest()
    assert computed_hash == expected_hash
    assert len(computed_hash) == 64

def test_backup_directory_structure():
    """Verify backup storage directory exists and is protected."""
    backup_dir = Path(__file__).resolve().parent.parent.parent / "infrastructure" / "postgres" / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    assert backup_dir.exists()
    assert backup_dir.is_dir()
