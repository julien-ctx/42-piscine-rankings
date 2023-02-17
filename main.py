from includes.intra import ic
from includes.config import campus_id, color as color
from datetime import datetime, timedelta
import sys, os
import pandas as pd
import numpy as np

style = """
<style>
  .dataframe {
    border-collapse: separate;
    border-spacing: 10px;
    font-family: 'Open Sans', sans-serif;
    font-size: 14px;
    border-radius: 10px;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    margin: 50px auto;
    width: 80%;
  }
  th, td {
    padding: 20px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }
  thead tr {
    background-color: #f2f2f2;
  }
  th, a {
    background-color: #333;
    color: #fff;
    font-size: 16px;
    font-weight: bold;
  }
  td {
    background-color: #f9f9f9;
    border-radius: 2px;
  }
</style>
"""

def get_exam(id, exam):
	payload = {
		"filter[campus]": campus_id,
	}
	try:
		response = ic.get(f"users/{id}/projects_users", params=payload)
		if response.status_code == 200:
			data = response.json()
			for project in data:
				if (project['project']['name'] == exam):
					return project['final_mark'] if project['final_mark'] else None
		else:
			sys.exit(f"Unexpected response: code ${response.status_code}")
	except Exception as e:
		sys.exit(e)

def get_logtime(id, begin_time, end_time):
	payload = {
		"filter[campus_id]": campus_id,
		'begin_at': begin_time,
		'end_at': end_time
	}
	try:
		response = ic.get(f"users/{id}/locations_stats", params=payload)
		if response.status_code == 200:
			data = response.json()
			logtimes = []
			for value in data.values():
				try:
					logtimes.append(datetime.strptime(value, '%H:%M:%S.%f'))
				except ValueError:
					for _ in range(2):
						logtimes.append(datetime.strptime('12:00:00', '%H:%M:%S'))
			minutes = int(sum([log.minute for log in logtimes])) / 60
			hours = int(sum([log.hour for log in logtimes]) + minutes)
			minutes = round((minutes - int(minutes)) * 60)
			return hours, minutes
		else:
			sys.exit(f"Unexpected response: code ${response.status_code}")
	except Exception as e:
		sys.exit(e)

if __name__ == "__main__":
	page_num = 1
	df = pd.DataFrame({})
	pool_month = input(color.BLUE + "POOL MONTH (letters): " + color.RESET)
	while (pool_month not in ['january', 'february', 'march', 'april', 'may', 'june', 'july', \
	'august', 'september', 'october', 'november', 'december']):
		pool_month = input(color.BLUE + "POOL MONTH (letters): " + color.RESET)
	pool_year = input(color.BLUE + "POOL YEAR (numbers): " + color.RESET)
	while (len(pool_year) != 4 or not pool_year.isdigit()):
		pool_year = input(color.BLUE + "POOL YEAR (numbers): " + color.RESET)

	begin_time = ''
	end_time = ''

	while True:
		payload = {
			"filter[campus_id]": campus_id,
			"page[size]": 100,
			"page[number]": page_num,
			"filter[cursus_id]": 9,
		}	
		try:
			response = ic.get("cursus_users", params=payload)
			if response.status_code == 200:
				data = response.json()
				if not data:
					break
				for user in data:
					if user['user']['pool_month'] == pool_month \
					and user['user']['pool_year'] == pool_year:
						print(f"\033[K{color.BOLD}Retrieving data from {user['user']['login']}{color.RESET}", end='\r')
						if not begin_time:
							begin_time = user['begin_at'].split('T')[0]
						if not end_time:
							end_time = user['end_at'].split('T')[0]
						hours, minutes = get_logtime(user['user']['id'], begin_time, end_time)
						rows = pd.DataFrame({
							'id': [int(user['user']['id'])],
							'name': [user['user']['displayname']],
							'level': [round(float(user['level']), 2)],
							'login': [user['user']['login']],
							'logtime_hours': [int(hours)],
							'logtime_min': [int(minutes)],
							'total_time': [int(hours) * 60 + int(minutes)],
							
						})
						for exam in ['C Piscine Exam 00', 'C Piscine Exam 01', 'C Piscine Exam 02', 'C Piscine Final Exam']:
							mark = get_exam(user['user']['id'], exam)
							rows = rows.assign(**{exam[10:len(exam)].lower().replace(' ', '_'): int(mark) if mark else None})
						df = pd.concat([df, rows], ignore_index=True)
				page_num += 1
			else:
				sys.exit(f"Unexpected response: code ${response.status_code}")
		except Exception as e:
			sys.exit(e)

	df = df.dropna(axis=1, how='all')
	columns = df.columns
	if not os.path.exists('dataframes'):
		os.mkdir('dataframes')
	for column in columns:
		tmp = df.sort_values(by=column, ascending=False)
		tmp['rank'] = np.arange(1, len(tmp) + 1)
		tmp.set_index('rank', inplace = True)
		html = tmp.to_html()
		for link in columns:
			html = html.replace(f'<th>{link}</th>', f'<th><a href="./{link}.html">{link}</a></th>')
		with open(f"dataframes/{column}.html", 'w') as f:
			f.write(style)
			f.write(f'<h1 style="text-align: center">{column} rankings</h1>')
			f.write('<h3 style="text-align: center">You can click on a column to sort the array by its values</h3>')
		with open(f"dataframes/{column}.html", 'a') as f:
			f.write(html)
	if os.system(f"open dataframes/level.html"):
		sys.exit("Error: couldn't open HTML default page")
