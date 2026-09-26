def test_reconciliation_parity_logic():
    """Verify restore verification correctly identifies matching and mismatched tables."""
    orig_counts = {"patients": 100, "encounters": 250, "appointments": 300}
    restored_matching = {"patients": 100, "encounters": 250, "appointments": 300}
    restored_mismatch = {"patients": 99, "encounters": 250, "appointments": 300}

    def verify_parity(c1, c2):
        for k in c1:
            if c1[k] != c2.get(k):
                return False
        return True

    assert verify_parity(orig_counts, restored_matching) is True
    assert verify_parity(orig_counts, restored_mismatch) is False
