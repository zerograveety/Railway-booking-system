import requests
import json

headers = {
    "X-RapidAPI-Key": "c00f62a032msh419d6429c8f2eefp150e5fjsn95b0fdf37cac",
    "X-RapidAPI-Host": "irctc1.p.rapidapi.com"
}

# Test Search Station
print("--- SearchStation ---")
try:
    res1 = requests.get("https://irctc1.p.rapidapi.com/api/v1/searchStation", headers=headers, params={"query": "Delhi"})
    print(json.dumps(res1.json(), indent=2)[:500] + "...")
except Exception as e:
    print(e)
    if 'res1' in locals():
        print(res1.text[:200])

# Test train bw stations
print("\n--- TrainsBetweenStations ---")
try:
    # Most v3 APIs use fromStationCode, toStationCode, dateOfJourney
    res2 = requests.get("https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations", headers=headers, params={"fromStationCode":"NDLS", "toStationCode":"MMCT", "dateOfJourney":"2026-06-01"})
    print(json.dumps(res2.json(), indent=2)[:1000] + "...")
except Exception as e:
    print(e)
    if 'res2' in locals():
        print(res2.text[:200])

