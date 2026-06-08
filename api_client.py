import requests
import logging 

BASE_URL = "https://opensky-network.org/api"

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