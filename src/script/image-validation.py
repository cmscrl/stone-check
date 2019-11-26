# -*- coding: utf-8 -*-

import sys
import numpy as np
import os
from PIL import Image
import cv2
from matplotlib import pyplot as plt

def main():
    #Gray image load
    img = cv2.imread(sys.argv[1]) #circles.jpg #lim6.jpg
    imgOriginal = img.copy()

    # Check if image is loaded fine
    if img is None:
        print ('Error opening image')
        print ('Program Arguments: [image_name -- default lena.jpg]')
        exit()

    stoneEgdesCoordinates = edgesDetection(img)
    filtered_boxes = holesOnStone(img)
    img = cracksIdentification(imgOriginal, stoneEgdesCoordinates, img)

    cv2.imwrite(sys.argv[2], img)

def edgesDetection (image):

    imageCopy=image.copy()
    shifted = cv2.pyrMeanShiftFiltering(imageCopy,21,51)
    imgGray = cv2.cvtColor(shifted,cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgGray,75,255,cv2.THRESH_BINARY_INV)

    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2) #não sei se é necessário neste caso!!!!
    
    # sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=3)
   
    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)
    
    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0
    markers = cv2.watershed(imageCopy,markers)
    
    imageCopy[markers == -1] = [255,0,0]

    # Convert BGR to HSV
    imageHSV = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(imageHSV, lower_blue, upper_blue)
    
    # Bitwise-AND mask and original image
    blueEgdes = cv2.bitwise_and(imageCopy,imageCopy, mask= mask)

    # Eliminate the edges arround image
    w, h, __ = blueEgdes.shape
    blueEgdes[0:w,0:1] = (0,0,0)
    blueEgdes[0:w,h-1:h] = (0,0,0)
    blueEgdes[0:1,0:h] = (0,0,0)
    blueEgdes[w-1:w,0:h] = (0,0,0)
    bluePixels = np.where((blueEgdes>lower_blue) | (blueEgdes<upper_blue))
    
    stoneEgdesCoordinates = []
    comparaArray = np.array([255,0,0])
    
    # To identify the edges of stone
    for x in range (w):
        for y in range (h):
            if(np.array_equal(blueEgdes[x,y] , comparaArray) 
            and x != 0 and y !=0 and x!=w-1 and y!=h-1) :  
                stoneEgdesCoordinates.append([x,y])
    
    # To color the edges of stone 
    for cnt in range (stoneEgdesCoordinates.__len__()):
        a,b = stoneEgdesCoordinates[cnt]
        image[a,b] = (255,0,0)
    
    #return a list with all coordinates of stone edges
    return stoneEgdesCoordinates

def holesOnStone(img):

    res,binary = cv2.threshold(img,150,255,cv2.THRESH_BINARY)
    binaryGray= cv2.cvtColor(binary,cv2.COLOR_RGB2BGR)
    edges = cv2.Canny(binaryGray,100,200)
    blur = cv2.GaussianBlur(edges,(5,5),0)

    _, _, boxes, _ = cv2.connectedComponentsWithStats(blur)
    
    # first box is the background
    boxes = boxes[1:]
    filtered_boxes = []
    #To identify the measures necessary to design the squares
    for x,y,w,h,pixels in boxes:
        if pixels < 10000 and h < 200 and w < 200 and h > 10 and w > 10:
            filtered_boxes.append((x,y,w,h))
    
    #To design the puple squares on original image
    for x,y,w,h in filtered_boxes:
        cv2.rectangle(img, (x,y), (x+w,y+h), (153,51,153),2)
    
    #return an array with the coordinates of boxes that contains the holes
    return filtered_boxes


def cracksIdentification (img, stoneEgdCoor, imgFinal):

    imgC = img.copy()
    shifted = cv2.pyrMeanShiftFiltering(imgC,10,20)
    grayImage = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgC,150,255,cv2.THRESH_BINARY)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)

    w,h=thresh.shape
    
    filtered_boxes = []
    cracks=[]
    
    for i in range (w):
        for j in range (h):
            if(np.any(thresh[i, j] != 0) and (np.any(thresh[i, j] != 255))
            and i != 0 and j !=0 and i!=w-1 and j!=h-1) :      
                    filtered_boxes.append([i,j]) 
    
 
    for i in range (filtered_boxes.__len__()):
        if not (filtered_boxes[i] in stoneEgdCoor): 
            cracks.append(filtered_boxes[i])
     
    for i in range (cracks.__len__()):
        w,h=cracks[i]
        imgFinal[w,h]=[0,0,255]

    return imgFinal

main()