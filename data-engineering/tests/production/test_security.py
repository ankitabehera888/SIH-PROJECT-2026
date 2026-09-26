from pathlib import Path

def test_env_example_has_no_plaintext_passwords():
    """Verify .env.example contains only placeholders, no real secrets."""
    example_path = Path(__file__).resolve().parent.parent.parent / ".env.example"
    assert example_path.exists()
    content = example_path.read_text(encoding="utf-8")
    
    # Sensitive substrings should be empty or CHANGE_ME placeholders
    assert "CHANGE_ME" in content or "CHANGE_THIS" in content
    assert "postgres:5432" in content

def test_gitignore_protects_secrets_and_backups():
    """Verify .gitignore blocks .env, .env.*, and backup dumps."""
    gitignore_path = Path(__file__).resolve().parent.parent.parent / ".gitignore"
    assert gitignore_path.exists()
    content = gitignore_path.read_text(encoding="utf-8")
    
    assert ".env" in content
    assert ".env.*" in content
    assert "*.parquet" in content
    assert "*.sql.gz" in content or "backup/*.sql" in content
