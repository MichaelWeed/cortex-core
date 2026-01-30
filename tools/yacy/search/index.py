import os
import requests

def main(query, max_results=10):
    yacy_url = os.getenv("YACY_URL", "http://localhost:8090")
    params = {
        "query": query,
        "maximumRecords": max_results,
        "resource": "global",
        "urlMaskFilter": ".*",
        "preferResource": "true",
        "nav": "all"
    }
    try:
        res = requests.get(f"{yacy_url}/yacysearch.json", params=params, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}
