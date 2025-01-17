import jwt

def decode_and_verify_jwt(token, client_secret, client_id):
    try:
        # Decode JWT
        decoded = jwt.decode(token, client_secret, algorithms=["HS256"], audience=client_id)
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
