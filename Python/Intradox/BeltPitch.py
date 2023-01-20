import platform
import math
import cv2
import sys
import numpy             as np
import ToolsCAD          as cad
import ToolsImageProcess as cam
import ToolsDataProcess  as dat
from timeit     import default_timer as timer
from PIL        import Image, ImageFont, ImageDraw
from statistics import mean
from statistics import pstdev
from statistics import median



Camera    = 'acttoL'
#Camera    = 'acttoM'
#Camera    = 'acttoS'
#Camera    = 'DELLL'
#Camera    = 'DELLM'
#Camera    = 'DELLS'
#Camera    = 'LogitecL'
Marker    = 'REF'
#Marker    = 'DARB_L'
#Marker    = 'S7050'
#Marker    = 'S800AIM'

DebugShow = True
DebugShow = False
UseCam    = True
ThresholdMinMaxRatio = 0.5
MarkerPosError       = 0.08
AngleRangeRz         = 8.0
AngleRangeRxy        = 5.0

if platform.system() == 'Darwin': # iPhone
	Camera = 'iPhone'
	DebugShow = False
	import motion
	import speech
	import resource
	motion.start_updating()
else:
	import os
	import psutil


print('Script: ',sys.argv[0])
if len(sys.argv) > 1:
	Marker = str(sys.argv[1])
	print ('Arg: ' + Marker)

cam.initCamera(Camera)
cam.initMarker(Marker)
cam.debugShow = DebugShow
dat.ThresholdPointError = MarkerPosError
#cam.threshold = Threshold

# correct for the wrong image format in the iPhone
if platform.system() == 'Darwin': # iPhone
	temp = cam.cam.width
	cam.cam.width = cam.cam.height
	cam.cam.height = temp
	
print('Vid: [' , cam.cam.width, ' , ', cam.cam.height, ']')
print(platform.system())
print(platform.machine())
#print(platform.platform(0, 0))

# set text parameters
# font
font = cv2.FONT_HERSHEY_SIMPLEX

fontSmall      = 0.5
fontMedium     = 0.8
fontLarge      = 2.0

# color of the debug text
color       = (255, 224, 224)
borderColor = (  0,   0,   0)
# set the thickness of the font
thickness = 1

# debug text line coordinates
org00 = (130, 375)
org   = ( 20, 430)
org0  = (130, 460)
org1  = ( 20,  35)
org2  = ( 20,  55)
org3  = ( 20,  75)
org4  = ( 20,  95)
org5  = ( 20, 115)
org6  = ( 20, 125)

CP = cad.Point()

Elong = 0.0
ElongAvg = []

PAB = cad.Point()
PBC = cad.Point()
PAD = cad.Point()
PDC = cad.Point()

def imagePrint(captionStr,p,color, borderColor,size,width):
	cv2.putText(frame, captionStr, (p[0]-1,p[1]-1), font, size, borderColor, width, cv2.LINE_AA)
	cv2.putText(frame, captionStr, (p[0]+1,p[1]-1), font, size, borderColor, width, cv2.LINE_AA)
	cv2.putText(frame, captionStr, (p[0]+1,p[1]+1), font, size, borderColor, width, cv2.LINE_AA)
	cv2.putText(frame, captionStr, (p[0]-1,p[1]+1), font, size, borderColor, width, cv2.LINE_AA)
	cv2.putText(frame, captionStr, p, font, size, color, width, cv2.LINE_AA)

def imageCircle(P1, color):
	cv2.circle(frame,(round(P1.x),round(P1.y)), 6, (0,0,0), 1)
	cv2.circle(frame,(round(P1.x),round(P1.y)), 5, (255,255,255), 1)
	cv2.circle(frame,(round(P1.x),round(P1.y)), 4, color, -1)
	
def imageLine(P1,P2, color):
	cv2.line(frame,(round(P1.x),round(P1.y)),(round(P2.x),round(P2.y)),(  0,  0,  0),4)
	cv2.line(frame,(round(P1.x),round(P1.y)),(round(P2.x),round(P2.y)),(255,255,255),3)
	cv2.line(frame,(round(P1.x),round(P1.y)),(round(P2.x),round(P2.y)), color,       2)

		
modeToggle = 1
Time_start = timer()
focusCounter = 100
ToggleTimer = timer()
ToggleTimer = timer()
Toggle = False

while(cam.cam.vid.isOpened()):
	CP.x = cam.cam.width  //2
	CP.y = cam.cam.height //2
	# check the keys for human interaction
	if platform.system() == 'Darwin': #check for iOS, OpenCV for iOS has no function for cv2.waitKey()
		acc = motion.get_acceleration()
		if abs(acc[0]) > 0.75:
			if timer() - ToggleTimer > 1.0:
				ToggleTimer = timer()
				Toggle = True
	else:
		key = cv2.waitKey(1)
		if key == ord('q') or key ==ord('Q') or key ==27:
			break
		if key == ord('1'):
			cam.marker.scaleRatio -= 0.01
			if cam.marker.scaleRatio < 0.1:
				cam.marker.scaleRatio = 0.1
		if key == ord('2'):
			cam.marker.scaleRatio += 0.01
			if cam.marker.scaleRatio > 8.0:
				cam.marker.scaleRatio = 8.0
		if key == ord('c'):
			UseCam = not UseCam
		if key == ord('x'):
			cam.cam.magicN += 5
			print(cam.cam.magicN)
		if key == ord('z'):
			cam.cam.magicN -= 5
			print(cam.cam.magicN)
		if key == ord('f'):
			if cam.marker.filter == 'HIGH_PASS':
				cam.marker.filter = 'LOW_PASS'
			else:
				cam.marker.filter = 'HIGH_PASS'
		if key == ord('/'):
			Toggle = True
		if key == ord('d') or key == ord('D'):
			DebugShow = not DebugShow
			cam.debugShow = DebugShow
			if not DebugShow:
				cv2.destroyAllWindows()
	if Toggle:
		Toggle = False
		modeToggle += 1
		if modeToggle >= 9:
			modeToggle = 0
		match modeToggle:
			case 0:
				Marker    = 'REF'
			case 1: 
				Marker    = 'DARB_L'
			case 2:
				Marker    = 'DARB_R'
			case 3:
				Marker    = 'S7000'
			case 4:
				Marker    = 'S7050'
			case 5:
				Marker    = 'S400ARB'
			case 6:
				Marker    = 'S800AIM'
			case 7:
				Marker    = 'S800AIM_Sorter'
			case 8:
				Marker    = 'S550'
		cam.initMarker(Marker)
		if platform.system() == 'Darwin':
			speech.say(Marker)
	
	if DebugShow:
		debugFrame  = np.zeros((cam.cam.height,cam.cam.width,3), np.uint8)
		debugFrame2 = np.zeros((cam.cam.height,cam.cam.width,3), np.uint8)
		debugFrame3 = np.zeros((cam.cam.height,cam.cam.width,3), np.uint8)
	
	# grab the frame data
	if UseCam:
		ret, frame = cam.getCamFrame()
		if not ret:
			print('Failed to receive frame, exiting...')
			#continue
			break
	else:
		frame = cv2.imread('Test.bmp')
		print(cam.marker.scaleRatio)
	
	if platform.system() != 'Darwnin': # when on the PC crop the image to match the iPhone size
		h = 480
		w = 360
		x = (frame.shape[1] - w) // 2
		y = (frame.shape[0] - h) // 2
		
		frame = frame[y:y+h, x:x+w]
		cam.cam.height = frame.shape[0]
		cam.cam.width  = frame.shape[1]
	
	# resize the frame to maximize the space on the iPhone screen
	frame = cv2.resize(frame, (round(frame.shape[1] * 1.15),round(frame.shape[0] * 1.15)), interpolation = cv2.INTER_AREA)
	cam.cam.height = frame.shape[0]
	cam.cam.width  = frame.shape[1]
	
	#frame = hisEqulColor(frame)

	
	
	#delta = cam.estimateFocus(frame)
	#focusEst = delta / (cam.marker.image.shape[1] / 1.5)
	#print(focusEst)
	
	# find the markers in the frame
	markerCorrelation = 0.0
	markerScale       = 0.0
	datapoints = []
	dataRange  = []
	markerCorrelation, markerScale, dataPoints, status = cam.findMarkers(frame)
	# find the 4 corner markers of the data field
	PLT,PLB,PRB,PRT, dataRange = dat.findCorners(dataPoints,CP)
	# refine the found points by realigning them to the all the points found on the sides of the corresponding box
	PA,PB,PC,PD, coll, row, dataRangeEdge = dat.refineCorners(dataPoints,PLT,PLB,PRB,PRT)
	
	# set the threshold for marker detection
	cam.threshold = markerCorrelation * ThresholdMinMaxRatio
	
	if DebugShow:
		imageLine(PA,PB, (0,0,255))
		imageLine(PB,PC, (0,0,255))
		imageLine(PC,PD, (0,0,255))
		imageLine(PD,PA, (0,0,255))
		imageLine(PA,PC, (0,0,255))
		imageLine(PB,PD, (0,0,255))
	
	# Create the aiming cross on the image
	cv2.line(frame,(cam.cam.width//2,0),(cam.cam.width//2,cam.cam.height),(255,255,255),1)
	cv2.line(frame,(0,cam.cam.height//2),(cam.cam.width,cam.cam.height//2),(255,255,255),1)
	
	# place the found markers in the image
	countPoints   = 0
	countPointsOK = 0
	for pt in dataPoints:
		p = cad.Point()
		p.x = pt[0]
		p.y = pt[1]
		imageCircle(p,(0,0,196))
		countPoints += 1
		if DebugShow:
			cv2.circle(debugFrame,pt, 5, (0,0,255), 1)
			cv2.putText(debugFrame,str(countPoints),pt,font,fontSmall / 2,(255,255,255),thickness,cv2.LINE_AA)
	
	# place the good markers in the image
	countPoints = 0
	for pt in dataRange:
		p = cad.Point()
		p.x = pt[0]
		p.y = pt[1]
		imageCircle(p,(0,128,128))
		countPointsOK += 1
		if DebugShow:
			countPoints += 1
			cv2.circle(debugFrame2,pt, 5, (0,255,255), 1)
			cv2.putText(debugFrame2,str(countPoints),pt,font,fontSmall / 2,(255,255,255),thickness,cv2.LINE_AA)
	
	# place the edge markers in the image
	countPoints = 0
	for pt in dataRangeEdge:
		p = cad.Point()
		p.x = pt[0]
		p.y = pt[1]
		imageCircle(p,(0,128,0))
		if DebugShow:
			countPoints += 1
			cv2.circle(debugFrame3,pt, 5, (0,0,255), 1)
			cv2.putText(debugFrame3,str(countPoints),pt,font,fontSmall / 2,(255,255,255),thickness,cv2.LINE_AA)
	
	# place the found corner markers in the image
	imageCircle(PLT,(0,255,255))
	imageCircle(PLB,(0,255,255))
	imageCircle(PRB,(0,255,255))
	imageCircle(PRT,(0,255,255))
	
	if DebugShow:
		cv2.line(debugFrame,(round(PLT.x),round(PLT.y)),(round(PLB.x),round(PLB.y)),(255,0,0),1)
		cv2.line(debugFrame,(round(PLB.x),round(PLB.y)),(round(PRB.x),round(PRB.y)),(255,0,0),1)
		
		cv2.line(debugFrame,(round(PRB.x),round(PRB.y)),(round(PRT.x),round(PRT.y)),(255,0,0),1)
		cv2.line(debugFrame,(round(PRT.x),round(PRT.y)),(round(PLT.x),round(PLT.y)),(255,0,0),1)
		
		cv2.circle(debugFrame,(round(PLT.x),round(PLT.y)), 6, (0,255,255), 2)
		cv2.circle(debugFrame,(round(PRB.x),round(PRB.y)), 6, (0,255,255), 2)
		cv2.circle(debugFrame,(round(PLB.x),round(PLB.y)), 6, (0,255,255), 2)
		cv2.circle(debugFrame,(round(PRT.x),round(PRT.y)), 6, (0,255,255), 2)
	
	# process the data and calculate the stretch
	Rx = 0.0
	Ry = 0.0
	Rz = 0.0
	if (coll >= 3) and (row >= 3): # make sure at least 9 points are detected in a min 3x3 square 
		if PA.x * PA.y * PB.x * PB.y * PC.x * PC.y * PD.x * PD.y != 0:
			# center the found coordinates around the center of the lens, this significantly improves the accuracy
			PA,PB,PC,PD,PAB,PBC,PAD,PDC = cad.centerImage(PA, PB, PC, PD, CP)
			if DebugShow:
				cv2.line(frame,(round(PA.x),round(PA.y)),(round(PB.x),round(PB.y)),(0,255,255),2)
				cv2.line(frame,(round(PB.x),round(PB.y)),(round(PC.x),round(PC.y)),(0,255,255),2)
				cv2.line(frame,(round(PC.x),round(PC.y)),(round(PD.x),round(PD.y)),(0,255,255),2)
				cv2.line(frame,(round(PD.x),round(PD.y)),(round(PA.x),round(PA.y)),(0,255,255),2)
				cv2.line(frame,(round(PA.x),round(PA.y)),(round(PC.x),round(PC.y)),(0,255,255),2)
				cv2.line(frame,(round(PB.x),round(PB.y)),(round(PD.x),round(PD.y)),(0,255,255),2)
				
				cv2.line(frame,(round(PAB.x),round(PAB.y)),(round(PDC.x),round(PDC.y)),(0,255,255),2)
				cv2.line(frame,(round(PBC.x),round(PBC.y)),(round(PAD.x),round(PAD.y)),(0,255,255),2)
			
			if (PA.x * PA.y * PB.x * PB.y * PC.x * PC.y * PD.x * PD.y) != 0: # make sure all corners are valid
				# Calculate the elongation 
				Elong, Rx, Ry, Rz = cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , cam.cam.magicN, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)
				
				if DebugShow:
					E200 = round(cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , 200, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)[0] * 10)/10 
					E400 = round(cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , 400, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)[0] * 10)/10 
					E600 = round(cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , 600, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)[0] * 10)/10 
					E800 = round(cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , 800, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)[0] * 10)/10 
					E1000 = round(cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , 1000, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)[0] * 10)/10 
					E1200 = round(cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , 1200, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)[0] * 10)/10 
					E1400 = round(cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , 1400, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)[0] * 10)/10 
					E1600 = round(cad.getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC , 1600, CP, coll,row, cam.marker.pitchX, cam.marker.pitchY)[0] * 10)/10 
					print(cam.cam.magicN, ' | ' , E200 ,',',E400 ,',',E600 ,',',E800 ,',',E1000 ,',',E1200 ,',',E1400,',',E1600)
	
	DebugTime = timer()
	Time_end  = timer() # get the frame timer
	
	# create visual aids to help aiming the camera
	focusCounter += 10
	focusRange = min(cam.cam.width, cam.cam.height) // 4
	if focusCounter > focusRange:
		focusCounter = 0
	match status:
		case 'OK':
			if (abs(math.degrees(Rx)) > AngleRangeRxy) or (abs(math.degrees(Ry)) > AngleRangeRxy) or (abs(math.degrees(Rz)) > AngleRangeRz):
				cv2.rectangle(frame, (10,10), (cam.cam.width - 10, cam.cam.height -10),(0,0,0), 12)
			else:
				cv2.rectangle(frame, (10,10), (cam.cam.width - 10, cam.cam.height -10),(96,196,96), 2)
		case 'TOO_FAR':
			box1 = ((CP.x               ,CP.y),                ((focusRange * 2) + focusCounter, (focusRange * 2) + focusCounter),         0 )
			boxP1 = cv2.boxPoints(box1)
			boxP1 = np.int0(boxP1)
			frame = cv2.drawContours(frame,[boxP1],0,(0,0,196),6)
		case 'TOO_CLOSE':
			box1 = ((CP.x               ,CP.y),                ((focusRange * 3) - focusCounter, (focusRange * 3) - focusCounter),         0 )
			boxP1 = cv2.boxPoints(box1)
			boxP1 = np.int0(boxP1)
			frame = cv2.drawContours(frame,[boxP1],0,(0,0,196),6)
		case 'SEARCHING':
			box1 = []
			if focusCounter > focusRange // 2:
				box1 = ((CP.x               ,CP.y),                ((focusRange * 3), (focusRange * 3)),         0 )
			else:
				box1 = ((CP.x               ,CP.y),                ((focusRange * 2), (focusRange * 2)),         0 )
			boxP1 = cv2.boxPoints(box1)
			boxP1 = np.int0(boxP1)
			frame = cv2.drawContours(frame,[boxP1],0,(32,224,224),6)
		case _:
			pass #do nothing
	
	# create the leveler view
	box1   = ((CP.x                          ,CP.y),                         ((focusRange * 2) -  8, (focusRange * 2) -  8), 0)
	box11  = ((CP.x                          ,CP.y),                         ((focusRange * 2) + 24, (focusRange * 2) + 24), 0)
	box2   = ((CP.x - (math.degrees(Ry) * 8 ),CP.y - (math.degrees(Rx) * 8)), (focusRange * 2, focusRange * 2),              math.degrees(Rz) * 2)
	boxP1  = cv2.boxPoints(box1)
	boxP11 = cv2.boxPoints(box11)
	boxP2  = cv2.boxPoints(box2)
	boxP1  = np.int0(boxP1)
	boxP11 = np.int0(boxP11)
	boxP2  = np.int0(boxP2)
	
	if status != 'SEARCHING':
		if (abs(math.degrees(Rx)) > AngleRangeRxy) or (abs(math.degrees(Ry)) > AngleRangeRxy) or (abs(math.degrees(Rz)) > AngleRangeRz):
			frame = cv2.drawContours(frame,[boxP1], 0,(0,0,0),5)
			frame = cv2.drawContours(frame,[boxP11],0,(0,0,0),5)
			frame = cv2.drawContours(frame,[boxP2], 0,(255,255,255),5)
			
			frame = cv2.drawContours(frame,[boxP1], 0,(255,255,255),3)
			frame = cv2.drawContours(frame,[boxP11],0,(255,255,255),3)
			frame = cv2.drawContours(frame,[boxP2], 0,(0,0,196),3)
		else:
			rame = cv2.drawContours(frame,[boxP1],  0,(0,0,0),3)
			frame = cv2.drawContours(frame,[boxP11],0,(0,0,0),3)
			
			frame = cv2.drawContours(frame,[boxP1],0,(255,255,255),1)
			frame = cv2.drawContours(frame,[boxP11],0,(255,255,255),1)
			if coll >= 3 and row >= 3:
				frame = cv2.drawContours(frame,[boxP2],0,(0,0,0),4)
				frame = cv2.drawContours(frame,[boxP2],0,(0,196,0),2)
			else:
				frame = cv2.drawContours(frame,[boxP2],0,(255,255,255),6)
				frame = cv2.drawContours(frame,[boxP2],0,(0,0,0),4)
	
	frameStr1 = ' {:>6.2f}[%] {:>6.2f}[%] {:>6.1f}[%] {:>4}[pix]'
	frameStr2 = ' {:>3}[ms] {:>4.1f}[fps]'
	frameStr3 = ' {:>3}[n] of {:3}[n]'
	frameStr4 = '[{:>5.1f} {:>5.1f} {:>5.1f}][deg]'
	frameStr5 = '  ' + Marker
	
	imagePrint(frameStr1.format(cam.threshold,markerCorrelation,markerScale*100.0,cam.cam.magicN),org1,color,borderColor,fontSmall,thickness)
	imagePrint(frameStr2.format(round((Time_end - Time_start) * 1000),1 / (Time_end - Time_start)),org2,color,borderColor,fontSmall,thickness)
	imagePrint(frameStr3.format(countPointsOK, countPoints),org3,color,borderColor,fontSmall,thickness)
	if (abs(math.degrees(Rx)) < AngleRangeRxy) and (abs(math.degrees(Ry)) < AngleRangeRxy) and (abs(math.degrees(Rz)) < AngleRangeRz):
		imagePrint(frameStr4.format(math.degrees(Rx),math.degrees(Ry),math.degrees(Rz)),org4,color,borderColor,fontSmall,thickness)
	else:
		imagePrint(frameStr4.format(math.degrees(Rx),math.degrees(Ry),math.degrees(Rz)),org4,(0,0,255),(255,255,255),fontSmall,thickness)
	imagePrint(frameStr5,org5,color,borderColor,fontSmall,thickness)
	
	if DebugShow:
		memUse = 0
		if platform.system() == 'Darwin':
			memUse = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
			#print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
		else:
			process = psutil.Process(os.getpid())
			#print(process.memory_info().rss)
			memUse = process.memory_info().rss
		# print the various diag data on the screen
		frameStr6 = ' {:>12}'
		imagePrint(frameStr6.format(memUse),org6,color,borderColor,fontSmall,thickness)
	
	# print the result
	textW = 2
	if (coll >= 3) and (row >= 3):
		if abs(Elong) < 10.0: # ignore too extreme values
			ElongAvg.append(Elong)
			while len(ElongAvg) > 40:
				ElongAvg.pop(0)
			Elong = mean(ElongAvg)
			stdv  = pstdev(ElongAvg)
			stdv  = stdv * 2 # raise confidence from 67 to 95%
			
			frameStr = '{:6.2f}%'
			stdv = max(stdv, 0.02) # set a minimum error to allow for unknown system errors
			if stdv < 0.20:
				imagePrint(frameStr.format(Elong + stdv),org00,(0,224,0),(0,0,0),fontMedium,2)
				imagePrint(frameStr.format(Elong - stdv),org0, (0,224,0),(0,0,0),fontMedium,2)
				textW = 8
			elif stdv < 0.5:
				imagePrint(frameStr.format(Elong + stdv),org00,(0,224,244),(0,0,0),fontMedium,2)
				imagePrint(frameStr.format(Elong - stdv),org0, (0,224,244),(0,0,0),fontMedium,2)
				textW = 5
			elif stdv < 1.2:
				imagePrint(frameStr.format(Elong + stdv),org00,(0,0,244),(255,255,255),fontMedium,1)
				imagePrint(frameStr.format(Elong - stdv),org0, (0,0,244),(255,255,255),fontMedium,1)
				textW = 3
			elif stdv >= 1.2:
				imagePrint(frameStr.format(Elong + stdv),org00,(0,0,0),(255,255,255),fontMedium,1)
				imagePrint(frameStr.format(Elong - stdv),org0, (0,0,0),(255,255,255),fontMedium,1)
				textW = 2
			
			if (Elong <= -0.5):
				imagePrint(frameStr.format(Elong),org,color,borderColor,fontLarge,textW)
			if (Elong > -0.5) and (Elong <= 2.0):
				imagePrint(frameStr.format(Elong),org,(0,224,0),(0,0,0),fontLarge,textW)
			if (Elong > 2.0) and (Elong <= 3.0):
				imagePrint(frameStr.format(Elong),org,(0,255,255),(0,0,0),fontLarge,textW)
			if (Elong > 3.0) and (Elong <= 4.5):
				imagePrint(frameStr.format(Elong),org,(0,0,255),(255,255,255),fontLarge,textW)
			if (Elong > 4.5):
				imagePrint(frameStr.format(Elong),org,(0,0,0),(255,255,255),fontLarge,textW)
				
	else:
		imagePrint('  -.--%',org,(0,0,0),(255,255,255),fontLarge,textW)
	
	Time_start = Time_end # store the frame timer for next loop
	
	# Display the resulting frame
	if DebugShow:
		cv2.imshow('debugFrame',debugFrame)
		cv2.imshow('debugFrame2',debugFrame2)
		cv2.imshow('debugFrame3',debugFrame3)
	
	if platform.system() == 'Darwin': # iPhone uses a different color format that needs to be corrected for
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	
	
	cv2.imshow('frame', frame)
	#print((timer() - DebugTime) * 1000)
	


# After the loop release the cap object
cam.release()
# Destroy all the windows
if platform.system() != 'Darwin':
	cv2.destroyAllWindows()





#
#
#
#
#
