import cv2
import numpy as np 
import math 



class PossibleChar:

	def __init__(self, _contour):
		self.contour = _contour

		self.boundingRect = cv2.boundingRect(self.contour)

		[intX, intY, intW, intH] = self.boundingRect
		self.positionint = [self.boundingRect[0],self.boundingRect[1]]
		self.intBoundingRectX = intX+intW/2
		self.intBoundingRectY = intY+intH/2
		self.intBoundingRectW = intW
		self.intBoundingRectH = intH
		self.position = self.boundingRect[:2]
		self.positionBottomRight = [self.position[0]+intW, self.position[1]+intH]
		self.bottomleft = [intX, intY+intH]
		self.bottomright = [intX+intW, intY+intH]
		self.righttop = [intX+intW, intY]
		self.widthHeightRate = intH
		self.intBoundingRectArea = self.intBoundingRectH * self.intBoundingRectW

		self.numberOfMatch = 0

		self.matchingChars = [self.contour]



	def addMatchingChar(self, contour):
		self.matchingChars.append(contour)






