from intra import ic
from config import campus_id
from config import color as color
import sys
import pandas as pd
from datetime import datetime, timedelta

# Piscine dates:
# September 2021: 2021-09-06 to 2021-10-02 (not included)

def get_logtime(id, start_time, end_time):
    payload = {
        "filter[campus_id]": campus_id,
        'begin_at': start_time,
        'end_at': end_time
    }

    response = ic.get(f"users/{id}/locations_stats", params=payload)
    if response.status_code == 200:
        data = response.json()
    logtimes = []
    for value in data.values():
        if (value.startswith('24')):
            for _ in range(2):
                logtimes.append(datetime.strptime('12:00:00', '%H:%M:%S'))
        else:
            logtimes.append(datetime.strptime(value, '%H:%M:%S.%f'))
    minutes = int(sum([log.minute for log in logtimes])) / 60
    hours = int(sum([log.hour for log in logtimes]) + minutes)
    minutes = round((minutes - int(minutes)) * 60)
    return hours, minutes

def get_users():
    # Get all users of a piscine
    users = []
    page_num = 1
    pool_month = input(color.BLUE + "POOL MONTH (letters): " + color.RESET)
    pool_year = input(color.BLUE + "POOL YEAR (numbers): " + color.RESET)
    start_time = input(color.BLUE + "START DATE (YYYY-MM-DD): " + color.RESET)
    end_time = input(color.BLUE + "END DATE (YYYY-MM-DD): " + color.RESET)
    sorted_by = input(color.BLUE + "SORTED BY (total_time, login, level): " + color.RESET)
    filename = input(color.BLUE + "FILENAME: " + color.RESET)

    while (True):
        payload = {
            'filter[pool_month]': pool_month,
            'filter[pool_year]': pool_year,
            'campus_id': campus_id,
            'page[size]': 100,
            'page[number]': page_num,
        }
        response = ic.get(f"campus/{campus_id}/users", params=payload)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
        else:
            sys.exit(f"Unexpected response: code ${response.status_code}")   
        for user in data:
            users.append(user['id'])
        page_num += 1
    return users, start_time, end_time, sorted_by, filename

if __name__ == "__main__":
    page_num = 1
    df = pd.DataFrame({
        'id': [],
        'name': [],
        'level': [],
        'login': [],
        'logtime_hours': [],
        'logtime_min': [],
        'total_time': []
    })

    users, start_time, end_time, sorted_by, filename = get_users()

    while True:
        payload = {
            "filter[campus_id]": campus_id,
            "page[size]": 100,
            "page[number]": page_num,
            "filter[cursus_id]": 9
        }

        response = ic.get("cursus_users", params=payload)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            for user in data:
                if (user['user']['id'] in users):
                    hours, minutes = get_logtime(user['user']['id'], start_time, end_time)
                    new_row = pd.DataFrame({
                        'id': [int(user['user']['id'])],
                        'name': [user['user']['displayname']],
                        'level': [round(float(user['level']), 2)],
                        'login': [user['user']['login']],
                        'logtime_hours': [int(hours)],
                        'logtime_min': [int(minutes)],
                        'total_time': [int(hours) * 24 + int(minutes)]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
            page_num += 1
        else:
            sys.exit(f"Unexpected response: code ${response.status_code}")

    df = df.sort_values(by=sorted_by, ascending=False)
    df.to_csv(filename, index=False)

