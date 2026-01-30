import os
import requests

def main(urls, depth=2):
    yacy_url = os.getenv("YACY_URL", "http://localhost:8090")
    password = os.getenv("YACY_ADMIN_PASSWORD", "admin")
    auth = ("admin", password)
    
    results = []
    for url in urls:
        payload = {
            "crawlingstart": "true",
            "crawlingMode": "url",
            "url": url,
            "depth": str(depth),
            "recrawl": "true"
        }
        try:
            res = requests.post(f"{yacy_url}/CrawlStart_p.html", data=payload, auth=auth, timeout=10)
            results.append({"url": url, "status": res.status_code})
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return results
