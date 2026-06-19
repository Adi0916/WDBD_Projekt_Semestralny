import requests
import logging
import os
from requests.auth import HTTPBasicAuth

import requests
import os
import logging

# Ustaw te zmienne w środowisku (export CLIENT_ID=... itp.)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BASE_URL = "https://opensky-network.org/api"
TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

def get_access_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    return response.json().get("access_token")

def fetch_all_flights(begin_ts, end_ts):
    try:
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"begin": int(begin_ts), "end": int(end_ts)}

        response = requests.get(f"{BASE_URL}/flights/all", params=params, headers=headers, timeout=20)

        if response.status_code == 404:
            return []

        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Błąd API: {e}")
        return []

def fetch_states(bbox=None):

    url = f"{BASE_URL}/states/all"
    params = {}

    if bbox and len(bbox) == 4:
       params = {
            "lamin": bbox[0],
            "lomin": bbox[1],
            "lamax": bbox[2],
            "lomax": bbox[3]
        }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    return response.json()

'''
def fetch_all_flights(begin_ts, end_ts):
    url = f"{BASE_URL}/flights/all"
    params = {
        "begin": int(begin_ts),
        "end": int(end_ts)
    }
    response = requests.get(url, params=params, timeout=20)

    if response.status_code == 404:
        logging.warning(f"No flight data available for the period {begin_ts} - {end_ts}.")
        return []
    response.raise_for_status()
    return response.json()
'''
