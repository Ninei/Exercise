import os

import cv2
import copy
import numpy as np


class camera(object):
	def __init__(self):
		self.width   = 0
		self.height  = 0
		self.deviceN = 0
		self.magicN  = 0
		self.vid     = 0
		self.scale   = 0

class markerImage(object):
	def __init__(self):
		self.width   = 0
		self.height  = 0
		self.image   = 0
		self.pitchX  = 0
		self.pitchY  = 0
		self.filter  = 0
		self.scaleMin = 0
		self.scaleMax = 0
		self.scaleWarning = 0
		self.scaleRatio = 0

cam     = camera()
marker  = markerImage()
markerS = markerImage()
threshold = 0.8
debugShow = False

markerScale = 1.0
markerSearchDir = 1
status = 'OK'

#Method = cv2.TM_CCOEFF
Method = cv2.TM_CCOEFF_NORMED

#Method = cv2.TM_CCORR
#Method = cv2.TM_CCORR_NORMED

#Method = cv2.TM_SQDIFF
#Method = cv2.TM_SQDIFF_NORMED


#prepare the 5x5 shaped low pass filter
kernelLowPass = np.array([[1, 1, 1, 1, 1], 
						  [1, 1, 1, 1, 1], 
						  [1, 1, 1, 1, 1], 
						  [1, 1, 1, 1, 1], 
						  [1, 1, 1, 1, 1]])
kernelLowPass = kernelLowPass / np.sum(kernelLowPass)

#prepare the 3x3 / 5x5 shaped high pass filter
#kernelHighPass = np.array([[ 0.0, -1.0,  0.0], 
#						    [ -1.0,  5.0, -1.0],
#						    [  0.0, -1.0,  0.0]])

kernelHighPass = np.array([[ 0.0, -1.0, -3.0, -1.0,  0.0], 
						   [-1.0,  1.5,  2.5,  1.5, -1.0],
						   [-3.0,  2.5,  4.0,  2.5, -3.0],
						   [-1.0,  1.5,  2.5,  1.5, -1.0],
						   [ 0.0, -1.0, -3.0, -1.0,  0.0]])
kernelHighPass = kernelHighPass / (np.sum(kernelHighPass) if np.sum(kernelHighPass)!=0 else 1)


debugPlot = []

def initCamera(cameraDevice):
	global markerScale
	print('Setup camera ' , cameraDevice)
	match cameraDevice:
		case 'iPhone':
			cam.width  = 360
			cam.height = 480
			cam.magicN = 275
			#cam.magicN = 200
			cam.device =   0
			cam.scale  =   0.75
		case 'acttoS':
			cam.width  = 160
			cam.height = 120
			cam.magicN = 220
			cam.device =   1
			cam.scale  =   0.25
		case 'acttoM':
			cam.width  = 320
			cam.height = 240
			cam.magicN = 440
			cam.device =   1
			cam.scale  =   0.5
		case 'acttoL':
			cam.width  = 640
			cam.height = 480
			cam.magicN = 880
			cam.device =   1
			cam.scale  =   1.0
		case 'DELLS':
			cam.width  = 160
			cam.height = 120
			cam.magicN = 127
			cam.device =   0
			cam.scale  =   0.25
		case 'DELLM':
			cam.width  = 320
			cam.height = 240
			cam.magicN = 253
			cam.device =   0
			cam.scale  =   0.5
		case 'DELLL':
			cam.width  = 640
			cam.height = 480
			cam.magicN = 506
			cam.device =   0
			cam.scale  =   1.0
		case 'LogitecL':
			cam.width  = 640
			cam.height = 480
			cam.magicN = 506
			cam.device =   1
			cam.scale  =   1.0
		case _:
			# default
			cam.width  = 320
			cam.height = 240
			cam.magicN = 400
			cam.device =   0
			cam.scale  =   0.5
		
	# set the camera parameters
	print('Connect to camera')
	cam.vid = cv2.VideoCapture(cam.device)
	print('Set the camera resolution 1/2')
	cam.vid.set(cv2.CAP_PROP_FRAME_WIDTH,  cam.width)
	print('Set the camera resolution 2/2')
	cam.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, cam.height)
	# update the camera parameters with the actual settings
	print('Validate Camera settings')
	cam.width  = round(cam.vid.get(cv2.CAP_PROP_FRAME_WIDTH))   # float `width`
	cam.height = round(cam.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`
	markerScale = cam.scale

currentPath = os.getcwd() + "Intradox/";

def initMarker(beltType):
	# get the belt marker
	match beltType:
		case 'DARB_L':
			marker.image = cv2.imread(currentPath+'Marker_DARB_L.bmp')
			marker.pitchX = 50.8
			marker.pitchY = 50.6
			marker.filter = 'HIGH_PASS'
			marker.scaleMin = 0.20
			marker.scaleMax = 0.50
			marker.scaleWarning = 0.02
			marker.scaleRatio   = 1.08
		case 'DARB_R':
			marker.image = cv2.imread(currentPath+'Marker_DARB_R.bmp')
			marker.pitchX = 50.8
			marker.pitchY = 50.6
			marker.filter = 'HIGH_PASS'
			marker.scaleMin = 0.20
			marker.scaleMax = 0.50
			marker.scaleWarning = 0.02
			marker.scaleRatio   = 1.08
		case 'S400ARB':
			marker.image = cv2.imread(currentPath+'Marker_S400ARB45.bmp')
			marker.pitchX = 50.8
			marker.pitchY = 50.8
			marker.filter = 'NONE'
			marker.scaleMin = 0.20
			marker.scaleMax = 0.50
			marker.scaleWarning = 0.02
			marker.scaleRatio   = 1.15
		case 'S7000':
			marker.image = cv2.imread(currentPath+'Marker_S7000.bmp')
			marker.pitchX = 81.0
			marker.pitchY = 50.5
			marker.filter = 'HIGH_PASS'
			marker.scaleMin = 0.25
			marker.scaleMax = 0.50
			marker.scaleWarning = 0.02
			marker.scaleRatio   = 1.50
		case 'S7050':
			#marker.image = cv2.imread('Marker_S7050.bmp')
			marker.image = cv2.imread(currentPath+'Marker_S7050_test.bmp')
			marker.pitchX = 81.0
			marker.pitchY = 50.5
			marker.filter = 'HIGH_PASS'
			marker.scaleMin = 0.25
			marker.scaleMax = 0.50
			marker.scaleWarning = 0.02
			marker.scaleRatio   = 1.22
		case 'S800AIM':
			marker.image = cv2.imread(currentPath+'Marker_S800_AIM.bmp')
			marker.pitchX = 50.8
			marker.pitchY = 16.8095
			marker.filter = 'HIGH_PASS'
			marker.scaleMin = 0.30
			marker.scaleMax = 0.70
			marker.scaleWarning = 0.02
			marker.scaleRatio   = 1.06
		case 'S800AIM_Sorter':
			marker.image = cv2.imread(currentPath+'Marker_S800_AIM_Sorter.bmp')
			marker.pitchX = 50.8
			marker.pitchY = 16.8095
			marker.filter = 'HIGH_PASS'
			marker.scaleMin = 0.30
			marker.scaleMax = 0.70
			marker.scaleWarning = 0.02
			marker.scaleRatio   = 1.01
		case 'S550':
			marker.image = cv2.imread(currentPath+'Marker_S550.bmp')
			marker.pitchX = 8.0
			marker.pitchY = 25.375
			marker.filter = 'HIGH_PASS'
			marker.scaleMin = 0.40
			marker.scaleMax = 0.55
			marker.scaleWarning = 0.01
			marker.scaleRatio   = 1.39
		case 'REF':
			marker.image = cv2.imread(currentPath+'SQ.png')
			marker.pitchX = 7.0
			marker.pitchY = 7.0
			marker.filter = 'NONE'
			marker.scaleMin = 0.5
			marker.scaleMax = 1.1
			marker.scaleWarning = 0.02
			marker.scaleRatio   = 1.8
		case _:
			marker.image = cv2.imread(currentPath+'X.bmp')
			marker.pitchX = 7.0 
			marker.pitchY = 7.0
			marker.filter = 'NONE'
			marker.scaleMin = 0.5
			marker.scaleMax = 1.5
			marker.scaleWarning = 0.1
			marker.scaleRatio   = 1.5
	
	# set the marker parameters
	marker.width  = marker.image.shape[1]
	marker.height = marker.image.shape[0]

def getCamFrame():
	frame = cam.vid.read()
	return frame

def release():
	cam.vid.release()

def removeGlare(image,level):
	#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	mask = cv2.threshold(image, level, 255, cv2.THRESH_BINARY)[1]
	#cv2.imshow('Mask',mask)
	# use mask with input to do inpainting
	image = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA) 
	#cv2.imshow('RemoveGlare',image)
	return image

def hisEqulColor(image):
	ycrcb=cv2.cvtColor(image,cv2.COLOR_BGR2YCR_CB)
	channels=cv2.split(ycrcb)
	#print(len(channels))
	cv2.equalizeHist(channels[0],channels[0])
	cv2.merge(channels,ycrcb)
	cv2.cvtColor(ycrcb,cv2.COLOR_YCR_CB2BGR,image)
	return image

def prepImageOrg(image, scale, filter, ID):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	match filter:
		case 'LOW_PASS':
			image = cv2.filter2D(image,-1,kernelLowPass)
			if debugShow:
				cv2.imshow('lowPass' + ID,image)
		case 'HIGH_PASS':
			
			# remove the DC component
			image = cv2.GaussianBlur(image, (21, 21), 0) - image + 127
			
			#image = removeGlare(image,200)
			
			# high pass filter
			image = cv2.filter2D(image,-1,kernelHighPass)
			# smooth the results
			image = cv2.blur(image,(3,3),0)
			#image = cv2.normalize(image, image, 0, 255,cv2.NORM_MINMAX)
			
			if debugShow:
				cv2.imshow('highPass' + ID,image)
		case 'NONE':
			pass
		case _:
			pass
	if scale != 1.0:
		image = cv2.resize(image, (round(image.shape[1] * scale),round(image.shape[0] * scale)), interpolation = cv2.INTER_AREA)
	image = cv2.blur(image,(3,3),0)
	return image
	
def prepImage(image, scale, filter, ID):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	if scale != 1.0:
		image = cv2.resize(image, (round(image.shape[1] * scale),round(image.shape[0] * scale)), interpolation = cv2.INTER_AREA)
	#else:
	#	#removeGlare(image,200)
	#image = cv2.equalizeHist(image)
	#
	
	
	
	
	match filter:
		case 'LOW_PASS':
			image = cv2.filter2D(image,-1,kernelLowPass)
			image = cv2.GaussianBlur(image,(11,11),0)
			if debugShow:
				cv2.imshow('lowPass' + ID,image)
		case 'HIGH_PASS':
			
			# remove the DC component
			#image = cv2.GaussianBlur(image, (21, 21), 0) - image + 127
			image = cv2.blur(image, (11, 11), 0) - image + 127
			#image = image - cv2.GaussianBlur(image, (21, 21), 0) + 127
			
			image = cv2.GaussianBlur(image,(5,5),0)
			#image = removeGlare(image,200)
			# high pass filtercc
			image = cv2.filter2D(image,-1,kernelHighPass)
			# smooth the results
			
			image = cv2.bilateralFilter(image,9,75,75)
			
			#image = cv2.normalize(image, image, 0, 255,cv2.NORM_MINMAX)
			
			if debugShow:
				cv2.imshow('highPass' + ID,image)
		case 'NONE':
			pass
		case _:
			pass
	
	
	return image
	
def matchTemplate(frame, marker):
	result = cv2.matchTemplate(frame,marker,Method)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
	return min_val, max_val, min_loc, max_loc, result

def findMarkers(frame):
	global markerScale
	global debugPlot
	global status
	
	MarkerStepS = 0.002 * cam.scale
	MarkerStepM = 0.008 * cam.scale
	MarkerStepL = 0.05 * cam.scale
	MarkerScaleMin = marker.scaleMin * cam.scale
	MarkerScaleMax = marker.scaleMax * cam.scale
	
	# prepare the frame
	
	
	
	frame_gray = prepImage(frame,1, marker.filter, 'MAIN')
	
	frame_mask = copy.copy(frame_gray)
	cv2.rectangle(frame_mask,(0,0), (frame_mask.shape[1],frame_mask.shape[0]), 0, -1)
	
	
	# course marker search
	delta = estimateFocus(frame)
	focusEst = delta / (marker.image.shape[1] / marker.scaleRatio)
	# make a proportional update towards the expected required focus
	if focusEst != 0:
		markerScale -= (markerScale - focusEst) / 4.0
	
	# find the best matching marker scale
	# update the "focus" by resizing the marker, attempting to get the best matching size
	marker2 = prepImage(marker.image,markerScale - MarkerStepM, marker.filter, 'Marker-')
	min_valM, max_valM, min_loc, max_loc, result = matchTemplate(frame_gray, marker2)
	
	marker2 = prepImage(marker.image, markerScale + MarkerStepM * cam.scale, marker.filter, 'Marker+')
	min_valP, max_valP, min_loc, max_loc, result = matchTemplate(frame_gray, marker2)
	
	marker2 = prepImage(marker.image, markerScale, marker.filter, 'Marker')
	min_val, max_val, min_loc, max_loc, result = matchTemplate(frame_gray, marker2)
	corr = max_val
	
	if max_val < 0.45: # the correlation is too low, update the marker scale, this avoids getting locked in a max or min value
		markerScale += MarkerStepS * markerSearchDir
		status = 'SEARCHING'
		if focusEst != 0:
			markerScale = focusEst
		
	else:
		markerSearchCounter = 0
		status = 'OK'
		if max_val < max(max_valP, max_valM): # if needed update the marker scale to match the best zoom
			if max_valP > max_valM:
				markerScale += MarkerStepS
			else:
				markerScale -= MarkerStepS
				
	if markerScale >= MarkerScaleMax - marker.scaleWarning:
		status = 'TOO_FAR'
		
	if markerScale >= MarkerScaleMax:
		markerScale = MarkerScaleMax
		
	if markerScale <= MarkerScaleMin + marker.scaleWarning:
		status = 'TOO_CLOSE'
		
	if markerScale <= MarkerScaleMin:
		markerScale = MarkerScaleMin
		
	result_org = copy.copy(result)
	
	# process the data
	# loop through the matched image until the highest result is below the threshold
	# this is done by finding the highest threshold and then covering that area with
	# a black image to allow finding the next best match
	dataPoints = []
	while (max_val >= threshold) and (len(dataPoints) < 265): # limit the markers to the best 256 points to ensure reasonable performance
		# add the found point to the list of points
		if  (max_loc[0] > 0) and (max_loc[0] < result.shape[1]) and\
			(max_loc[1] > 0) and (max_loc[1] < result.shape[0]):
			dataPoints.append((max_loc[0] + (round(marker.width * markerScale)//2), max_loc[1] + (round(marker.height * markerScale)//2)))
		# black out the area where the point was found to allow finding the next best 
		cv2.rectangle(result,(max_loc[0] - (round(marker.width * markerScale)//2), max_loc[1] - (round(marker.height* markerScale)//2)), (max_loc[0] + (round(marker.width * markerScale)//2), max_loc[1] + (round(marker.height * markerScale)//2)), 0, -1)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
	
	if debugShow:
		debugstr = 'scale : {:.2f} Correlation: {:.2f}'
		cv2.putText(result, debugstr.format(markerScale,corr), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
		cv2.imshow('result', result)
		cv2.imshow('result_org',result_org)
		cv2.imshow('marker2',marker2)
		cv2.imshow('frameGray',frame_gray)
	
	markerScale2 = markerScale / cam.scale
	
	return corr, markerScale2, dataPoints, status

def estimateFocus(image):
	global marker
	threshold = 0.7
	blockRange = 10
	dataPoints = []
	val0 = 0
	val1 = 0
	delta = 0
	
	h = 31
	w = image.shape[1] // 3
	x = (image.shape[1] - w) // 2
	y = (image.shape[0] - h) // 2
	image  = image[y:y+h, 0:image.shape[1]]
	#image  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image = prepImage(image,1,marker.filter,'EF')
	
	image  = cv2.blur(image,(1,91),0)
	marker2 = image[0:image.shape[0] // 2, x:x+w]
	
	result = cv2.matchTemplate(image,marker2,Method)
	if debugShow:
		cv2.imshow('estimateFocusBlurResult1',result)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
	while (max_val >= threshold) and (len(dataPoints) < 265): # limit the markers to the best 256 points to ensure reasonable performance
		# add the found point to the list of points
		if  (max_loc[0] > 0) and (max_loc[0] < result.shape[1]):
			if len(dataPoints) > 0:
				if max_loc[0] > dataPoints[0]:
					dataPoints.append(max_loc[0])
			else:
				dataPoints.append(max_loc[0])
		# black out the area where the point was found to allow finding the next best 
		cv2.rectangle(result,(max_loc[0] - blockRange, 0), (max_loc[0] + blockRange, result.shape[0]), 0, -1)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
	delta = 0
	if len(dataPoints) >= 1:
		val0 = dataPoints[0]
		dataPoints.pop(0)
		if len(dataPoints) >= 1:
			val1 = min(dataPoints)
			delta = val1- val0
			if delta <= blockRange + 1:
				delta = 0
	
	if debugShow:
		cv2.imshow('estimateFocusBlurImage', image)
		cv2.imshow('estimateFocusBlurMarker',marker2)
		cv2.imshow('estimateFocusBlurResult',result)
		print(val0, val1, delta, dataPoints)
	return delta
#
#
#
#
#









#

