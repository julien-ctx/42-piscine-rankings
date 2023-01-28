import requests
from intra import ic
from config import campus_id
import webbrowser

page_num = 1
total = 0
chrome = webbrowser.get('chrome')

while True:
    payload = {
        "filter[campus_id]": campus_id,
        "range[updated_at]":"2023-01-25T00:00:00.000Z,2023-01-30T00:00:00.000Z",
        "page[size]": 100,
        "page[number]": page_num
    }

    response = ic.get("cursus_users", params=payload)
    if response.status_code == 200: # Is the status OK?
        data = response.json()
    if not data:
        break
    for user in data:
        total += 1
        print(user)
    page_num += 1

print(f"{total} registered users")
