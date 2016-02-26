import csv


def VideoTuples():
	address = 'Video Observations.csv'

	with open('video_tuples.csv','w',newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['filename','tuple_number'])
		
		with open(address) as fin:
			reader = csv.reader(fin, dialect='excel')

			for row in reader:
				fileName = row[0]
				if fileName == 'Video File' or fileName == '':
					continue

				code = row[-1]
				# print(code)
				number = code.count('P') + code.count('I')
				writer.writerow([fileName, number])


# count the length of each segment
def CalLength(segment):
	# print(segment)

	m_index = segment.find('-')
	start = segment[2:m_index]
	end = segment[m_index+1:-1]

	s_index = start.find(':')
	e_index = end.find(':')

	minutes = int(end[0:e_index]) - int(start[0:s_index])
	seconds = int(end[e_index+1:]) - int(start[s_index+1:])

	res = minutes * 60 + seconds
	if res < 0:
		res = 0

	return res


def SegLength():
	address = 'Video Observations.csv'

	with open('play_segment_length.csv', 'w', newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['seg_id', 'filename', 'segment', 'seg_length'])
		
		with open(address) as fin:
			reader = csv.reader(fin, dialect='excel')
			seg_id = 0

			for row in reader:
				fileName = row[0]
				if fileName == 'Video File' or fileName == '':
					continue

				# extract the segments from string
				code = row[-1]
				number = code.count('P')
				flag = 0
				start = 0

				# print(fileName)
				while (flag < number):
					index = code.find('P', start)
					seg_id += 1
					seg_end = code.find(']', index)
					segment = code[index:seg_end+1]
					seg_length = CalLength(segment)
					writer.writerow([seg_id, fileName, segment, seg_length])
					flag += 1
					start = seg_end + 1


def CompComments():
	address = 'Video Observations.csv'

	with open('ChrisCode.csv','w',newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['seg_id','filename','segment'])
		
		with open(address) as fin:
			reader = csv.reader(fin, dialect='excel')
			seg_id = 0

			for row in reader:
				fileName = row[0]
				if fileName == 'Video File' or fileName == '':
					continue

				# extract the segments from string
				code = row[-4]
				number = code.count('P') + code.count('I')
				flag = 0
				start = 0

				# print(fileName)
				while (flag < number):
					index1 = code.find('P', start)
					index2 = code.find('I', start)

					# print(index)
					seg_id += 1
					index = min(index1, index2)
					if index == -1:
						index = max(index1, index2)

					seg_end = code.find(']', start)
					segment = code[index:seg_end+1]
					# seg_length = CalLength(segment)
					# print(segment)
					writer.writerow([seg_id, fileName, segment])
					flag += 1
					start = seg_end + 1


if __name__ == '__main__':
	# VideoTuples()
	SegLength()
	# CompComments()
	print('Done!')