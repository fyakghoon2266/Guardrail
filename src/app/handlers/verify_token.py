import os

def verify_token(Authentication_token: str) -> bool:
    auth_header = Authentication_token
    if not auth_header:
        return 400

    token = auth_header.split("Bearer ")[-1] if "Bearer " in auth_header else None
    correct_token = os.getenv("API_TOKEN")
    
    if token != correct_token:
        return 401
    
    return None