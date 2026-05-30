import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import httpx
from dotenv import load_dotenv

def test_raw_bithumb():
    load_dotenv()
    
    api_key = os.getenv("BITHUMB_API_KEY")
    secret_key = os.getenv("BITHUMB_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("Keys are missing.")
        return
        
    # Bithumb API Signatures require microseconds timestamp
    nonce = str(int(time.time() * 1000))
    endpoint = "/info/balance"
    
    # Query parameters
    params = {
        "endpoint": endpoint,
        "currency": "ALL"
    }
    
    query_str = urllib.parse.urlencode(params)
    
    # Signature layout: endpoint + \x00 + query_string + \x00 + nonce
    signature_data = f"{endpoint}\x00{query_str}\x00{nonce}"
    
    try:
        # Create Bithumb Signature
        signature = hmac.new(
            secret_key.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # Base64 encode the hex signature
        api_sign = base64.b64encode(signature.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Api-Key": api_key,
            "Api-Sign": api_sign,
            "Api-Nonce": nonce,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        url = "https://api.bithumb.com/info/balance"
        
        print("🔄 [Bithumb Native] Sending request to Bithumb...")
        response = httpx.post(url, data=params, headers=headers, timeout=10.0)
        
        print(f"📥 [Bithumb Native] Response Status: {response.status_code}")
        res_json = response.json()
        print(f"📥 [Bithumb Native] JSON Payload: {res_json}")
        
    except Exception as e:
        print(f"Error during raw request: {str(e)}")

if __name__ == "__main__":
    test_raw_bithumb()
