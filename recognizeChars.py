import numpy as np 
import cv2 



# function can work parallel and be callable by other program
# input is flattaned image , it is easy to carry and gather the characters on a file instead of image


def recognize(flattanedChar):
    npaClassifications = np.loadtxt("classifications.txt", np.float32)                  # read in training classifications

    npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)                 # read in training images


    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))       # reshape numpy array to 1d, necessary to pass to call to train

    kNearest = cv2.ml.KNearest_create()                   # instantiate KNN object

    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

    strFinalString = ""
    #for flattanedChar in flattanedChars:
    flattanedChar = np.float32(flattanedChar)       # convert from 1d numpy array of ints to 1d numpy array of floats
    retval, npaResults, neigh_resp, dists = kNearest.findNearest(flattanedChar, k = 1)     # call KNN function find_nearest
    strCurrentChar = str(chr(int(npaResults[0][0])))  
    strFinalString = strFinalString + strCurrentChar 
    print(strCurrentChar)
