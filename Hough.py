import math
import numpy as np 
import matplotlib.pyplot as plt 
import time
import csv

""""
# np.pi works, math.cos, math.sin

start = time.time()
degrees = np.arange(0,180)

positions = [[-71, 12], [10, -2],
[10, -2] ,[7, -1],
[7, -1] ,[23, -4],
[23, -4] ,[23, -3],
[23, -3] ,[0, 0]]"
# positions = [(182, 236), (170, 227), (179, 192), (160, 178), (168, 169), (135, 142)] # not straigth line
#positions = [(446, 196), (454, 194), (477, 191), (500, 187), (507, 186), (517, 184), (524, 183)] # license plate
#positions = [(170, 227), (182, 236), (160, 178), (135, 142), (327, 109)] # not straight line
#positions = [(447, 198), (500, 187), (509, 187), (517, 184)] # license plate
positions = [(500, 187), (446, 196), (447, 198), (24,72),(1,1),(454, 194), (477, 191), (507, 186), (517, 184), (524, 183), (479, 95)] # license plate with noise
#positions = [(517, 184), (446, 196), (447, 198), (454, 194), (500, 187), (507, 186), (524, 183)] # license plate 
#positions = [(464, 96), (362, 106), (327, 109), (541, 78),(517, 184), (446, 196), (447, 198), (454, 194), (500, 187), (507, 186), (524, 183)] # not license plate but creates straight line
"""
positions = [(227, 397), (202, 332), (235, 296), (230, 282), (460, 330), (468, 328), (480, 322), (488, 320),
 (499, 315), (505, 312), (511, 309), (516, 307), (232, 279), (227, 276), (220, 294), (205, 277), 
 (227, 266), (25, 210), (12, 206), (96, 211), (252, 221), (27, 166), (17, 166), (5, 149), (37, 144),
  (441, 138), (436, 138), (430, 137), (419, 122), (371, 121), (435, 120), (389, 119), (385, 119), (441, 118), 
  (446, 115), (459, 114), (453, 114), (466, 112), (92, 112), (493, 110), (422, 108), (156, 159), (127, 125), (441, 106), 
  (336, 127), (579, 104), (589, 103), (376, 99), (652, 97), (657, 127), (654, 116), (664, 96), (680, 131), (668, 128), 
  (682, 126), (667, 104), (619, 96), (357, 94), (693, 123), (720, 117), (734, 114), (719, 96), (696, 96), (735, 94), (84, 91),
   (368, 89), (378, 88), (435, 85), (516, 84), (441, 84), (423, 84), (447, 83), (459, 81), (466, 80), (472, 79), (479, 78), (218, 78), 
   (486, 77), (493, 76), (453, 76), (500, 75), (508, 73), (51, 71), (517, 70), (746, 68), (27, 68), (731, 67), (579, 64), (588, 62), (598, 61), 
   (260, 61), (292, 60), (50, 55), (718, 53), (677, 53), (236, 53), (77, 51),
 (46, 47), (32, 47), (240, 45), (230, 42), (194, 42), (412, 40), (692, 55), (657, 32), (400, 29), (699, 28), (692, 26),
  (669, 23), (243, 23), (300, 19), (678, 17), (291, 16), (310, 13), (664, 10), (179, 9), (87, 3), (96, 34), (705, 2), (399, 0), (261, 0), (268, 0)] # license plate with noise


def findStraightLine(positions,max_distance ,stepOfAngle = 2, printit = False):
	### to store theata-distance of a line from the (0,0) point
	## dimensions are number of angle and max distance from the origin


	degrees = np.arange(0,180,stepOfAngle)
	data = np.zeros((len(degrees),int(max_distance/5)+1)) # create 2 dimension array that corresponds each angle and distance, we will store the number of matching 
	negativeData = np.zeros((len(degrees),int(max_distance/5)+1))

	# finds the corresponding distance for each position and angle 
	# increments the value in data or negative data
	# crates 
	for angle in degrees[:]:
		i = 0
		for pos in positions:
			rad = math.radians(angle)
			### working on polar coordinate system 
			a = pos[0]*math.cos(rad) + pos[1]*math.sin(rad)
			if a < 0 :
				negativeData[int(angle/stepOfAngle)][round(a/5)] += 1 
			else:	
				data[int(angle/stepOfAngle)][round(a/5)] += 1 			
			i += 1


	## this loop finds the intersection of lines in the half space 
	## matches stores angle-distance values that more than four lines intersect in half space
	angledist = len(data)
	dstdist = len(data[0])
	matches = []
	for angle in range(angledist):	
		for dst in range(dstdist):
			if data[angle][dst] > 4:
				matches.append([angle*stepOfAngle,dst*5])
			if 	negativeData[angle][dst] > 4:
				matches.append([angle*stepOfAngle,-1*(dst*5)])		

	## we have already found the angle-distance value of straight lines
	## find the points that are on the lines
	matchedCont = []  ## stores points on the line 
	for match in matches[:]:
		matchedLoc = []
		for pos in positions:
			rad = math.radians(match[0])
			a = (pos[0]*math.cos(rad) + pos[1]*math.sin(rad))
			if abs(a-match[1]) < 3:
				matchedLoc.append(pos)
		matchedCont.append(matchedLoc)	


	if printit == True:
		with open("houghResults.csv", mode='w', newline='') as file:
			csvWriter = csv.writer(file, delimiter=',')
			for angle in data:
				csvWriter.writerow(angle)
	return matchedCont

def main():
	return_value = findStraightLine(positions, 1000)
	print(return_value)
if __name__== "__main__":
  	main()
