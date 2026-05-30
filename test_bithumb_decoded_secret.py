import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import httpx
from dotenv import load_dotenv

def test_signature(api_key, secret_key_str, is_decoded=False):
    nonce = str(int(time.time() * 1000))
    endpoint = "/info/balance"
    
    params = {
        "endpoint": endpoint,
        "currency": "ALL"
    }
    
    query_str = urllib.parse.urlencode(params)
    signature_data = f"{endpoint}\x00{query_str}\x00{nonce}"
    
    try:
        # If testing decoded format, decode the base64 secret first
        if is_decoded:
            secret_bytes = base64.b64decode(secret_key_str)
        else:
            secret_bytes = secret_key_str.encode('utf-8')
            
        signature = hmac.new(
            secret_bytes,
            signature_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        api_sign = base64.b64encode(signature.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Api-Key": api_key,
            "Api-Sign": api_sign,
            "Api-Nonce": nonce,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        url = "https://api.bithumb.com/info/balance"
        response = httpx.post(url, data=params, headers=headers, timeout=5.0)
        return response.status_code, response.json()
    except Exception as e:
        return 999, {"error": str(e)}

def run_tests():
    load_dotenv()
    api_key = os.getenv("BITHUMB_API_KEY")
    secret_key = os.getenv("BITHUMB_SECRET_KEY")
    
    print(f"[Test] Connect Key: {api_key}")
    print(f"[Test] Secret Key (Raw): {secret_key}")
    
    # Test 1: Standard UTF-8 Secret
    print("\n🧪 [Test 1] Using Secret Key as plain UTF-8 string...")
    status, res = test_signature(api_key, secret_key, is_decoded=False)
    print(f"Status: {status} -> {res}")
    
    # Test 2: Base64 Decoded Secret
    print("\n🧪 [Test 2] Using Base64 Decoded Secret Key...")
    status, res = test_signature(api_key, secret_key, is_decoded=True)
    print(f"Status: {status} -> {res}")

if __name__ == "__main__":
    run_tests()
