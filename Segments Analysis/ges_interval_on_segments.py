import os
import csv


# Output csv file
def OutPut(name, res):
	with open(name, 'w', newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['id', 'intervals'])

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


# Extract segments from the codes
def GetSegs(code, category):
	number = code.count(category)
	flag = 0
	start = 0
	segments = []

	# print(fileName)
	while (flag < number):
		index = code.find(category, start)
		seg_end = code.find(']', index)
		segments.append(code[index:seg_end+1])
		flag += 1
		start = seg_end + 1

	return segments


# Judge if a time is in a period
def CompareSeg(time, segment):
	# print(time, segs)

	m_index = segment.find('-')
	start = segment[2:m_index]
	end = segment[m_index+1:-1]

	s_index = start.find(':')
	e_index = end.find(':')

	s = int(start[0:s_index]) * 60 + int(start[s_index+1:])
	e = int(end[0:e_index]) * 60 + int(end[e_index+1:])
	
	if time < s:
		res = -1
	elif time >= s and time <= e:
		res = 0
	elif time > e:
		res = 1

	# print(res)
	return res


# Extract gestures according to the time segments
def GetGestures(address, segs):
	flag = -1
	res = []
	# print(address, segs)
	# startTime = ''

	# When time segments are 0
	if len(segs) < 1:
		return res

	with open(address) as flog:
		reader = csv.reader(flog, dialect='excel')
		
		for seg in segs:
			res_seg = []

			for row in reader:

				# Skip the first two lines
				if row == [] or row[0] == 'Time':
					continue

				# Get the session start time
				if flag == -1:
					startTime = row[0]
					flag = 0
				
				# Extract intervals
				if row[2] == ' RMRIG' or row[2] == ' RMLEF' or row[2] == ' RMORE' or row[2] == ' RDONE':
					time = CalLength(startTime, row[0])
					in_seg = CompareSeg(time, seg)
					
					# If this gesture is in time the segment
					# add this gesture to the results
					if in_seg == 0:
						res_seg.append([row[0], row[1], row[2]])
						continue
					elif in_seg == 1:
						break

			res.append(res_seg)
				
	return res


# Calculate all intervals
def CalIntervals1(segs):
	times = []
	intervals = []
		
	for row in segs:

		# Skip the fake ids
		current_id = int(row[1])
		if current_id < 0:
			continue

		# Extract intervals
		if row[2] == ' RMRIG' or row[2] == ' RMLEF' or row[2] == ' RMORE' or row[2] == ' RDONE':
			if len(times) > 0:
				interv = CalLength(times[-1], row[0])
				# if interv == 0:
				# 	print(times[-1], row[0], row[2])
				# 	print(interv, fileName)
				intervals.append(interv)
			times.append(row[0])
	# print(segs)
	return intervals


# Calculate intervals of the same users
def CalIntervals2(segs):
	times = [[] for i in range(6)]
	intervals = []
		
	for row in segs:

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
def CalIntervals3(segs):
	times = []
	intervals = []
	last_id = 0
		
	for row in segs:

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
def GetInterval():
	address = 'Video Observations.csv'
	dataPath = 'sessions'
	res1 = []
	res2 = []
	res3 = []
	res4 = []
	res5 = []
	res6 = []

	with open(address) as fin:
		reader = csv.reader(fin, dialect='excel')

		# Find the training data file name 
		# according to video observation file
		for row in reader:
			fileName = row[0]
			if fileName == 'Video File' or fileName == '':
				continue

			# Find the exact log file according to the name
			folderName = fileName[10:20]
			address2 = dataPath + '/'+folderName

			# Parse the time segments
			time_seg1 = GetSegs(row[-1], 'P')
			time_seg2 = GetSegs(row[-1], 'I')

			# print(fileName, time_seg2)

			# Extract features for training data file
			for fileName2 in os.listdir(address2):
				time1 = fileName[-12:-4]
				time2 = fileName2[-12:-4]
				if time1 == time2:
					filePath = address2 + '/' + fileName2
					ges1 = GetGestures(filePath, time_seg1)
					ges2 = GetGestures(filePath, time_seg2)

					# print(ges2)
					
					for seg in ges1:
						res1 += CalIntervals1(seg)
						res2 += CalIntervals2(seg)
						res3 += CalIntervals3(seg)

					for seg in ges2:
						res4 += CalIntervals1(seg)
						res5 += CalIntervals2(seg)
						res6 += CalIntervals3(seg)

					break

	OutPut('play_all_intervals.csv', res1)
	OutPut('play_same_player_intervals.csv', res2)
	OutPut('play_cons_sp_intervals.csv', res3)
	OutPut('int_all_intervals.csv', res4)
	OutPut('int_same_player_intervals.csv', res5)
	OutPut('int_cons_sp_intervals.csv', res6)


if __name__ == '__main__':
	GetInterval()
	print('Done!')
