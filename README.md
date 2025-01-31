# Package to start Pure1 API client python developpment

This repository was made to help customers to build and develop their first Pure1 API Client.

## Authentication Integrating with Pure1 via its REST API

When integrating with Pure1 via its REST API, you need a secure and reliable way to prove your identity. Pure1 employs public-key cryptography to generate and validate digital signatures, ensuring that only authorized clients can request data or services.

---

### Why Is Authentication Needed?

Pure1’s authentication flow ensures only authorized and trusted users can access or manipulate storage data and analytics. This level of access control is crucial for:

- Maintaining data integrity  
- Preventing malicious activity  
- Complying with industry security standards

---

### How Is It Secured?

1. **Public-Key Cryptography**  
   By using a private key that never leaves your control, the system dramatically reduces the risk of unauthorized access.

2. **Short-Lived Access Tokens**  
   Tokens eventually expire, which limits the window of opportunity if a token is ever compromised.

3. **Industry-Standard JWT**  
   JWTs are a well-established mechanism for securely transmitting information.

This multi-layered approach ensures that every API interaction is both authenticated (proving who you are) and authorized (enforcing the right level of access), delivering a robust security framework for your data management needs.

---

### Pure1 High-Level Authentication Steps

#### 1. Key Generation and Registration
- You create a public and private key pair using a cryptographic tool (like OpenSSL).  
- Upload the **public key** to Pure1.  
- Pure1 stores this key and uses it to verify your future signatures.

#### 2. Creating a Signed JWT (JSON Web Token)
- Create a JWT containing essential information (e.g., client identifier, expiry date).  
- Sign the JWT with your **private key**.  
- This signature confirms the request really comes from you (because only you have the matching private key).

#### 3. Exchanging for an Access Token
- Send the signed JWT to Pure1’s authentication endpoint.  
- Pure1 verifies your signature using the **public key** you registered.  
- If valid, Pure1 issues you a **short-lived access token**.  
- Include this token in subsequent API calls to prove you’re authenticated.

#### 4. Making API Requests
- Every request to Pure1 includes the **access token** in the Authorization header.  
- Pure1 checks the token’s validity and identity context.  
- If all checks pass, your API call proceeds.

---

### OAuth 2.0-Like Flow

Pure1 uses a JWT-based flow that follows the OAuth 2.0 pattern, closely resembling an OAuth 2.0 “client credentials” flow with private key JWT for authentication. Essentially:

1. **Sign a JWT** with your private key.  
2. **Pure1 verifies** it with your registered public key.  
3. **Pure1 issues** an OAuth 2.0-style access token.  
4. **Include** that token in your API calls.

This mechanism ensures secure, authenticated access to Pure1’s data and services.

## Python packages

Install the requred python packages:

    % pip install -r requirements.tx

## Run your first Pure1 API client python script (/arrays endpoint)

    % python3 get_pure1_fleet_infos.py  pure1:apikey:DSIxxxxxx2FGCADN /Users/user1/.ssh/my_ssh_private_key.pem

