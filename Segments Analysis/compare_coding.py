import csv

def SegExtract(code):
	number = code.count('P') + code.count('I')
	flag = 0
	start = 0
	end = -1
	segments = []

	while (flag < number):
		index1 = code.find('P', start, end)
		index2 = code.find('I', start, end)

		index = min(index1, index2)
		if index == -1:
			index = max(index1, index2)

		segment = code[index:index+12]
		segments.append(segment)
		flag += 1
		start = index + 11

	return segments


def CompareTable():
	address = 'Video Observations.csv'

	with open('CompareCode.csv', 'w', newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['seg_id', 'filename', 'segment'])
		
		with open(address) as fin:
			reader = csv.reader(fin, dialect='excel')

			for row in reader:
				fileName = row[0]
				if fileName == 'Video File' or fileName == '':
					continue

				# extract the segments from string
				code_bin = row[-1]
				code_chris = row[-4]
				segments_bin = SegExtract(code_bin)
				segments_chris = SegExtract(code_chris)

				# align segments


def CalLength(segment):
	print(segment)

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


def CalOverlap(seg1, seg2):
	s1_index = seg1.find('-')
	s2_index = seg2.find('-')

	start = max(seg1[2:s1_index], seg2[2:s2_index])
	end = min(seg1[s1_index+1:-1], seg2[s2_index+1:-1])
	res = seg1[0] + '[' + start + '-' + end + ']'

	return res


def CalMiss(seg1, seg2):
	s1_index = seg1.find('-')
	s2_index = seg2.find('-')

	start1 = seg1[2:s1_index]
	start2 = seg2[2:s2_index]
	end1 = seg1[s1_index+1:-1]
	end2 = seg2[s2_index+1:-1]

	if start1 <= start2 and end1 >= end2:
		miss = 0
	elif start1 <= start2 and end1 < end2:
		temp = 'P['+ end1 + '-' + end2 + ']'
		miss = CalLength(temp)
	elif start1 > start2 and end1 <= end2:
		temp1 = 'P[' + start2 + '-' + start1 + ']'
		temp2 = 'P[' + end1 + '-' + end2 + ']'
		miss = CalLength(temp1) + CalLength(temp2)
	else:
		temp = 'P[' + start2 + '-' + start1 + ']'
		miss = CalLength(temp)

	return miss

def CalExtra(seg1, seg2):
	s1_index = seg1.find('-')
	s2_index = seg2.find('-')

	start1 = seg1[2:s1_index]
	start2 = seg2[2:s2_index]
	end1 = seg1[s1_index+1:-1]
	end2 = seg2[s2_index+1:-1]

	if start1 <= start2 and end1 >= end2:
		temp1 = 'P[' + start1 + '-' + start2 + ']'
		temp2 = 'P[' + end2 + '-' + end1 + ']'
		extra = CalLength(temp1) + CalLength(temp2)
	elif start1 <= start2 and end1 < end2:
		temp = 'P[' + start1 + '-' + start2 + ']'
		extra = CalLength(temp)
	elif start1 > start2 and end1 <= end2:
		extra = 0
	else:
		temp = 'P[' + end2 + '-' + end1 + ']'
		extra = CalLength(temp)

	return extra


def FillTable():
	address = 'comparison.csv'

	with open('CompareRes.csv','w',newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['filename','seg_Bin','seg_Chris','start','end',
						'coded_secs','agree_coded','miss_p','miss_i','extra_p',
						'extra_i','uncoded_secs','agree_un'])
		
		with open(address) as fin:
			reader = csv.reader(fin, dialect='excel')

			for row in reader:
				fileName = row[0]
				if fileName == 'filename':
					continue

				if row[1] == '':
					writer.writerow(row)
					continue

				seg_bin = row[1]
				seg_chris = row[2]

				print('bin:',seg_bin)
				print('chris',seg_chris)

				# Label is different
				if seg_chris == '' or seg_bin[0] != seg_chris[0]:

					if seg_bin[0] == 'P':
						coded_secs = CalLength(seg_bin)
						agree_coded = 0
						miss_p = 0
						extra_p = coded_secs
						uncoded_secs = ''
						agree_un = ''
						
						if seg_chris == '' or seg_chris[0] == 'U':
							miss_i = 0
							extra_i = 0
						elif seg_chris[0] == 'I':
							miss_i = CalLength(seg_chris)
							extra_i = 0
						

					elif seg_bin[0] == 'I':
						coded_secs = CalLength(seg_bin)
						agree_coded = 0
						miss_i = 0
						extra_i = coded_secs
						uncoded_secs = ''
						agree_un = ''

						if seg_chris == '' or seg_chris[0] == 'U':
							miss_p = 0
							extra_p = 0
						elif seg_chris[0] == 'P':
							miss_p = CalLength(seg_chris)
							extra_p = 0

					else:
						uncoded_secs = CalLength(seg_bin)
						agree_un = 0
						coded_secs = ''
						agree_coded = ''
						miss_i = ''
						miss_p = ''
						extra_i = ''
						extra_p = ''
				
				# Label is the same
				elif seg_bin[0] == seg_chris[0]:

					if seg_bin[0] == 'P':
						coded_secs = CalLength(seg_bin)
						overlap_seg = CalOverlap(seg_bin, seg_chris)
						agree_coded = CalLength(overlap_seg)
						miss_p = CalMiss(seg_bin, seg_chris)
						extra_p = CalExtra(seg_bin, seg_chris)
						miss_i = 0
						extra_i = 0
						uncoded_secs = ''
						agree_un = ''

					elif seg_bin[0] == 'I':
						coded_secs = CalLength(seg_bin)
						overlap_seg = CalOverlap(seg_bin, seg_chris)
						agree_coded = CalLength(overlap_seg)
						miss_p = 0
						extra_p = 0
						miss_i = CalMiss(seg_bin, seg_chris)
						extra_i = CalExtra(seg_bin, seg_chris)
						uncoded_secs = ''
						agree_un = ''

					else:
						uncoded_secs = CalLength(seg_bin)
						overlap_seg = CalOverlap(seg_bin, seg_chris)
						agree_un = CalLength(overlap_seg)
						coded_secs = ''
						agree_coded = ''
						miss_i = ''
						miss_p = ''
						extra_i = ''
						extra_p = ''

				writer.writerow([fileName,seg_bin,seg_chris,row[3],row[4],
				coded_secs,agree_coded,miss_p,miss_i,extra_p,
				extra_i,uncoded_secs,agree_un])


if __name__ == '__main__':
	# CompareTable()
	FillTable()
	print('Done!')