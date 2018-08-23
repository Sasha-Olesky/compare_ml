import numpy as np
import cv2

def average2D(table2D):
	n = 0
	s = 0
	for i in table2D:
		s += len(i)
		for j in i:
			n += j
	return (n*1.0/s)

def hashTable(table2D, averageHash):
	for i in range(0, len(table2D)):
		for j in range(0, len(table2D[i])):
			if (table2D[i][j] > averageHash):
				table2D[i][j] = '1'
			else:
				table2D[i][j] = '0'
	return (table2D)

def concatenation(table2D):
	table2D = [ y for x in table2D for y in x]
	table2D = ''.join(str(int(i)) for i in table2D)
	table2D = int(table2D, 2)
	table2D = hex(table2D)
	return table2D[2:-1]

def hash_match(hash1, hash2):
	if hash1 == '':
		hash1 = '0'
	if hash2 == '':
		hash2 = '0'
	hex1 = int(hash1, 16)
	hex2 = int(hash2, 16)

	size = len(hash2) if hash1 <= hash2 else len(hash1)
	size *= 4
	similitude = (hex1 ^ hex2)
	similitude = bin(similitude)[2:]
	similitude = similitude.count('0') + size-len(similitude)
	percentage = similitude*100.0/size
	return percentage

def get_hash(img):
	# Resize them to 8x8
	imgresize = cv2.resize(img, (8, 8))
	imgresize = cv2.cvtColor(imgresize, cv2.COLOR_BGR2GRAY)
	imgdct = cv2.dct(np.float32(imgresize) / 255.0)

	# Calculate average DCT
	imgavdct = average2D(imgdct)

	# Hash the DCT
	imgdcthash = hashTable(imgdct, imgavdct)

	# Generage the hash Value
	imgvalue = concatenation(imgdcthash)

	return imgvalue

def compare_hash(hash1, hash2):
	match1 = hash_match(hash1, hash2)
	match2 = hash_match(hash1, hash2)
	if match1 > 50 and match2 > 50:
		return 'Same Image'
	else:
		return 'Different Image'

def hash_calc(img1, img2):
	# Resize them to 8x8
	img1resize = cv2.resize(img1, (8, 8))
	img2resize = cv2.resize(img2, (8, 8))

	# Change color to black and white
	img1resize = cv2.cvtColor(img1resize, cv2.COLOR_BGR2GRAY)
	img2resize = cv2.cvtColor(img2resize, cv2.COLOR_BGR2GRAY)

	# Calculate the DCT
	img1dct = cv2.dct(np.float32(img1resize) / 255.0)
	img2dct = cv2.dct(np.float32(img2resize) / 255.0)

	# Calculate average DCT
	img1avdct = average2D(img1dct)
	img2avdct = average2D(img1dct)

	# Hash the DCT
	img1dcthash = hashTable(img1dct, img1avdct)
	img2dcthash = hashTable(img2dct, img2avdct)

	# Generage the hash Value
	img1value = concatenation(img1dcthash)
	img2value = concatenation(img2dcthash)

	# Calculate the match between the two hash (in % )
	matching = hash_match(img1value, img2value)

	return matching


def hash_compare(img1, img2):
	match1 = hash_calc(img1, img2)
	match2 = hash_calc(img2, img1)
	matching_val = (match1+match2)/2
	if match1 > 50 and match2 > 50:
		return ('Same Image', matching_val)
	else:
		return ('Different Image', matching_val)