import hashlib
import secrets


def generate_sha256_token():
    # Generate a secure random string (e.g., 32 characters)
    random_string = secrets.token_hex(32)
    sha256_hash = hashlib.sha256(random_string.encode()).hexdigest()
    return random_string, sha256_hash

# Example
if __name__ == "__main__":
    plain, hashed = generate_sha256_token()
    print("Plain token:", plain)
    print("SHA-256 Hash:", hashed)