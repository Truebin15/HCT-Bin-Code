import os
import csv


# Output csv file
def OutPut(name, res):
	with open(name, 'w', newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['filename', 'grams'])

		for i, ele in enumerate(res):
				writer.writerow([i, ele])


# Extract Ngrams from sequence
def Ngram(seq, nsize):
	res = []
	length = len(seq) - nsize + 1

	for i in range(length):
		res.append(seq[i:i+nsize])

	return res


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
			res_seg = ''

			for row in reader:

				# Skip the first two lines
				if row == [] or row[0] == 'Time':
					continue

				# Get the session start time
				if flag == -1:
					startTime = row[0]
					flag = 0
				
				# Extract intervals
				if row[2] == ' RMRIG':
					time = CalLength(startTime, row[0])
					in_seg = CompareSeg(time, seg)
					
					# If this gesture is in time the segments
					# add this gesture to the results
					if in_seg == 0:
						res_seg += 'R'
					elif in_seg == 1:
						break

				elif row[2] == ' RMLEF':
					time = CalLength(startTime, row[0])
					in_seg = CompareSeg(time, seg)
					
					# If this gesture is in time the segments
					# add this gesture to the results
					if in_seg == 0:
						res_seg += 'L'
					elif in_seg == 1:
						break

				elif row[2] == ' RMORE':
					time = CalLength(startTime, row[0])
					in_seg = CompareSeg(time, seg)
					
					# If this gesture is in time the segments
					# add this gesture to the results
					if in_seg == 0:
						res_seg += 'U'
					elif in_seg == 1:
						break

				elif row[2] == ' RDONE':
					time = CalLength(startTime, row[0])
					in_seg = CompareSeg(time, seg)
					
					# If this gesture is in time the segments
					# add this gesture to the results
					if in_seg == 0:
						res_seg += 'D'
					elif in_seg == 1:
						break

			res.append(res_seg)

	return res


# Generate test data in json format
def NgramExtract(nsize):
	address = 'Video Observations.csv'
	dataPath = 'sessions'
	res1 = []
	res2 = []
	total_p = 0
	total_i = 0

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

			total_p += len(time_seg1)
			total_i += len(time_seg2)

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

					for ges in ges1:
						res1 += Ngram(ges, nsize)

					for ges in ges2:
						res2 += Ngram(ges, nsize)
					
					break

	# print('the number of play segments: ',total_p)
	# print('the number of interact segments: ', total_i)
	OutPut('seg_'+str(nsize)+'_gram_play.csv', res1)
	OutPut('seg_'+str(nsize)+'_gram_int.csv', res2)


if __name__ == '__main__':
	start = 1
	end = 2

	for i in range(start, end):
		NgramExtract(i)

	print('Done!')
