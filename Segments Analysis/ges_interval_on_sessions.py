import os
import csv


# Extract features from each log file in a dictionary
'''
def CalIntervals(address):
	id_status = [0]*6
	times = [[]]*6
	intervals = [[]]*6

	with open(address) as flog:
		reader = csv.reader(flog, dialect='excel')
		
		for row in reader:

			# Skip the first two lines
			if row == [] or row[0] == 'Time':
				continue

			# The id is from 1 while the id_status is from 0
			# so -1 is needed to access the id_status
			current_id = int(row[1]) - 1 

			# add the ids to users
			if row[2] == ' RSARR':
				# If current_id has not been registered
				if id_status[current_id] == 0:
					id_status[current_id] = 1

			elif row[2] == ' RSGON':
				# If current_id has been registered
				if id_status[current_id] == 1:
					id_status[current_id] = 0

			# count the number of gestures
			elif row[2] == ' RMRIG':
				if id_status[current_id] == 1:
					interv = CalLength(row[0], times[current_id][-1])
					times[current_id].append(row[0])
					intervals[current_id].append(interv)

			elif row[2] == ' RMLEF':
				abs

			elif row[2] == ' RMORE':
				abs

			elif row[2] == ' RDONE':
				abs
'''


# Output csv file
def OutPut(name, res):
	with open(name, 'w', newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['id', 'interval'])

		for i, ele in enumerate(res):
				writer.writerow([i, ele])


# Calculate the length of a period
def CalLength(start, end):
	# print(start, '\n', end)
	s_hour = start[0:2]
	s_min = start[3:5]
	s_sec = start[6:]

	e_hour = end[0:2]
	e_min = end[3:5]
	e_sec = end[6:]

	h = int(e_hour) - int(s_hour)
	m = int(e_min) - int(s_min)
	s = float(e_sec) - float(s_sec)

	res = h*3600 + m*60 + s
	# print(res)
	return res


# Calculate all intervals
def CalIntervals1(address):
	times = []
	intervals = []

	with open(address) as flog:
		reader = csv.reader(flog, dialect='excel')
		
		for row in reader:

			# Skip the first two lines
			if row == [] or row[0] == 'Time':
				continue

			# Skip the fake ids
			current_id = int(row[1])
			if current_id < 0:
				continue

			# Extract intervals
			if row[2] == ' RMRIG' or row[2] == ' RMLEF' or row[2] == ' RMORE' or row[2] == ' RDONE':
				if len(times) > 0:
					interv = CalLength(times[-1], row[0])
					intervals.append(interv)
				times.append(row[0])
	# print(len(intervals))
	return intervals


# Calculate intervals of the same users
def CalIntervals2(address):
	times = [[] for i in range(6)]
	intervals = []

	with open(address) as flog:
		reader = csv.reader(flog, dialect='excel')
		
		for row in reader:

			# Skip the first two lines
			if row == [] or row[0] == 'Time':
				continue

			# Skip the fake ids
			current_id = int(row[1])
			if current_id < 0:
				continue

			# Extract intervals
			if row[2] == ' RMRIG' or row[2] == ' RMLEF' or row[2] == ' RMORE' or row[2] == ' RDONE':
				time = times[current_id-1]

				if len(time) > 0:
					interv = CalLength(time[-1], row[0])
					intervals.append(interv)
				
				times[current_id-1].append(row[0])
				# print(times)

	# print(len(intervals))
	return intervals


# Calculate the intervals of consecutive same players
def CalIntervals3(address):
	times = []
	intervals = []
	last_id = 0

	with open(address) as flog:
		reader = csv.reader(flog, dialect='excel')
		
		for row in reader:

			# Skip the first two lines
			if row == [] or row[0] == 'Time':
				continue

			# Skip the fake ids
			current_id = int(row[1])
			if current_id < 0:
				continue

			# Extract intervals
			if row[2] == ' RMRIG' or row[2] == ' RMLEF' or row[2] == ' RMORE' or row[2] == ' RDONE':

				if len(times) > 0 and last_id == current_id:
					interv = CalLength(times[-1], row[0])
					intervals.append(interv)
				times.append(row[0])
				last_id = current_id
	
	# print(len(intervals))
	return intervals


# Generate test data in json format
def Ges_interval():
	address = 'Video Observations.csv'
	dataPath = 'sessions'
	res1 = []
	res2 = []
	res3 = []

	with open(address) as fin:
		reader = csv.reader(fin, dialect='excel')

		# Find the training data file name 
		# according to video observation file
		for row in reader:
			fileName = row[0]
			if fileName == 'Video File' or fileName == '':
				continue

			if row[-2] == 'IP' or row[-2] == 'P':

				# Find the exact log file according to the name
				folderName = fileName[10:20]
				address2 = dataPath + '/'+folderName

				# Extract features for training data file
				for fileName2 in os.listdir(address2):
					time1 = fileName[-12:-4]
					time2 = fileName2[-12:-4]
					if time1 == time2:
						filePath = address2 + '/' + fileName2
						res1 += CalIntervals1(filePath)
						res2 += CalIntervals2(filePath)
						res3 += CalIntervals3(filePath)
						break

	# OutPut('int_session_all_intervals.csv', res1)
	# OutPut('int_session_same_player_intervals.csv', res2)
	# OutPut('int_session_cons_sp_intervals.csv', res3)

	OutPut('play_session_all_intervals.csv', res1)
	OutPut('play_session_same_player_intervals.csv', res2)
	OutPut('play_session_cons_sp_intervals.csv', res3)


if __name__ == '__main__':
	Ges_interval()
	# address = 'sessions/2015-06-19/screen-2015-06-19--18-15-14.csv'
	# OutPut('test3.csv', CalIntervals3(address))
	print('Yes Done!')