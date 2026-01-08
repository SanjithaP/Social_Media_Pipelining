import requests

BASE = "https://a.4cdn.org"

def get_catalog(board: str):
    url = f"{BASE}/{board}/catalog.json"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()

def get_thread(board: str, thread_no: int):
    url = f"{BASE}/{board}/thread/{thread_no}.json"
    r = requests.get(url, timeout=20)
    if r.status_code == 404:
        raise RuntimeError("Thread archived")
    r.raise_for_status()
    return r.json()
