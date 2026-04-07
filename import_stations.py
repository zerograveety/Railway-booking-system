import requests
import json
from app import app, db, Station

def download_stations():
    print("Downloading 8,990+ station data from datameet/railways...")
    url = "https://raw.githubusercontent.com/datameet/railways/master/stations.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error downloading data: {response.status_code}")
        return None

def import_to_db(data):
    if not data or 'features' not in data:
        print("Invalid data format")
        return

    print("Parsing features and cleaning duplicates...")
    features = data['features']
    stations_map = {} # code -> {name, code, city}
    
    for feature in features:
        props = feature.get('properties', {})
        code = props.get('code')
        name = props.get('name')
        
        if code and name:
            # Clean up names (standardize case)
            code = code.strip().upper()
            name = name.strip().title()
            state = props.get('state', 'India') or 'India'
            
            stations_map[code] = {
                'name': name,
                'code': code,
                'city': state
            }

    print(f"Found {len(stations_map)} unique stations.")
    
    with app.app_context():
        # Get existing codes to avoid UniqueViolation
        existing_codes = {s.code for s in db.session.query(Station.code).all()}
        
        new_stations = []
        for code, info in stations_map.items():
            if code not in existing_codes:
                new_stations.append(info)
        
        if not new_stations:
            print("No new stations to add.")
            return

        print(f"Adding {len(new_stations)} new stations to PostgreSQL in batches...")
        batch_size = 1000
        for i in range(0, len(new_stations), batch_size):
            batch = new_stations[i:i + batch_size]
            print(f"Uploading batch {i//batch_size + 1}...")
            db.session.bulk_insert_mappings(Station, batch)
            db.session.commit()
            
        print("Success! All stations are now in PostgreSQL.")

if __name__ == "__main__":
    station_data = download_stations()
    if station_data:
        import_to_db(station_data)
