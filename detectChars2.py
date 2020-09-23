import cv2 
import numpy as np
import math
import aContour
import Hough
import random 
import time
import recognizeChars



CANBELICPLATE = 4

# finds the corresponding contour by using its coordinate
def findMatchedCont(listOfContours, MatchedPositions, img, path, saveImg= False,showSteps = False):
	counter = 1

	# we have the positions of matched contours not itself
	# get contours from their known positions
	listOfMatchedContours = []
	for positions in MatchedPositions:
		positions.sort(key = lambda x: x[0])
		newimg = img.copy()
		
		contours0 = []
		classList = []
		for pos in positions:
			for cont in listOfContours:
				if pos == cont.position:
					contours0.append(cont)
					classList.append(cont)
					if showSteps == True:
						cv2.drawContours(newimg, cont.contour, 0, (0,0,255), 1)
		#now mathced contours are stored in listOfMatchedContours

		# end of for

		contours = []
		if len(contours0) > 2:
			contours = matchContours(contours0)
		if len(contours) > 3 and (showSteps== True or saveImg == True):
			conditionForRectangle = canBeLicPlate(contours)
			print("conditionForRectangle", conditionForRectangle)
			if conditionForRectangle == True:
				####print("before inner and matching",len(contours0))
				#print("after inner", len(innerRemoved))

				######print("last contour drawn with green", len(contours))	
				if showSteps == True:
					for i in contours:
						cv2.drawContours(newimg, i.contour, 0, (0,255,0),1)
					cv2.imshow("result of hough and matching", newimg)
					cv2.waitKey(0)
					cv2.destroyAllWindows()	
					
				if saveImg == True :
					for i in contours:
						cv2.drawContours(newimg, i.contour, 0, (0,255,0),1)
					fileName = path + "/{}_{}.jpg".format(path[-5:],counter)
					counter += 1
					cv2.imwrite(fileName, newimg)

		if len(contours) >3 and canBeLicPlate(contours):
			listOfMatchedContours.append(removeRepeatingCont(contours))
	# listOfMatchedContours contains all possible license plates 
	# first loop over all possiblicplate and if all of chars of a lic plate are also contained by other possiblicplate delete it
	operatedLicPLates = []
	messMathced = []				
	for x in np.arange(0, len(listOfMatchedContours), 1):
		anEmpty = []
		if len(messMathced) > 0:
			for m in np.arange(0,len(messMathced),1):
				#print(len(listOfMatchedContours), len(messMathced), m, x)
				if similarOrSame(listOfMatchedContours[x], messMathced[m]) > 0:
					anEmpty = messMathced[m]
					del messMathced[m]
					break
				else:
					anEmpty.extend(listOfMatchedContours[x])
		if True:	
			similarities = 0			
			for y in np.arange(x, len(listOfMatchedContours), 1):
				#if x != y:
				similarities = similarOrSame(listOfMatchedContours[x], listOfMatchedContours[y])
				if similarities > 0:
					anEmpty.extend(listOfMatchedContours[y])
		messMathced.append(removeRepeatingCont(anEmpty))			

	counter = 1
	for plate in messMathced:	
		newimg = img.copy()
		if saveImg == True:
			for i in plate:
				cv2.drawContours(newimg, i.contour, 0, (0,255,0),1)
			fileName = path + "\\{}_{}.jpg".format(path[-5:],counter)
			counter += 1
			cv2.imwrite(fileName, newimg)					

	return messMathced


## we found the straight line and contours on it but we dont know how far they are each other 
## matchContours eliminates the lines which are not suitable for a license plate 
## start most left contour and compare them with left and right contours of it ,
def matchContours(classContours):
	newList = []
	distances = []
	for c in np.arange(len(classContours)):
		# take its length and distance to nearest contour and compare if satisfies add to new list
		if c == 0:
			curContPos, curContH = classContours[c].position, classContours[c].intBoundingRectH
			rightContPos, rightContH = classContours[c+1].position, classContours[c+1].intBoundingRectH
			
			if abs(curContH-rightContH) < curContH/5:
				distance  = distanceBetweenContour(curContPos, rightContPos)
				
				if distance < 2*curContH:
					newList.append(classContours[c])
					distances.append(distance)
		elif c == (len(classContours)-1):
			curContPos, curContH = classContours[c].position, classContours[c].intBoundingRectH
			leftContPos, leftContH = classContours[c-1].position, classContours[c-1].intBoundingRectH
			if abs(curContH-leftContH) < curContH/5:
				distance  = distanceBetweenContour(curContPos, leftContPos)
				
				if distance < 2*curContH:
					newList.append(classContours[c])
					distances.append(distance)
		else:
			curContPos, curContH = classContours[c].position, classContours[c].intBoundingRectH
			leftContPos, leftContH = classContours[c-1].position, classContours[c-1].intBoundingRectH
			rightContPos, rightContH = classContours[c+1].position, classContours[c+1].intBoundingRectH
			leftDistCond = distanceBetweenContour(curContPos, leftContPos) < 2*curContH
			rightDistCond = distanceBetweenContour(curContPos, rightContPos) < 2*curContH
			
			leftRatioCond = abs(curContH-leftContH) < curContH/5
			rightRatioCond = abs(curContH-rightContH) < curContH/5 
			#allCond = (leftRatioCond and leftDistCond) or (rightRatioCond and rightDistCond)
			rightCond = (rightRatioCond and rightDistCond)
			leftCond = (leftRatioCond and leftDistCond)
			if rightCond == True:
				if abs(curContH-leftContH) < curContH*0.8:
					newList.append(classContours[c])
					distances.append(distanceBetweenContour(curContPos, rightContPos))
			if leftCond == True:
				if abs(curContH-rightContH) < curContH*0.8:
					newList.append(classContours[c])
					distances.append(distanceBetweenContour(curContPos, leftContPos))
		if len(distances) < -1:
			avg = sum(distances) / len(distances)
			cond = 0
			for i in distances:
				if (i-avg) < avg/7.5:
					cond += 1
			if cond != len(distances):
				newList = []
	return newList			

def canBeLicPlate(contours):
	sumOfWidht = 0
	for i in contours:
		sumOfWidht += i.intBoundingRectW
	calculatedWidth = distanceBetweenContour(contours[0].position, contours[-1].righttop)
	if 	(sumOfWidht>calculatedWidth) or calculatedWidth-sumOfWidht < calculatedWidth/ CANBELICPLATE :
		return True
	else:
		return False	

def removeRepeatingCont(listOfCont):
	result = []
	for i in listOfCont:
		cond = False
		for x in result:
			if i.position == x.position:
				cond = True
		if cond == False:		
			result.append(i)			
	return result



def similarOrSame(licPlate, tempLicPlate):
	similarities = 0
	for cont in licPlate:
		for temp in tempLicPlate:
			if cont.position == temp.position:
				similarities += 1						
	return similarities 
def distanceBetweenContour(first, second):
    intX = abs(first[0] - second[0])
    intY = abs(first[1] - second[1])

    return math.sqrt((intX ** 2) + (intY ** 2))




def findPossibleChar(listOfContoursClass):
	centersOfContours = []
	result = []
		
	
	for contour in listOfContoursClass:
		curX = contour.intBoundingRectX
		curY = contour.intBoundingRectY
		curH = contour.intBoundingRectH
		curW = contour.intBoundingRectW
		condition = 0
		for control in listOfContoursClass:
			contX = control.intBoundingRectX
			contY = control.intBoundingRectY
			contH = control.intBoundingRectH
			heightRatio = abs(curH-contH)/curH
			if [curX,curY] != [contX,contY]:
				distance = distanceBetweenContour([curX,curY], [contX,contY])
				if distance < 3*curH and heightRatio < 0.4:
					condition += 1	
		if condition > 1:
			result.append(contour)		
	return result


def drawPureCont(contours, img, i, cond= False, isClass = False):
	w, h, _ = img.shape
	black_image = np.zeros((w,h,3), np.uint8)
	if isClass == False	:
		if cond == False:
			cv2.drawContours(black_image, contours, -1, (0,0,255), 1)
			cv2.imshow("contours{}".format(i), black_image)
		if cond == True:
			for i in np.arange(len(contours)):
				intRandomBlue = random.randint(0, 255)
				intRandomGreen = random.randint(0, 255)
				intRandomRed = random.randint(0, 255)	
				cv2.drawContours(black_image, contours, i, (intRandomBlue,intRandomGreen,intRandomRed), 1)
			cv2.imshow("contours{}".format(i), black_image)
	else:
		if cond == False:
			for cont in contours:
				cv2.drawContours(black_image, cont.contour, 0, (0,0,255), 1)
			cv2.imshow("contours{}".format(i), black_image)
		if cond == True:
			for cont in contours:
				intRandomBlue = random.randint(0, 255)
				intRandomGreen = random.randint(0, 255)
				intRandomRed = random.randint(0, 255)	
				cv2.drawContours(black_image, cont.contour , 0, (intRandomBlue,intRandomGreen,intRandomRed), 1)
			cv2.imshow("contours{}".format(i), black_image)			


	return black_image


def cont2Class(contours):
	listOfContoursClass= []
	for contour in contours:
		cont = aContour.PossibleChar(contour)
		cont.contour = [contour]
		listOfContoursClass.append(cont)
	return listOfContoursClass


""""def removeInnercontours(contours):
	result = []
	for contour in contours:
		contour1 = contour
		contour = aContour.PossibleChar(contour)
		contX, contY , contH, contW = contour.boundingRect #gives top left corner coordinate
		counter = 0
		allInner = []
		
		for inner in contours:
			inner1 = inner
			inner = aContour.PossibleChar(inner)
			innerX, innerY , innerH, innerW = inner.boundingRect
			if (inner != contour and (contH*contW)>(innerW*innerH)):
				

				if (inner.intBoundingRectX > contX and 
					inner.intBoundingRectX < contX+contW and 
					inner.intBoundingRectY > contY and 
					inner.intBoundingRectY < contY+contH):
					counter += 1
					allInner.append(inner1)
		if counter < 2:
			result.append(contour1)
	for cont in result:
		try: 
			if cont in allInner:
				result.remove(cont)
		except:
			continue		
	return result"""



# isRightRectangle returns true is given contours creates a right rectangle
# and widht of rectangle cannot be bigger than its length
def removeInnerCont(contoursClassList):
	resultList = list(contoursClassList)
	for curCont in contoursClassList:
		for tempCont in contoursClassList:
			if curCont.position != tempCont.position:	
				if curCont.position[0] > tempCont.position[0] and curCont.righttop[0] < tempCont.righttop[0]:
					if curCont.position[1] > tempCont.position[1] and curCont.bottomleft[1] < tempCont.bottomleft[1]:
						try:
								resultList.remove(curCont)
						except:
							pass
						###print("cont is removed")
	#resultList.sort(key = lambda x: x.position[0] )	
	return resultList

def houghAlgor(listOfContoursClass, img):	
	comp  = 0
	positions = []
	x = img.shape[0]
	y = img.shape[1]
	# lines will be represented by distance to origin and angle, need to know max distance from the origin
	max_distance = math.sqrt((x**2+y**2))

	for x in listOfContoursClass:
		positions.append(x.position)

		#matched = x.matchingChars
		#if len(matched) > 5:
		#	matchedClass = cont2Class(matched)
						
	result  = Hough.findStraightLine(positions, int(max_distance))

	return result



# we are going to get perspective of license plate
def extractLicensePLates(possiblePlates, img, realImage,scalepercent, imageScaled,numberOfCar,  showSteps = False):
	countPlate = 0
	angleImg = img.copy()
	if imageScaled == True:
		mlt = (100/scalepercent)	
	else:
		mlt = 1	
	count = 0

	####print plates contours postion 
	#### print characters position that you callculate
	### crop as a ractangle without any rotation 
	yanildim = realImage.copy()
	extend = 1.007
	narrow = 0.993
	resultPlates = []
	for plate in possiblePlates:
		plate = sorted(plate, key = lambda x: x.position[0])
		# put a circle on each corner of license plate 
		topLeft = 	(int(plate[0].position[0]*mlt*narrow),int(plate[0].position[1]*mlt*narrow))
		topRight =  (int(plate[-1].righttop[0]*mlt*extend),int(plate[-1].righttop[1]*mlt*narrow))
		bottomLeft = (int(plate[0].bottomleft[0]*mlt*narrow),int(plate[0].bottomleft[1]*mlt*extend))
		bottomRight = (int(plate[-1].bottomright[0]*mlt*extend), int(plate[-1].bottomright[1]*mlt*extend))
		center1 = (int(plate[0].intBoundingRectX*mlt), int(plate[0].intBoundingRectY*mlt))
		center2 = (int(plate[-1].intBoundingRectX*mlt), int(plate[-1].intBoundingRectY*mlt))
		#anglePlate = calculateAngle2(center1, center2)
		topPosY, bottomPosY = [topLeft[1], topRight[1]] ,[bottomRight[1], bottomLeft[1]]
		leftPosX, rightPosX = [topLeft[0], bottomLeft[0]], [topRight[0], bottomRight[0]]
		topPosY.sort()
		bottomPosY.sort()
		leftPosX.sort()
		rightPosX.sort()
		########### task starts crop the rectangle witout any rotation #################
		if topPosY[0]-10>0 and bottomPosY[-1]+10>0 and leftPosX[0]-10>0 and rightPosX[-1]+10>0:
			plateImage = realImage[topPosY[0]-10:bottomPosY[-1]+10, leftPosX[0]-10:rightPosX[-1]+10]
			topLeftPosition =  [leftPosX[0]-10, topPosY[0]-10]
		else:
			plateImage = realImage[topPosY[0]:bottomPosY[-1], leftPosX[0]:rightPosX[-1]]
			topLeftPosition =  [leftPosX[0], topPosY[0]]
		#cv2.imshow("plate img", plateImage)  ###shows cropped image any rotation 
		pts1 = np.float32([topLeft, topRight, bottomLeft, bottomRight])
		width = distanceBetweenContour(topLeft,topRight)
		height =distanceBetweenContour(topLeft, bottomLeft)
		pts2 = np.float32([[0,0], [width,0],[0,height], [width, height] ])
		M = cv2.getPerspectiveTransform(pts1,pts2)
		dst = cv2.warpPerspective(realImage,M,(int(width), int(height)))
		dstGray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)		
		dstThresh = cv2.adaptiveThreshold(dstGray, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,35,5)
		
		#cv2.imshow("plate image{}.jpg".format(count), dstThresh)
		resPlate , maxMatching= extractCharsFromPlate(dstThresh, showSteps)
		if maxMatching > 3:
			resultPlates.append(resPlate)
		count += 1
	#cv2.imwrite("denedimyanildim{}.jpg".format(numberOfCar), yanildim)  ## save the yanildim
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	return resultPlates




def extractCharsFromPlate(img, showSteps):
	extra = 20
	extra1 = extra//2
	white = np.ones((img.shape[0]+extra,img.shape[1]+extra), np.uint8)
	white.fill(255)
	white[extra1:img.shape[0]+extra1, extra1:img.shape[1]+extra1] = img
	
	contours, hierarchy = cv2.findContours(white, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	if showSteps == True:
		black = np.ones((img.shape[0]+extra,img.shape[1]+extra,3), np.uint8)
		cv2.imshow("white gib", white)
	#contours = cont2Class(contours)
	heights = []
	matchedCont = []
	maxMatch = 0
	maxEle = 0
	for cnt in contours[1:]:       # find the character in license plate 
		_,_,w,x = cv2.boundingRect(cnt)
		if x > img.shape[0]*0.3 and x >= w :  # height of character should be close
			cond = False   
			for h in np.arange(0, len(heights), 1):   # looping in heights and gather the similar ones
				if round(abs(x-heights[h][0])) <= round(x*0.1) or x == heights[h][0]:  # if conoturs height is matched with element of heights list 
					heights[h][1] += 1
					matchedCont[h].append(cnt)
					cond = True
					break
			if cond == False:
				heights.append([x,1])
				matchedCont.append([cnt])

		else:
			cv2.drawContours(white, [cnt], 0 ,(255,255,255), -1 )

	for i in range(0,len(heights),1):
		if heights[i][1] > maxMatch:
			maxEle = i
			maxMatch = heights[i][1]
	if len(matchedCont) > 0 and showSteps == True:				
		for cnt in matchedCont[maxEle]:
			cv2.drawContours(black, [cnt], 0, (255,0,0), 1)
			topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
			bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
			leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
			rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
			cv2.circle(black, topmost,2, (0,255,0), 2)
			cv2.circle(black, bottommost,2, (0,255,0), 2)
			cv2.circle(black, leftmost,2, (0,0,255), 1)
			cv2.circle(black, rightmost,2, (0,0,255), 1)
			cv2.imshow("aasfa", black)
			k = 0#cv2.waitKey()
			if k == ord('q'):
				cv2.destroyAllWindows()
				break	
	for x in range(0,len(heights), 1):
		if x == maxEle:
			pass
		else:
			for y in range(0,len(matchedCont[x]),1):
				cv2.drawContours(white, [matchedCont[x][y]], 0, (255,255,255), -1 )
			
	if showSteps == True:			
		cv2.imshow("öldaw", white)
		cv2.imshow("thresh plate", black)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
	return white , maxMatch	