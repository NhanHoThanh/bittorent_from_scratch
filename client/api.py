import requests

BASE_URL = "http://localhost:8081/api"


def signup(username, password):
    url = f"{BASE_URL}/signup/"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    # access_token = response.json().get("access_token")
    return response.json()


def login(username, password):
    url = f"{BASE_URL}/login/"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    # access_token = response.json().get("access_token")
    return response.json()


def announce(access_token, info_hash, peer_id, port, uploaded, downloaded, left, event, compact, ip_address=None):
    url = f"{BASE_URL}/announce/"
    payload = {
        "info_hash": info_hash,
        "peer_id": peer_id,
        "port": port,
        "uploaded": uploaded,
        "downloaded": downloaded,
        "left": left,
        "event": event,
        "compact": compact
    }
    if ip_address:
        payload["ip_address"] = ip_address
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
