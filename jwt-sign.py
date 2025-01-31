import jwt
import time

# Path to your RSA private key
private_key_path = "/Users/lboschet/.ssh/pure1_rsa"

with open(private_key_path, "r") as key_file:
    private_key = key_file.read()

# Current Unix time
now = int(time.time())

# JWT payload
payload = {
    "iss": "pure1:apikey:DSIsBRHmv2FGCADN",       # Must match your Pure1 application ID
    "sub": "pure1:apikey:DSIsBRHmv2FGCADN",       # Must match your Pure1 application ID
    "aud": "https://api.pure1.purestorage.com/oauth2/1.0/token",  # Pure1 1.0 token endpoint
    "iat": now,                                   # Issued At: current time
    "exp": now + 300                              # Expires after 5 minutes (300 seconds)
}

# Sign the JWT with your RSA private key using RS256
signed_jwt = jwt.encode(
    payload,
    private_key,
    algorithm="RS256"
)

# Print the resulting token
print(signed_jwt)
