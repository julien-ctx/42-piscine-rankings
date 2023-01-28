from intra import ic
from config import campus_id
import sys
import pandas as pd
from datetime import datetime, timedelta
import webbrowser

page_num = 1
chrome = webbrowser.get('chrome')
df = pd.DataFrame({'Name': [], 'Level': [], 'Login': []})

# while True:
#     payload = {
#         "filter[campus_id]": campus_id,
#         "range[updated_at]":"2023-01-26T00:00:00.000Z,2023-01-31T00:00:00.000Z",
#         "page[size]": 100,
#         "page[number]": page_num,
#         "sort[level]": "desc",
#         "filter[cursus_id]": 9
#     }

#     response = ic.get("cursus_users", params=payload)
#     if response.status_code == 200:
#         data = response.json()
#         if not data:
#             break
#         for user in data:
#             new_row = pd.DataFrame({
#                 'Name': [user['user']['displayname']],
#                 'Level': [float(user['level'])],
#                 'Login': [user['user']['login']]
#             })
#             df = pd.concat([df, new_row], ignore_index=True)
#         page_num += 1
#     else:
#         sys.exit(f"Unexpected response: code ${response.status_code}")

# print(df)



payload = {
    "filter[campus_id]": campus_id,
    'begin_at': '2023-01-01',
    'end_at': '2023-01-31'
}

response = ic.get("users/97751/locations_stats", params=payload)
if response.status_code == 200:
    data = response.json()

logtimes = [datetime.strptime(value, '%H:%M:%S.%f') for value in data.values()]

# extract hours from datetime objects
hours = int(sum([log.hour for log in logtimes]))
minutes = int(sum([log.minute for log in logtimes])) / 60
hours += minutes
minutes = round((minutes - int(minutes)) * 60)

print(hours, minutes)
