from intra import ic
from config import campus_id
from config import color as color
import sys
import pandas as pd
from datetime import datetime, timedelta

def get_logtime(id, start_time, end_time):
    payload = {
        "filter[campus_id]": campus_id,
        'begin_at': start_time,
        'end_at': end_time
    }

    response = ic.get(f"users/{id}/locations_stats", params=payload)
    if response.status_code == 200:
        data = response.json()

    try:
        logtimes = [datetime.strptime(value, '%H:%M:%S.%f') for value in data.values()]
        minutes = int(sum([log.minute for log in logtimes])) / 60
        hours = int(sum([log.hour for log in logtimes]) + minutes)
        minutes = round((minutes - int(minutes)) * 60)
    except ValueError as e:
        return 0, 0
    return hours, minutes

def get_users():
    # Get all users of a piscine
    users = []
    page_num = 1
    pool_month = input(color.BLUE + "POOL MONTH (letters): " + color.RESET)
    pool_year = input(color.BLUE + "POOL YEAR (numbers): " + color.RESET)
    start_time = input(color.BLUE + "START DATE (YYYY-MM-DD): " + color.RESET)
    end_time = input(color.BLUE + "END DATE (YYYY-MM-DD): " + color.RESET)

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
    return users, start_time, end_time

if __name__ == "__main__":
    page_num = 1
    df = pd.DataFrame({
        'id': [],
        'name': [],
        'level': [],
        'login': [],
        'logtime_hours': [],
        'logtime_min': [],
        'total_min': []
    })

    users, start_time, end_time = get_users()

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
                        'level': [float(user['level'])],
                        'login': [user['user']['login']],
                        'logtime_hours': [int(hours)],
                        'logtime_min': [int(minutes)],
                        'total_min': [int(hours) * 24 + int(minutes)]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
            page_num += 1
        else:
            sys.exit(f"Unexpected response: code ${response.status_code}")

    df = df.sort_values(by='total_min', ascending=False)
    df.to_csv('february.csv', index=False)

