import requests, os
from datetime import datetime, timedelta
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

SEAT_TYPES = [
    "S_CHAIR", "SHOVAN", "SNIGDHA", "F_SEAT", "F_CHAIR", "AC_S", "F_BERTH", "AC_B", "SHULOV", "AC_CHAIR"
]

TOKEN = None
TOKEN_TIMESTAMP = None

def set_token(token: str):
    global TOKEN, TOKEN_TIMESTAMP
    TOKEN = token
    TOKEN_TIMESTAMP = datetime.utcnow()

def fetch_token() -> str:
    mobile_number = os.getenv("FIXED_MOBILE_NUMBER")
    password = os.getenv("FIXED_PASSWORD")
    if not mobile_number or not password:
        raise Exception("Fixed mobile number or password not configured.")
    url = f"https://railspaapi.shohoz.com/v1.0/web/auth/sign-in"
    payload = {"mobile_number": mobile_number, "password": password}
    max_retries = 2
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 422:
                raise Exception("Server-side Mobile Number or Password is incorrect. Please wait a moment while we resolve this issue.")
            elif response.status_code >= 500:
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception("We're facing a problem with the Bangladesh Railway website. Please try again in a few minutes.")
                continue
            data = response.json()
            token = data["data"]["token"]
            return token
        except requests.RequestException as e:
            error_str = str(e)
            if "NameResolutionError" in error_str or "Failed to resolve" in error_str:
                raise Exception("We couldn't reach the Bangladesh Railway website. Please try again in a few minutes.")
            raise Exception(f"Failed to fetch token: {error_str}")

def fetch_train_data(model: str, api_date: str) -> dict:
    url = "https://railspaapi.shohoz.com/v1.0/web/train-routes"
    payload = {
        "model": model,
        "departure_date_time": api_date
    }
    headers = {'Content-Type': 'application/json'}

    max_retries = 2
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 403:
                raise Exception("Rate limit exceeded. Please try again later.")
                
            if response.status_code >= 500:
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception("We're unable to connect to the Bangladesh Railway website right now. Please try again in a few minutes.")
                continue
                
            response.raise_for_status()
            return response.json().get("data")
        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response and e.response.status_code == 403:
                raise Exception("Rate limit exceeded. Please try again later.")
            raise

def get_seat_availability(train_model: str, journey_date: str, from_city: str, to_city: str) -> tuple:
    global TOKEN
    if not TOKEN:
        TOKEN = fetch_token()
        set_token(TOKEN)

    url = "https://railspaapi.shohoz.com/v1.0/web/bookings/search-trips-v2"
    params = {
        "from_city": from_city,
        "to_city": to_city,
        "date_of_journey": journey_date,
        "seat_class": "SHULOV"
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}

    max_retries = 2
    retry_count = 0
    has_retried_with_new_token = False

    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 401 and not has_retried_with_new_token:
                try:
                    error_data = response.json()
                    error_messages = error_data.get("error", {}).get("messages", [])
                    if isinstance(error_messages, list) and any("Invalid User Access Token!" in msg for msg in error_messages):
                        TOKEN = fetch_token()
                        set_token(TOKEN)
                        headers["Authorization"] = f"Bearer {TOKEN}"
                        has_retried_with_new_token = True
                        continue
                except ValueError:
                    TOKEN = fetch_token()
                    set_token(TOKEN)
                    headers["Authorization"] = f"Bearer {TOKEN}"
                    has_retried_with_new_token = True
                    continue
            
            if response.status_code == 403:
                raise Exception("Rate limit exceeded. Please try again later.")
                
            if response.status_code >= 500:
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception("We're unable to connect to the Bangladesh Railway website right now. Please try again in a few minutes.")
                continue
                
            response.raise_for_status()
            trains = response.json().get("data", {}).get("trains", [])

            for train in trains:
                if train.get("train_model") == train_model:
                    seat_info = {stype: {"online": 0, "offline": 0, "fare": 0, "vat_amount": 0} for stype in SEAT_TYPES}
                    for seat in train.get("seat_types", []):
                        stype = seat["type"]
                        if stype in seat_info:
                            fare = float(seat["fare"])
                            vat_amount = float(seat["vat_amount"])
                            if stype in ["AC_B", "F_BERTH"]:
                                fare += 50
                            seat_info[stype] = {
                                "online": seat["seat_counts"]["online"],
                                "offline": seat["seat_counts"]["offline"],
                                "fare": fare,
                                "vat_amount": vat_amount
                            }
                    return (from_city, to_city, seat_info)

            return (from_city, to_city, None)

        except requests.RequestException as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code == 401 and not has_retried_with_new_token:
                try:
                    error_data = e.response.json()
                    error_messages = error_data.get("error", {}).get("messages", [])
                    if isinstance(error_messages, list) and any("Invalid User Access Token!" in msg for msg in error_messages):
                        TOKEN = fetch_token()
                        set_token(TOKEN)
                        headers["Authorization"] = f"Bearer {TOKEN}"
                        has_retried_with_new_token = True
                        continue
                except ValueError:
                    TOKEN = fetch_token()
                    set_token(TOKEN)
                    headers["Authorization"] = f"Bearer {TOKEN}"
                    has_retried_with_new_token = True
                    continue
                    
            if hasattr(e, 'response') and e.response and e.response.status_code == 403:
                raise Exception("Rate limit exceeded. Please try again later.")
            return (from_city, to_city, None)

def clean_halt_times(routes):
    for stop in routes:
        arrival_time = stop.get("arrival_time")
        departure_time = stop.get("departure_time")
        halt = stop.get("halt")
        
        if arrival_time and departure_time and halt:
            try:
                arrival_clean = arrival_time.replace(" BST", "").strip()
                arr_hour_min, arr_am_pm = arrival_clean.split(' ')
                arr_hour, arr_minute = map(int, arr_hour_min.split(':'))
                arr_am_pm = arr_am_pm.lower()
                
                if arr_am_pm == "pm" and arr_hour != 12:
                    arr_hour += 12
                elif arr_am_pm == "am" and arr_hour == 12:
                    arr_hour = 0
                
                departure_clean = departure_time.replace(" BST", "").strip()
                dep_hour_min, dep_am_pm = departure_clean.split(' ')
                dep_hour, dep_minute = map(int, dep_hour_min.split(':'))
                dep_am_pm = dep_am_pm.lower()
                
                if dep_am_pm == "pm" and dep_hour != 12:
                    dep_hour += 12
                elif dep_am_pm == "am" and dep_hour == 12:
                    dep_hour = 0
                
                arrival_minutes = arr_hour * 60 + arr_minute
                departure_minutes = dep_hour * 60 + dep_minute
                
                if departure_minutes < arrival_minutes:
                    departure_minutes += 24 * 60
                
                halt_minutes = departure_minutes - arrival_minutes
                
                try:
                    halt_int = int(halt)
                    if halt_int > 120 or halt_int < 0:
                        stop["halt"] = str(halt_minutes)
                except (ValueError, TypeError):
                    stop["halt"] = str(halt_minutes)
                    
            except Exception:
                continue

def compute_matrix(train_model: str, journey_date_str: str, api_date_format: str) -> dict:
    train_data = fetch_train_data(train_model, api_date_format)
    if not train_data or not train_data.get("train_name") or not train_data.get("routes"):
        raise Exception("No information found for this train. Please try another train or date.")

    clean_halt_times(train_data['routes'])

    stations = [r['city'] for r in train_data['routes']]
    days = train_data['days']
    train_name = train_data['train_name']
    routes = train_data['routes']
    base_date = datetime.strptime(journey_date_str, "%d-%b-%Y")
    current_date = base_date
    previous_time = None

    MAX_REASONABLE_GAP_HOURS = 12

    station_dates = {}
    for i, stop in enumerate(routes):
        stop["display_date"] = None
        time_str = stop.get("departure_time") or stop.get("arrival_time")

        if time_str and "BST" in time_str:
            time_clean = time_str.replace(" BST", "").strip()
            try:
                hour_min, am_pm = time_clean.split(' ')
                hour, minute = map(int, hour_min.split(':'))
                am_pm = am_pm.lower()

                if am_pm == "pm" and hour != 12:
                    hour += 12
                elif am_pm == "am" and hour == 12:
                    hour = 0

                current_time = timedelta(hours=hour, minutes=minute)

                if previous_time is not None:
                    time_diff = (current_time - previous_time).total_seconds() / 3600
                    if current_time < previous_time:
                        time_diff = ((current_time + timedelta(days=1)) - previous_time).total_seconds() / 3600
                        if time_diff < MAX_REASONABLE_GAP_HOURS:
                            routes[i - 1]["display_date"] = current_date.strftime("%d %b")
                            current_date += timedelta(days=1)
                            stop["display_date"] = current_date.strftime("%d %b")
                        else:
                            hours = int(time_diff)
                            minutes = int((time_diff - hours) * 60)

                previous_time = current_time
            except Exception:
                continue

        station_dates[stop['city']] = current_date.strftime("%Y-%m-%d")

    total_duration = train_data.get('total_duration', 'N/A')

    weekday_short = datetime.strptime(journey_date_str, "%d-%b-%Y").strftime("%a")
    weekday_full = datetime.strptime(journey_date_str, "%d-%b-%Y").strftime("%A")
    
    # Comment out these two lines below as trains run every day temporarily on EID journey
    if weekday_short not in days:
        raise Exception(f"{train_name} does not run on {weekday_full}.")

    fare_matrices = {
        seat_type: {from_city: {} for from_city in stations} for seat_type in SEAT_TYPES
    }

    seat_type_has_data = {seat_type: False for seat_type in SEAT_TYPES}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(
                get_seat_availability,
                train_model,
                datetime.strptime(station_dates[from_city], "%Y-%m-%d").strftime("%d-%b-%Y"),
                from_city,
                to_city
            )
            for i, from_city in enumerate(stations)
            for j, to_city in enumerate(stations)
            if i < j
        ]
        for future in as_completed(futures):
            from_city, to_city, seat_info = future.result()
            for seat_type in SEAT_TYPES:
                fare_matrices[seat_type][from_city][to_city] = (
                    seat_info.get(seat_type, {"online": 0, "offline": 0, "fare": 0})
                    if seat_info else {"online": 0, "offline": 0, "fare": 0}
                )
                if seat_info:
                    for seat_type in SEAT_TYPES:
                        if seat_info[seat_type]["online"] + seat_info[seat_type]["offline"] > 0:
                            seat_type_has_data[seat_type] = True

    if not any(seat_type_has_data.values()):
        raise Exception("No seats available for the selected train and date. Please try a different date or train.")
    
    station_dates_formatted = {
        station: datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%b-%Y")
        for station, date_str in station_dates.items()
    }

    unique_dates = set(station_dates.values())
    has_segmented_dates = len(unique_dates) > 1
    next_day_str = ""
    prev_day_str = ""
    if has_segmented_dates:
        date_obj = datetime.strptime(journey_date_str, "%d-%b-%Y")
        next_day_obj = date_obj + timedelta(days=1)
        prev_day_obj = date_obj - timedelta(days=1)
        next_day_str = next_day_obj.strftime("%d-%b-%Y")
        prev_day_str = prev_day_obj.strftime("%d-%b-%Y")

    return {
        "train_model": train_model,
        "train_name": train_name,
        "date": journey_date_str,
        "stations": stations,
        "seat_types": SEAT_TYPES,
        "fare_matrices": fare_matrices,
        "has_data_map": seat_type_has_data,
        "routes": routes,
        "days": days,
        "total_duration": total_duration,
        "station_dates": station_dates,
        "station_dates_formatted": station_dates_formatted,
        "has_segmented_dates": has_segmented_dates,
        "next_day_str": next_day_str,
        "prev_day_str": prev_day_str,
    }