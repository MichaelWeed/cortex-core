import os
import requests

def main():
    yacy_url = os.getenv("YACY_URL", "http://localhost:8090")
    password = os.getenv("YACY_ADMIN_PASSWORD", "admin")
    auth = ("admin", password)
    
    try:
        res = requests.get(f"{yacy_url}/api/status.json", auth=auth, timeout=5)
        return res.json()
    except Exception as e:
        return {"error": str(e)}
