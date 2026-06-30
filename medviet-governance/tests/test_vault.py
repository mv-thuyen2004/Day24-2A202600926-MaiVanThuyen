# tests/test_vault.py
import pytest
import pandas as pd
import json
from src.encryption.vault import SimpleVault

def test_vault_roundtrip():
    vault = SimpleVault()
    original = "Nguyen Van A - CCCD: 012345678901"
    encrypted = vault.encrypt_data(original)
    
    assert "encrypted_dek" in encrypted
    assert "ciphertext" in encrypted
    assert encrypted["algorithm"] == "AES-256-GCM"

    decrypted = vault.decrypt_data(encrypted)
    assert decrypted == original

def test_vault_encrypt_column():
    vault = SimpleVault()
    df = pd.DataFrame({"secret": ["hello", "world"]})
    df_encrypted = vault.encrypt_column(df, "secret")
    
    # Assert values are JSON encoded
    for val in df_encrypted["secret"]:
        payload = json.loads(val)
        assert "encrypted_dek" in payload
        assert "ciphertext" in payload
