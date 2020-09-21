import cv2 
import numpy as np 
import detectChars2 as detectChars
import time
import os 
import pytesseract
import csv

GAUSSIAN_SMOOTH_FILTER_SIZE = (5,5)
ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9



def main(imgName, numberOfCar):
	
	img = cv2.imread(imgName)
	realImage = img.copy()
	showSteps = True

	startx = time.time()

	imageScaled = False
	scale_percent = 100

	scale_img = True

	holaa = 60
	widthke = int(img.shape[1] * holaa / 100)
	heightke = int(img.shape[0] * holaa / 100)
	dimek = (widthke, heightke)
	scaled = cv2.resize(img, dimek, interpolation = cv2.INTER_AREA)


	print(img.shape)
	if (img.shape[1]> 900 or img.shape[0] > 1300) and scale_img == True:
		if img.shape[1]> 720:
			scale_percent = int((900/ img.shape[1])*100)# percent of original size
		else: 
			scale_percent = int((1300/ img.shape[0])*100)
				
		width = int(img.shape[1] * scale_percent / 100)
		height = int(img.shape[0] * scale_percent / 100)
		dim = (width, height)
		img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
		imageScaled = True
	imgCopy = img

	


	# preprocess
	#bilateralimg = cv2.bilateralFilter(img,9,5,5)
	#blurred = cv2.GaussianBlur(img, GAUSSIAN_SMOOTH_FILTER_SIZE, 0)
	gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	result = cv2.adaptiveThreshold(gray, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, ADAPTIVE_THRESH_BLOCK_SIZE, ADAPTIVE_THRESH_WEIGHT)



	# find contours
	contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	#contours, hierarchy = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	
	if showSteps == True:
		detectChars.drawPureCont(contours,img,"_all_contours")################################# 
	counter = 0


	## eliminate the contour if its width greater than the height 
	## 
	remainContours = []   #list of possible char 

	for contour in contours:
		if cv2.contourArea(contour) > 10 :#and cv2.contourArea(contour) < 400:
			x, y, w, h = cv2.boundingRect(contour)
			if h > w and h<5*w:
				remainContours.append(contour)
		else:
			continue

	if showSteps == True:
		detectChars.drawPureCont(contours,img,"_after_elimi")

	remainContours1 = remainContours


	################ convert contours into class 
	contoursAsClass = detectChars.cont2Class(remainContours)

	## find the possible chars by comparing the contours 
	################################################################################
	if showSteps == True:
		detectChars.drawPureCont(remainContours,img,"beforFindPossible")

	possibstart = time.time()
	remainContoursClass = detectChars.findPossibleChar(contoursAsClass)
	possibstop = time.time()
	print(" possib takes", possibstop - possibstart)
	

	###############################################################################
	if showSteps == True:
		detectChars.drawPureCont(contoursAsClass,img,1, True, isClass =True)


	######### draw contours ########
	w, h, _ = img.shape
	if showSteps == True:
		
		black_image = np.zeros((w,h,3), np.uint8)
		black_image_0 = np.zeros((w,h,3), np.uint8)
		cv2.drawContours(black_image, remainContours1, -1, (0,255,0), 1)
		cv2.drawContours(black_image_0, contours, -1, (0,255,0), 1)
		cv2.imshow("resultee", black_image)
		cv2.imshow("first", black_image_0)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	black_image_2 = np.zeros((w,h,3), np.uint8)

	##remove the inner contours
	contoursAsClass = detectChars.removeInnerCont(remainContoursClass)



	houghstart = time.time()
	houghMatchedContPos = detectChars.houghAlgor(contoursAsClass, black_image_2)#,detectChars.drawPureCont(remainContours,img,1))
	houghstop = time.time()
	print("hough takes", houghstop-houghstart)

	savePath = "E:\\licensePlate\\results\\car{}".format(numberOfCar)
	#savePath = "results\\{}".format(imgName[:-4])
	try:
		os.mkdir(savePath)
	except OSError:
		pass
		
	#cv2.imwrite(savePath+"/{}_0.jpg".format(savePath[-5:]),img)
	listOfPossibleLicensePlates = detectChars.findMatchedCont(contoursAsClass,houghMatchedContPos,black_image_2, savePath, saveImg = False,showSteps = True)  # returns list of possible plate as class contour
	print("--------",len(listOfPossibleLicensePlates))
	#####print(len(listOfPossibleLicensePlates))
	resultPlates = detectChars.extractLicensePLates(listOfPossibleLicensePlates, img, realImage,scale_percent, imageScaled,numberOfCar, showSteps = False)
	stopx = time.time()
	
	print("whole", stopx-startx)
	startTess = time.time()
	showPlates = True
	savePlates = False
	extractChars = False

	lastPlatesString = ""
	lastPlatesList = []
	if extractChars == True:
		counter = 0
		pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
		for plate in resultPlates:
			if showPlates == True:
				cv2.imshow("result Plate {}".format(counter), plate)
			plate = cv2.GaussianBlur(plate, (5,5), 0)	
			text = pytesseract.image_to_string(plate)
			lastPlatesList.append(text)
			lastPlatesString += "," + text
			print("plate {} is".format(counter), text)
			counter += 1
		if showPlates == True:
			cv2.imshow("main img", scaled)
			stopTess = time.time()
			print("tesseract takes", stopTess - startTess)	
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	if savePlates == True:
		counter = 0
		pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
		for plate in resultPlates:
			text = pytesseract.image_to_string(plate)
			cv2.imwrite(savePath+"\\car{}_{}Plate.jpg".format(numberOfCar, counter), plate)
			cv2.imwrite(savePath+"\\car{}.jpg".format(numberOfCar), realImage)
			lastPlatesString += "," + text
			print("plate {} is".format(counter), text)
			counter += 1

	######print("Whole process takes",(stopx-startx), "seconds.")
	return manipulationOnResult(lastPlatesList)

def manipulationOnResult(lic_plates):
	all_chars = ["A", "B", "C", "C", "D", "E", "F", "G","H" ,"J", "I", "K", "L", "M", 
				"N", "O", "P", "R", "S", "T", "U" , "V", "Y", "Z", " "]
	all_int = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]			
	result = []
	for plate in lic_plates:
		newP = ""
		if len(plate) > 2:
			for ele in plate:
				if ele in all_chars or ele in all_int:
					newP += ele
				else:
					pass
		if len(newP) > 0:
			result.append(newP)
	lastres = []
	for plate in result:
		first , mid, last = "", "", ""
		firstcnd , midcnd, lastcnd = False, False, False
		if plate.count(' ') > 0:
			sprt_plate = plate.split(' ')

			for y in sprt_plate:
				if len(y) > 0 and firstcnd == False :
					cnt = 0
					for x in y:
						if x in all_int:
							cnt +=1
					if cnt == len(y):
						first = y
						firstcnd = True	
				if len(y) > 0 and midcnd == False:
					cnt = 0
					for x in y:
						if x in all_chars:
							cnt +=1
					if cnt == len(y):
						mid = y
						midcnd = True
						firstcnd = True
				if len(y) > 0 and lastcnd == False and (firstcnd == True and midcnd == True):
					cnt = 0
					for x in y:
						if x in all_int:
							cnt +=1
					if cnt == len(y):
						last = y
						lastcnd = True		
			#print("first" , first,"--mid",  mid, "--last", last)
			lastres.append([first, mid, last])	
			#print(sprt_plate)
				
	#print(result)
	return lastres
if __name__ == "__main__":
	imgs = os.listdir("photos1\\")
	for img in imgs[:4]:
		img = "photos1\\"+img
		
		plates = main(img, 0)
		

