from intra import ic
from config import campus_id
from config import color as color
import sys, os
import pandas as pd
from datetime import datetime, timedelta
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
  th {
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

def get_exams(id):

	payload = {
			"filter[campus]": campus_id,
		}
	response = ic.get(f"users/{id}/projects_users", params=payload)
	if response.status_code == 200:
		data = response.json()
	for project in data:
		if (project['project']['name'] == 'C Piscine Exam 00'):
			return project['final_mark'] if project['final_mark'] else 0
	return 0

def get_logtime(id, begin_time, end_time):
	payload = {
		"filter[campus_id]": campus_id,
		'begin_at': begin_time,
		'end_at': end_time
	}

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

if __name__ == "__main__":
	page_num = 1
	df = pd.DataFrame({
		'id': [],
		'name': [],
		'level': [],
		'login': [],
		'logtime_hours': [],
		'logtime_min': [],
		'total_time': [],
		'exam_00': []
	})
	pool_month = input(color.BLUE + "POOL MONTH (letters): " + color.RESET)
	while (pool_month not in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']):
		pool_month = input(color.BLUE + "POOL MONTH (letters): " + color.RESET)
	pool_year = input(color.BLUE + "POOL YEAR (numbers): " + color.RESET)
	while (len(pool_year) != 4 or not pool_year.isdigit()):
		pool_year = input(color.BLUE + "POOL YEAR (numbers): " + color.RESET)
	sorted_by = input(color.BLUE + "SORTED BY (total_time, exam, level): " + color.RESET)
	if sorted_by == 'exam':
		sorted_by == 'exam_00'

	begin_time = ''
	end_time = ''

	while True:
		payload = {
			"filter[campus_id]": campus_id,
			"page[size]": 100,
			"page[number]": page_num,
			"filter[cursus_id]": 9,
		}	

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
					exam = get_exams(user['user']['id'])
					new_row = pd.DataFrame({
						'id': [int(user['user']['id'])],
						'name': [user['user']['displayname']],
						'level': [round(float(user['level']), 2)],
						'login': [user['user']['login']],
						'logtime_hours': [int(hours)],
						'logtime_min': [int(minutes)],
						'total_time': [int(hours) * 60 + int(minutes)],
						'exam_00': [int(exam)]
					})
					df = pd.concat([df, new_row], ignore_index=True)
			page_num += 1
		else:
			sys.exit(f"Unexpected response: code ${response.status_code}")


	df = df.sort_values(by=sorted_by, ascending=False)
	df['rank'] = np.arange(1, len(df) + 1)
	df.set_index('rank', inplace = True)
	html_table = df.to_html()
	file = sorted_by + '.html'
	with open(file, 'w') as f:
		f.write(style)
	with open(file, 'a') as f:
		f.write(html_table)
	os.system(f"open {file}")
