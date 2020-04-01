import math
import numpy as np 
import matplotlib.pyplot as plt 
import time
import csv



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
