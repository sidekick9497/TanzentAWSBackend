import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


# -----------------------------------------------------------
# Hard-coded AES-256 key (base64 for readability)
# Replace with your own!
# -----------------------------------------------------------
_MASTER_KEY_B64 = "KGWhx1ofF+SeSs808WOW06GabqufpHM0DcMZOmAoERo="
_MASTER_KEY = base64.b64decode(_MASTER_KEY_B64)


# -----------------------------------------------------------
# Encrypt → returns ONE base64 string
# Format: base64( iv[12] + tag[16] + ciphertext[n] )
# -----------------------------------------------------------
def encrypt_text(plaintext: str) -> str:
    iv = get_random_bytes(12)  # 96-bit
    cipher = AES.new(_MASTER_KEY, AES.MODE_GCM, nonce=iv)

    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-16"))

    final_bytes = iv + tag + ciphertext
    final_b64 = base64.b64encode(final_bytes).decode()

    return final_b64


# -----------------------------------------------------------
# Decrypt from ONE base64 string
# -----------------------------------------------------------
def decrypt_text(b64data: str) -> str:
    raw = base64.b64decode(b64data)

    iv = raw[:12]
    tag = raw[12:28]
    ciphertext = raw[28:]

    cipher = AES.new(_MASTER_KEY, AES.MODE_GCM, nonce=iv)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    return plaintext.decode("utf-16")
