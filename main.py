from intra import ic
from config import campus_id
import sys, webbrowser
import pandas as pd
from datetime import datetime, timedelta

def get_logtime(id):
    payload = {
        "filter[campus_id]": campus_id,
        'begin_at': '2023-01-29',
        'end_at': '2023-02-25'
    }

    response = ic.get(f"users/{id}/locations_stats", params=payload)
    if response.status_code == 200:
        data = response.json()

    logtimes = [datetime.strptime(value, '%H:%M:%S.%f') for value in data.values()]
    minutes = int(sum([log.minute for log in logtimes])) / 60
    hours = int(sum([log.hour for log in logtimes]) + minutes)
    minutes = round((minutes - int(minutes)) * 60)
    return hours, minutes

if __name__ == "__main__":
    page_num = 1
    chrome = webbrowser.get('chrome')
    df = pd.DataFrame({
        'id': [],
        'name': [],
        'level': [],
        'login': [],
        'logtime_hours': [],
        'logtime_min': []
    })

    while True:
        payload = {
            "filter[campus_id]": campus_id,
            "range[updated_at]":"2023-01-26T00:00:00.000Z,2023-01-31T00:00:00.000Z",
            "page[size]": 100,
            "page[number]": page_num,
            "sort[level]": "desc",
            "filter[cursus_id]": 9
        }

        response = ic.get("cursus_users", params=payload)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            for user in data:
                hours, minutes = get_logtime(user['user']['id'])
                new_row = pd.DataFrame({
                    'id': [int(user['user']['id'])],
                    'name': [user['user']['displayname']],
                    'level': [float(user['level'])],
                    'login': [user['user']['login']],
                    'logtime_hours': [int(hours)],
                    'logtime_min': [int(minutes)]
                })
                df = pd.concat([df, new_row], ignore_index=True)
            page_num += 1
        else:
            sys.exit(f"Unexpected response: code ${response.status_code}")

    print(df.sort_values(by='id'))
